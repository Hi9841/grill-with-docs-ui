# Live browser session

Use Lavish Editor as the browser transport. It serves the generated HTML, provides the review UI, and returns submitted feedback to the foreground agent through polling.

Read its current guidance before use:

```text
npx -y lavish-axi --help
npx -y lavish-axi playbook input
```

Generate the round under `.lavish/` unless the project has an existing artifact location. Follow the input playbook for controls, submission state, and feedback hooks. Keep the page self-contained. Do not add a server, package scaffold, custom bridge, Playwright setup, or browser-connection questions.

Open the artifact and leave the session available to the user:

```text
npx -y lavish-axi <path-to-round.html>
```

Then wait in the foreground:

```text
npx -y lavish-axi poll <path-to-round.html>
```

Tell the user only to answer in the page and press Submit. Do not ask them to copy answers, send a reprompt, or say "continue". Poll delivery is the handoff.

When poll returns feedback, read it completely. Confirm the session and round identity, question IDs, choices, custom text, and deferred flags. Save the exact validated answer packet to `answers-N.toon`, then update the design tree and generate the next round. Reopen the next artifact in the same Lavish flow and poll again. Preserve prior rounds and snapshots.

If Lavish returns `browser_disconnected`, follow its current recovery guidance. Do not claim answers were saved until the workspace file was written and read back. If polling is killed or times out, rerun it because queued feedback remains available. End the session only after completion or explicit user request.
