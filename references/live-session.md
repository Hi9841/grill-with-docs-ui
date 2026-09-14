# Live browser session

Use the bundled `scripts/session.py`, resolved from the directory containing the loaded `SKILL.md`. It is one Python 3.10+ standard-library helper with no packages to install. Choose an available interpreter, such as `python3`, `python`, `py -3`, or `uv run python`. Verify its version. Use this helper directly; no third-party viewer or browser automation is required.

## Start and wait

Create a unique project-local session directory, normally `.grill-with-docs/<topic>-<unique-suffix>/`. Copy `assets/round.html` into it as `round-1.html`, replace the sample content with the entire current frontier, and preserve the form contract below. Read `references/page-design.md` before changing the layout. Example commands below use `python`; replace it with the verified interpreter:

```text
python <skill-directory>/scripts/session.py serve <session-directory> --open
```

Keep `serve` in a tracked long-running process. It reports a private loopback URL and opens the ordinary browser. If browser launch is unavailable, provide that URL; do not require DOM automation. Remote terminals need a browser on the same machine or an explicitly authorized secure port-forward. Never expose this helper on a public interface.

Wait for the round through a normal foreground tool call:

```text
python <skill-directory>/scripts/session.py wait <session-directory> --round 1 --timeout 45
```

The command returns the complete saved TOON packet when Submit succeeds. An unchanged round returns `status: "waiting"` after the timeout. Repeat the wait; keep the agent turn active. If the tool returns a running-process ID, resume that process rather than launching duplicate waits. Maintain required concise progress updates. A helper process cannot wake an agent that has ended its turn.

Submission is written atomically as `answers-1.toon` and verified before the browser reports success. Retries with identical contents are idempotent; conflicting submissions are rejected. Read the file and reconcile the answers. Write each later round to a staging filename first, then rename it to `round-N.html` only when complete. The page checks for the next numbered round every two seconds and navigates automatically once its current answers are saved. Do not change published questions in place.

After final user confirmation, publish `complete.html` containing the synthesis. The browser navigates to it automatically. Allow time for its two-second check and page load before stopping the owned server process. During an interruption, saved answers remain on disk; restart `serve` in the same directory and reopen the printed URL to resume. Pending browser drafts are best effort and scoped to the current URL. They are not guaranteed across a server restart, so do not stop a server with unsaved answers.

## Form contract

The template is the working example. The helper injects its browser code; write no submit handler or external scripts. Use double-quoted attributes and a closing lowercase `</body>` tag.

- Exactly one `<form id="grill-form" novalidate>` with a `button type="submit"`, and a separate `<p id="session-status" role="status">`. Optional progress goes in `#answer-progress`.
- Each flat `fieldset` has a unique `data-question="stable-id"`, a legend, and native radio inputs. Radio `name` equals the question ID. All question and option IDs match `[a-z][a-z0-9-]{0,63}`. No checked defaults.
- Include radio choices `custom` and `discuss`, reserved for "Write my own answer" and "Discuss first". Other choices have meaningful stable IDs. A `[data-custom]` container holds a labeled `textarea[data-text]`. A details section holds a labeled `textarea[data-context]`.
- Each question has a `button type="button" data-clear` and a `p[data-error]` with a unique ID. Connect controls to that error using `aria-describedby`. All radio inputs and textareas need unique DOM IDs for draft storage.

The browser submits ordinary URL-encoded form fields to the helper. The helper creates the TOON handoff; no JSON is used. A custom answer plus optional context becomes one text field separated by a blank line. Deferred questions remain unresolved.

## Boundaries and failures

The server binds only to `127.0.0.1` on a random port, checks Host and Origin, uses an unguessable session URL, and rejects arbitrary files and oversized submissions. Do not share its URL or commit private session artifacts. It is a local development helper, not a production service. It only serves numbered HTML rounds, its client code, receipt state, and the completion page.

The helper supplies best-effort browser drafts, inline validation, frozen submissions, receipt confirmation, and automatic retry after transient failures. Do not claim receipt from a draft. Resolve persistent save or contract errors in the existing session without overwriting previous answers. Keep the normal user flow to answering and pressing Submit.

Maintainer check:

```text
python -B -m unittest discover -s tests -v
```
