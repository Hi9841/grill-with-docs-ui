# Grill with docs UI

Stress-test a plan in a readable browser questionnaire. Keep the questioning discipline of **grilling** and the vocabulary and decision records of **domain-modeling**, without a wall of terminal questions.

Instruction-only skill. No bundled server, CLI, framework, or runtime scripts. The agent generates self-contained HTML with a little inline JavaScript for answers. Handoffs use **TOON**, not JSON.

## Install

Using the [Skills CLI](https://github.com/vercel-labs/skills), choose your agent and installation scope:

```bash
pnpm dlx skills add Hi9841/grill-with-docs-ui
```

Or with Bun:

```bash
bunx skills add Hi9841/grill-with-docs-ui
```

For manual installation, download or clone this repository and copy the inner `grill-with-docs-ui/` folder into your agent's configured skills directory. Keep `SKILL.md` and `references/` together. The optional `agents/openai.yaml` supplies Codex display metadata; the workflow itself is agent-neutral.

No separate installation of grilling, domain-modeling, grill-with-docs, AXI, or Lavish is needed. Their relevant workflow principles are included here.

### Browser requirements

The skill uses Lavish Editor's existing artifact and polling workflow. It opens the generated page, lets you answer once, and returns Submit feedback to the foreground agent. No Playwright setup or custom browser bridge is needed.

## Use it

Ask your agent:

> Use grill-with-docs-ui to stress-test my booking-system plan. Put the questions in a browser page and document the terms and decisions we settle.

For agents supporting dollar-prefixed skill invocation, use `$grill-with-docs-ui`.

1. The agent investigates the project and generates one scrollable page containing all currently independent questions. Each includes a recommendation, left unselected.
2. Answer in the Lavish page and choose **Submit round**. You can give custom answers or defer a question with **Discuss first**. There is nothing to paste or send in chat.
3. The waiting agent automatically collects and saves the answers, updates agreed terms and qualifying decision records, and opens the next round. Questions that depend on earlier answers wait until those decisions are settled.

The interview ends with an explicit confirm-or-revise question, not an assumed agreement.

## Saving answers

Submit freezes the round and the Lavish poll returns it to the foreground agent, which saves it to your workspace. Keep the poll running during the interview. If it is interrupted, rerun it because Lavish keeps queued feedback.

Sessions normally live under `.grill-with-docs/<topic>-<unique-suffix>/`:

```text
design-tree.md       Decisions, prerequisites, and open branches
round-1.html         Self-contained question page
answers-1.toon      Submitted answers saved by the agent
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

The generated page is served by Lavish for the review session. This is a skill that generates pages, not a hosted web application.

## Design

Large readable text, a single reading column, flat question sections, and quiet recommendations. Optional notes stay out of the way until needed. All current questions remain in one scrollable page, with native keyboard-accessible controls and one primary Submit action. Transport data stays out of the form.

## Repository structure

```text
README.md
LICENSE
grill-with-docs-ui/
  SKILL.md
  agents/openai.yaml
  references/
    domain-docs.md
    live-session.md
    page-design.md
```

## Credits and license

The grilling and domain-modeling workflow is adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills), composed by his grill-with-docs skill. Packaging follows [how-to-choose-an-llm](https://github.com/Hi9841/how-to-choose-an-llm). Answer handoffs use [TOON](https://toonformat.dev/reference/spec.html), following AXI's preference for concise agent-facing output.

[MIT license](LICENSE). Upstream copyright is retained.
