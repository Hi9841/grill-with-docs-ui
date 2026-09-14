# Grill with docs UI

Stress-test a plan in a readable browser questionnaire. Keep the questioning discipline of **grilling** and the vocabulary and decision records of **domain-modeling**, without a wall of terminal questions.

A standalone skill with one small local Python helper and a reusable HTML template. No Lavish, Playwright, framework, or third-party Python packages. Handoffs use **TOON**, not JSON.

## Install

Using the [Skills CLI](https://github.com/vercel-labs/skills), choose your agent and installation scope:

```bash
pnpm dlx skills add Hi9841/grill-with-docs-ui
```

Or with Bun:

```bash
bunx skills add Hi9841/grill-with-docs-ui
```

The repository root is the skill. There is no inner skill folder.

For manual installation, download or clone the repository. Put `SKILL.md`, `scripts/`, `assets/`, `references/`, `agents/`, and `LICENSE` directly inside your agent's configured `skills/grill-with-docs-ui/` directory. Keep these resources together. The optional `agents/openai.yaml` supplies Codex display metadata; the workflow itself is agent-neutral.

Your installed folder should look like this:

```text
skills/grill-with-docs-ui/
  SKILL.md
  scripts/session.py
  assets/round.html
  references/
  agents/openai.yaml
  LICENSE
```

For local development, point the agent's skill registration at this repository root. To install the current checkout with the Skills CLI, run `bunx skills add . --skill grill-with-docs-ui` from this directory. Installing from GitHub uses the published version, not uncommitted local edits.

The grilling and domain-modeling guidance is included. No other skill installation is needed.

### Browser requirements

Python 3.10+ and a modern browser on the same computer as the agent. The agent starts the bundled helper automatically and stays active waiting for submissions. No browser-inspection tool is needed. Remote terminals need an explicitly configured secure port-forward or a browser on their host; plain chat without process/file tools cannot run this skill.

### Updating an older installation

Back up any local customizations, then replace the old installation with the current skill package rather than merging directories. An old outer `SKILL.md` can hide an updated nested copy. Keep only one entrypoint in the installed skill folder.

If the agent still tries to launch `lavish-axi`, check the exact `SKILL.md` path it loaded. The current workflow runs `scripts/session.py serve`, then `scripts/session.py wait`. Verify that the helper exists beside that entrypoint:

```bash
python "<installed-skill-directory>/scripts/session.py" --version
```

After replacing an older installation, reload skills or start a fresh agent session so previously loaded instructions are not reused. Installing this skill does not change instructions already held by another running agent.

## Use it

Ask your agent:

> Use grill-with-docs-ui to stress-test my booking-system plan. Put the questions in a browser page and document the terms and decisions we settle.

For agents supporting dollar-prefixed skill invocation, use `$grill-with-docs-ui`.

1. The agent investigates the project and generates one scrollable page containing all currently independent questions. Each includes a recommendation, left unselected.
2. Answer in your browser and choose **Submit round**. You can give custom answers or defer a question with **Discuss first**. There is nothing to paste or send in chat.
3. The helper saves the answers and the waiting agent receives them, updates agreed terms and qualifying decision records, and writes the next round. It opens automatically in the same tab. Questions that depend on earlier answers wait until those decisions are settled.

The interview ends with an explicit confirm-or-revise question, not an assumed agreement.

## Saving answers

Submit freezes the round and saves an immutable TOON snapshot in the session directory. The page confirms saving only after the helper verifies the file. The agent's wait command reads that snapshot without consuming or deleting it. Keep the agent active during the interview; the helper can save answers but cannot wake a stopped agent. Browser drafts are best effort, not a replacement for saved submissions.

Sessions normally live under `.grill-with-docs/<topic>-<unique-suffix>/`:

```text
design-tree.md       Decisions, prerequisites, and open branches
round-1.html         Question page served by the helper
answers-1.toon       Submitted answers saved by the helper
round-2.html         Follow-up questions, when needed
```

Resolved vocabulary goes in the project's `CONTEXT.md` files. An ADR is offered only for a hard-to-reverse, non-obvious decision with a genuine tradeoff. Session files may contain sensitive project details; keep them out of public commits unless intentionally shared.

Example answer packet:

```toon
session: booking-rules-a7c2
round: 1
status: submitted
answers[2]{id,choice,text,deferred}:
  ownership,team,"Keep access when a member leaves.",false
  cancellation,"","Explain the refund timing first.",true
```

The helper listens on `127.0.0.1` with a random port and a private session URL. It checks request origins and serves only interview resources, not arbitrary workspace files. The page needs no internet access; it only contacts this local helper. This is not a hosted service. Keep the session URL and answer files private.

## Design

Large readable text, a single reading column, flat question sections, and quiet recommendations. Optional notes stay out of the way until needed. All current questions remain in one scrollable page, with native keyboard-accessible controls and one primary Submit action. Transport data stays out of the form.

## Repository structure

```text
README.md
LICENSE
SKILL.md
agents/openai.yaml
scripts/session.py
assets/round.html
references/
  domain-docs.md
  live-session.md
  page-design.md
tests/test_package.py
tests/test_session.py
```

## Verification

From the repository root:

```bash
python -B -m unittest discover -s tests -v
```

The tests use temporary sessions and the Python standard library. They cover full-text handoff, validation, retry safety, receipt recovery, and request boundaries. Browser behavior also needs a real session check; unit tests alone do not verify keyboard operation or layout.

## Credits and license

The grilling and domain-modeling workflow is adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills), composed by his grill-with-docs skill. Packaging follows [how-to-choose-an-llm](https://github.com/Hi9841/how-to-choose-an-llm). Answer handoffs use [TOON](https://toonformat.dev/reference/spec.html), following AXI's preference for concise agent-facing output.

[MIT license](LICENSE). Upstream copyright is retained.
