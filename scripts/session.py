"""Local-only questionnaire transport. Python 3.10+, standard library only."""
import sys

if __name__ == "__main__" and sys.argv[1:] in (["--version"], ["-v"], ["-V"]):
    print("1.0.0")
    raise SystemExit(0)

import argparse
import os
from pathlib import Path
import re
import secrets
import tempfile
import threading
import time
import webbrowser
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


def quote(value):
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return '"' + ''.join(escapes.get(c, f"\\u{ord(c):04x}" if ord(c) < 32 else c)
                         for c in str(value)) + '"'


def report(**fields):
    print('\n'.join(f"{key}: {quote(value)}" for key, value in fields.items()), flush=True)


class Questions(HTMLParser):
    """Read the generated form's small, explicit contract, not arbitrary HTML inputs."""
    def __init__(self, html):
        super().__init__()
        self.questions = {}
        self.hooks = {}
        self.current = None
        self.feed(html)
        if not self.questions or self.current is not None:
            raise ValueError("Round needs complete fieldsets with data-question IDs")
        if any(not {"custom", "discuss"} <= choices for choices in self.questions.values()):
            raise ValueError("Each question needs custom and discuss radio choices")
        if any(not {'data-custom', 'data-text', 'data-context', 'data-error', 'data-clear'} <= hooks
               for hooks in self.hooks.values()):
            raise ValueError("Each question needs custom, text, context, error, and clear hooks; use the template")

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "fieldset":
            identifier = data.get("data-question", "")
            if self.current or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", identifier):
                raise ValueError("Use flat fieldsets with stable lowercase question IDs")
            if identifier in self.questions:
                raise ValueError("Duplicate question ID")
            self.current = identifier
            self.questions[identifier] = set()
            self.hooks[identifier] = set()
        if self.current:
            self.hooks[self.current].update(data)
        if tag == "input" and data.get("type") == "radio":
            value = data.get("value", "")
            if not self.current or data.get("name") != self.current:
                raise ValueError("Radio names must match their question ID")
            if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value):
                raise ValueError("Use lowercase option IDs")
            if value in self.questions[self.current] or "checked" in data:
                raise ValueError("Duplicate or preselected option")
            self.questions[self.current].add(value)

    def handle_endtag(self, tag):
        if tag == "fieldset":
            self.current = None


def packet(session, number, questions, fields):
    allowed = {f"{identifier}.{suffix}" for identifier in questions
               for suffix in ("choice", "text", "context")}
    if fields.keys() - allowed or any(len(values) != 1 for values in fields.values()):
        raise ValueError("Unknown or duplicate answer fields")
    rows = []
    for identifier, choices in questions.items():
        choice = fields.get(f"{identifier}.choice", [""])[0]
        custom = fields.get(f"{identifier}.text", [""])[0]
        context = fields.get(f"{identifier}.context", [""])[0]
        if choice not in choices:
            raise ValueError(f"Choose an answer for {identifier}")
        if choice == "custom" and not custom.strip():
            raise ValueError(f"Write your answer for {identifier}")
        text = custom if choice == "custom" else ""
        if context:
            text += ("\n\n" if text else "") + context
        rows.append("  " + ",".join((quote(identifier),
                    quote("" if choice in {"custom", "discuss"} else choice),
                    quote(text), "true" if choice == "discuss" else "false")))
    return (f"session: {quote(session)}\nround: {number}\nstatus: submitted\n"
            f"answers[{len(rows)}]{{id,choice,text,deferred}}:\n" + "\n".join(rows))


def save_once(path, text):
    """Publish a complete file atomically without replacing an existing snapshot."""
    expected = text.encode("utf-8")
    if path.is_symlink():
        raise ValueError("Answer path must not be a symbolic link")
    descriptor, temporary = tempfile.mkstemp(prefix=".answer-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(expected)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != expected:
                raise ValueError("This round was already submitted; revise in a new round")
        if path.read_bytes() != expected:
            raise OSError("Answer verification failed")
    finally:
        os.unlink(temporary)


CLIENT = r'''
(() => {
  const form = document.querySelector('#grill-form');
  const status = document.querySelector('#session-status');
  if (!form || !status) return;
  const base = new URL('.', location.href);
  const round = Number(location.pathname.match(/round-(\d+)\.html$/)[1]);
  const groups = [...form.querySelectorAll('fieldset[data-question]')];
  const submit = form.querySelector('[type=submit]');
  const key = `grill:${location.pathname}:`;
  let busy = false, saved = false, storageWorks = true, pending = null, submissionError = '';
  const say = text => { if (status.textContent !== text) status.textContent = text; };
  const storage = (operation, name, value) => {
    try { return localStorage[operation](key + name, value); }
    catch { storageWorks = false; return null; }
  };
  const controls = [...form.querySelectorAll('input,textarea')];
  for (const control of controls) {
    const stored = storage('getItem', control.id);
    if (stored !== null) {
      if (control.type === 'radio') control.checked = stored === 'true';
      else control.value = stored;
    }
  }
  function refresh() {
    let answered = 0;
    for (const group of groups) {
      const selected = group.querySelector('input:checked');
      const custom = group.querySelector('[data-custom]');
      custom.hidden = selected?.value !== 'custom';
      if (selected && (selected.value !== 'custom' || group.querySelector('[data-text]').value.trim())) answered++;
    }
    const progress = document.querySelector('#answer-progress');
    if (progress) progress.textContent = `${answered} of ${groups.length} answered`;
  }
  form.addEventListener('input', () => {
    submissionError = '';
    for (const group of groups) {
      group.querySelector('[data-error]').textContent = '';
      group.querySelectorAll('[aria-invalid]').forEach(control => control.removeAttribute('aria-invalid'));
    }
    for (const control of controls) storage('setItem', control.id, control.type === 'radio' ? control.checked : control.value);
    refresh();
    if (!storageWorks) say('Draft storage unavailable. Keep this tab open until answers are saved.');
  });
  form.addEventListener('click', event => {
    const clear = event.target.closest('[data-clear]');
    if (!clear || busy || saved) return;
    clear.closest('fieldset').querySelectorAll('input').forEach(input => { input.checked = false; });
    form.dispatchEvent(new Event('input'));
  });
  const lock = value => { form.querySelectorAll('input,textarea,button').forEach(control => { control.disabled = value; }); };
  async function request(path, options = {}) {
    const response = await fetch(new URL(path, base), {...options, signal: AbortSignal.timeout(10000)});
    const text = await response.text();
    if (!response.ok) {
      const error = new Error(text);
      error.status = response.status;
      throw error;
    }
    return text;
  }
  async function send() {
    busy = true; lock(true); say('Saving answers…');
    try {
      await request(`submit/${round}`, {method:'POST', headers:{'X-Grill-Submit':'1'}, body:pending});
      saved = true; pending = null; storage('removeItem', 'pending');
      say('Answers saved. Waiting for the agent.');
    } catch (error) {
      if (error.status === 400) {
        pending = null; storage('removeItem', 'pending'); lock(false);
        submissionError = 'Not saved. ' + error.message;
        say(submissionError);
      } else {
        say('Not confirmed saved. Your answers are kept here; retrying automatically.');
      }
    } finally { busy = false; }
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (busy || saved || pending) return;
    let invalid = null;
    const fields = new URLSearchParams();
    for (const group of groups) {
      const choice = group.querySelector('input:checked');
      const text = group.querySelector('[data-text]');
      const error = group.querySelector('[data-error]');
      const missing = !choice || (choice.value === 'custom' && !text.value.trim());
      error.textContent = missing ? 'Choose an option, write an answer, or select Discuss first.' : '';
      const target = choice?.value === 'custom' ? text : group.querySelector('input');
      target.setAttribute('aria-invalid', String(missing));
      if (missing) invalid ||= target;
      fields.set(group.dataset.question + '.choice', choice?.value || '');
      fields.set(group.dataset.question + '.text', text.value);
      fields.set(group.dataset.question + '.context', group.querySelector('[data-context]').value);
    }
    if (invalid) { invalid.focus(); return; }
    pending = fields;
    storage('setItem', 'pending', fields.toString());
    send();
  });
  const restored = storage('getItem', 'pending');
  if (restored) { pending = new URLSearchParams(restored); lock(true); }
  refresh();
  async function check() {
    try {
      const state = await request(`state/${round}`);
      if (state.includes('saved: true')) {
        saved = true; pending = null; lock(true); storage('removeItem', 'pending');
        say('Answers saved. Waiting for the agent.');
        if (state.includes('complete: true')) {
          location.replace(new URL('complete.html', base));
          return;
        }
        const next = Number(state.match(/round: (\d+)/)[1]);
        if (next > round) location.replace(new URL(`round-${next}.html`, base));
      } else if (pending && !busy) { await send(); }
      else if (!busy && !submissionError) say(storageWorks ? 'Ready. Answers stay on this computer.' : 'Draft storage unavailable. Keep this tab open.');
    } catch {
      if (!busy) say(saved ? 'Answers saved. Session connection interrupted.' : 'Connection interrupted. Keep this tab open; reconnecting automatically.');
    } finally { setTimeout(check, 2000); }
  }
  check();
})();
'''


class SessionServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, directory):
        self.directory = Path(directory).resolve(strict=True)
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.schemas = {}
        super().__init__(("127.0.0.1", 0), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"
        self.base = f"{self.origin}/{self.token}/"

    def file(self, name):
        path = self.directory / name
        if path.is_symlink() or path.resolve().parent != self.directory:
            raise ValueError("Session files must stay inside the session directory")
        return path

    def latest(self):
        rounds = [int(match[1]) for path in self.directory.glob('round-*.html')
                  if (match := re.fullmatch(r"round-([1-9][0-9]*)\.html", path.name))]
        if not rounds:
            raise ValueError("Create round-1.html before starting the session")
        return max(rounds)

    def page(self, number):
        html = self.file(f"round-{number}.html").read_text(encoding="utf-8")
        schema = Questions(html).questions
        if '</body>' not in html or 'id="grill-form"' not in html or 'id="session-status"' not in html:
            raise ValueError("Round needs grill-form, session-status, and a closing body tag")
        self.schemas.setdefault(number, schema)
        if self.schemas[number] != schema:
            raise ValueError("Published questions changed; create a new round")
        return html.replace('</body>', '<script src="client.js" defer></script></body>')


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def log_message(self, *args):
        pass  # Do not log capability URLs or private answers.

    def respond(self, status, text, mime="text/toon"):
        body = text.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; img-src data:; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def route(self):
        if self.headers.get('Host') != urlsplit(self.server.origin).netloc:
            raise PermissionError("Invalid session host")
        prefix = '/' + self.server.token + '/'
        path = urlsplit(self.path).path
        if not path.startswith(prefix):
            raise PermissionError("Invalid session URL")
        return path[len(prefix):]

    def do_GET(self):
        try:
            route = self.route()
            if route == 'client.js':
                return self.respond(200, CLIENT, 'text/javascript')
            if route == 'complete.html':
                return self.respond(200, self.server.file('complete.html').read_text(encoding='utf-8'), 'text/html')
            if match := re.fullmatch(r'round-([1-9][0-9]*)\.html', route):
                return self.respond(200, self.server.page(int(match[1])), 'text/html')
            if match := re.fullmatch(r'state/([1-9][0-9]*)', route):
                saved = self.server.file(f'answers-{match[1]}.toon').is_file()
                complete = self.server.file('complete.html').is_file()
                return self.respond(200, f"round: {self.server.latest()}\nsaved: {str(saved).lower()}\ncomplete: {str(complete).lower()}")
            self.respond(404, 'error: "Unknown session resource"')
        except PermissionError as error:
            self.respond(403, f'error: {quote(error)}')
        except ValueError as error:
            self.respond(400, f'error: {quote(error)}')
        except OSError:
            self.respond(500, 'error: "Session file unavailable; check local file access"')

    def do_POST(self):
        try:
            route = self.route()
            if (self.headers.get('Origin') != self.server.origin
                    or self.headers.get('X-Grill-Submit') != '1'):
                raise PermissionError("Submit from the session page")
            match = re.fullmatch(r'submit/([1-9][0-9]*)', route)
            if not match:
                raise ValueError("Unknown submission route")
            if self.headers.get_content_type() != 'application/x-www-form-urlencoded':
                raise ValueError("Expected form-encoded answers")
            if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length', [])) != 1:
                raise ValueError("Expected one bounded request body")
            size = int(self.headers['Content-Length'])
            if not 0 < size <= 262144:
                raise ValueError("Answers must fit within 256 KiB")
            body = self.rfile.read(size)
            if len(body) != size:
                raise ValueError("Incomplete submission")
            fields = parse_qs(body.decode('utf-8'), keep_blank_values=True,
                              strict_parsing=True, errors='strict', max_num_fields=600)
            number = int(match[1])
            with self.server.lock:
                if number not in self.server.schemas:
                    raise ValueError("Open the round before submitting")
                text = packet(self.server.directory.name, number, self.server.schemas[number], fields)
                save_once(self.server.file(f'answers-{number}.toon'), text)
            self.respond(200, 'status: saved')
        except PermissionError as error:
            self.respond(403, f'error: {quote(error)}')
        except ValueError as error:
            self.respond(400, f'error: {quote(error)}')
        except OSError:
            self.respond(500, 'error: "Could not save answers; check local file access"')


class Parser(argparse.ArgumentParser):
    def error(self, message):
        report(error=message, help='Run session.py --help for commands and flags')
        raise SystemExit(2)


def main():
    parser = Parser(description="Local HTML interviews with TOON submissions.", allow_abbrev=False)
    commands = parser.add_subparsers(dest='command')
    serve = commands.add_parser('serve', help='Serve a session on loopback', allow_abbrev=False)
    serve.add_argument('directory', type=Path)
    serve.add_argument('--open', action='store_true', help='Open the normal browser')
    wait = commands.add_parser('wait', help='Wait for a saved round; output full TOON', allow_abbrev=False)
    wait.add_argument('directory', type=Path)
    wait.add_argument('--round', type=int, required=True)
    wait.add_argument('--timeout', type=int, default=45, help='Seconds before status: waiting (1-60)')
    args = parser.parse_args()
    if args.command is None:
        report(bin=Path(__file__).resolve(), status='No session started',
               help='session.py serve <directory> --open; session.py wait <directory> --round 1')
        return
    try:
        if args.command == 'wait':
            if args.round < 1 or not 1 <= args.timeout <= 60:
                parser.error('Use a positive round and timeout between 1 and 60')
            directory = args.directory.resolve(strict=True)
            path = directory / f'answers-{args.round}.toon'
            deadline = time.monotonic() + args.timeout
            while True:
                if path.is_symlink():
                    raise ValueError('Answer path must not be a symbolic link')
                if path.is_file():
                    print(path.read_text(encoding='utf-8'), flush=True)
                    return
                if time.monotonic() >= deadline:
                    report(status='waiting', round=args.round)
                    return
                time.sleep(0.25)
        with SessionServer(args.directory) as server:
            number = server.latest()
            server.page(number)
            url = server.base + f'round-{number}.html'
            report(status='ready', url=url, directory=server.directory)
            if args.open and not webbrowser.open(url):
                report(status='Open the printed session URL in your browser')
            server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        report(status='stopped')
    except (OSError, ValueError) as error:
        report(error=error, help='Check the session directory and generated round HTML')
        raise SystemExit(1)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
