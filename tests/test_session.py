"""Disposable stdlib tests. No dependencies or project-side test artifacts."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/session.py'
spec = importlib.util.spec_from_file_location('session', SCRIPT)
session = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session)

HTML = '''<!doctype html><html><body><form id="grill-form">
<fieldset data-question="ownership"><legend>Ownership</legend>
<input type="radio" name="ownership" value="team">
<input type="radio" name="ownership" value="custom">
<input type="radio" name="ownership" value="discuss">
<div data-custom><textarea data-text></textarea></div>
<textarea data-context></textarea><p data-error></p><button data-clear></button></fieldset>
</form><p id="session-status"></p></body></html>'''


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='grill-test-')
        self.directory = Path(self.temp.name)
        (self.directory / 'round-1.html').write_text(HTML, encoding='utf-8')
        self.server = session.SessionServer(self.directory)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.request('round-1.html')

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, route, fields=None, headers=None):
        defaults = {'Origin': self.server.origin, 'X-Grill-Submit': '1',
                    'Content-Type': 'application/x-www-form-urlencoded'}
        defaults.update(headers or {})
        request = Request(self.server.base + route, headers=defaults,
                          data=urlencode(fields).encode() if fields is not None else None)
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, response.read().decode()
        except HTTPError as error:
            return error.code, error.read().decode()

    def test_wait_receives_exact_saved_unicode_and_multiline(self):
        waiter = subprocess.Popen([sys.executable, str(SCRIPT), 'wait', str(self.directory),
                                   '--round', '1', '--timeout', '5'], stdout=subprocess.PIPE)
        text = '  A, "quote" \\ path\nline\r\ntab\tשלום😀\x01  '
        fields = {'ownership.choice': 'custom', 'ownership.text': text}
        self.assertEqual(self.request('submit/1', fields)[0], 200)
        output, _ = waiter.communicate(timeout=6)
        expected = session.packet(self.directory.name, 1, {'ownership': {'custom'}},
                                  {key: [value] for key, value in fields.items()})
        self.assertEqual((self.directory / 'answers-1.toon').read_bytes(), expected.encode())
        self.assertEqual(output.decode().replace('\r\n', '\n').rstrip('\n'), expected)
        self.assertEqual(session.quote('a\n"\\\t\x01'), '"a\\n\\"\\\\\\t\\u0001"')

    def test_duplicate_retries_are_idempotent_and_changes_rejected(self):
        first = {'ownership.choice': 'team'}
        self.assertEqual(self.request('submit/1', first)[0], 200)
        self.assertEqual(self.request('submit/1', first)[0], 200)
        self.assertEqual(self.request('submit/1', {'ownership.choice': 'discuss'})[0], 400)
        self.assertIn('"team"', (self.directory / 'answers-1.toon').read_text())

    def test_validation_rejects_incomplete_unknown_duplicate_and_blank(self):
        for fields in ({}, {'ownership.choice':'bogus'},
                       {'ownership.choice':'custom', 'ownership.text':' \n '},
                       {'ownership.choice':'team', '../file':'bad'},
                       [('ownership.choice','team'), ('ownership.choice','discuss')]):
            self.assertEqual(self.request('submit/1', fields)[0], 400)
        self.assertFalse((self.directory / 'answers-1.toon').exists())

    def test_deferred_is_open_with_context(self):
        self.assertEqual(self.request('submit/1', {'ownership.choice':'discuss',
                                                 'ownership.context':'Need examples'})[0], 200)
        self.assertIn('"ownership","","Need examples",true',
                      (self.directory / 'answers-1.toon').read_text())

    def test_origin_host_token_and_resource_boundaries(self):
        self.assertEqual(self.request('submit/1', {'ownership.choice':'team'},
                                      {'Origin':'https://evil.example'})[0], 403)
        self.assertEqual(self.request('round-1.html', headers={'Host':'evil.example'})[0], 403)
        self.assertEqual(self.request('../round-1.html')[0], 404)
        with self.assertRaises(HTTPError) as denied:
            urlopen(self.server.origin + '/wrong-token/round-1.html', timeout=3)
        self.assertEqual(denied.exception.code, 403)
        for route in ('design-tree.md', 'answers-1.toon', '../../secret', 'scripts/session.py'):
            self.assertEqual(self.request(route)[0], 404)

    def test_next_round_and_completion_are_discoverable(self):
        self.request('submit/1', {'ownership.choice':'team'})
        (self.directory / 'round-2.html').write_text(HTML, encoding='utf-8')
        state = self.request('state/1')[1]
        self.assertIn('round: 2', state)
        self.assertIn('saved: true', state)
        (self.directory / 'complete.html').write_text('<h1>Done</h1>')
        self.assertIn('complete: true', self.request('state/1')[1])
        self.assertEqual(self.request('complete.html'), (200, '<h1>Done</h1>'))

    def test_restart_restores_receipt_from_disk(self):
        self.request('submit/1', {'ownership.choice':'team'})
        self.server.schemas.clear()
        self.assertIn('saved: true', self.request('state/1')[1])
        self.assertEqual(self.request('submit/1', {'ownership.choice':'team'})[0], 400)
        self.request('round-1.html')
        self.assertEqual(self.request('submit/1', {'ownership.choice':'team'})[0], 200)

    def test_preselection_and_schema_changes_fail(self):
        with self.assertRaises(ValueError):
            session.Questions(HTML.replace('value="team"', 'value="team" checked'))
        with self.assertRaises(ValueError):
            session.Questions(HTML.replace('data-text', 'missing-hook'))
        (self.directory / 'round-1.html').write_text(HTML.replace('value="team"', 'value="person"'))
        self.assertEqual(self.request('round-1.html')[0], 400)

    def test_large_payload_fails_without_save(self):
        self.assertEqual(self.request('submit/1', {'ownership.choice':'custom',
                                                  'ownership.text':'x' * 270000})[0], 400)
        self.assertFalse((self.directory / 'answers-1.toon').exists())

    def test_cli_validation_and_version(self):
        for flag in ('-v', '-V', '--version'):
            result = subprocess.run([sys.executable, str(SCRIPT), flag], capture_output=True)
            self.assertEqual(result.stdout.strip(), b'1.0.0')
        result = subprocess.run([sys.executable, str(SCRIPT), 'serve', str(self.directory),
                                 '--bogus'], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'error:', result.stdout)


if __name__ == '__main__':
    unittest.main()
