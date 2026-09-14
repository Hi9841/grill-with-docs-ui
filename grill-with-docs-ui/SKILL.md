---
name: grill-with-docs-ui
description: Run grilling and domain-modeling interviews in a clean browser questionnaire with automatic TOON answer collection on Submit. Use when the user wants grill-with-docs in a browser instead of terminal questions.
---

# Grill with docs UI

Keep the rigor of grilling and the documentation discipline of domain-modeling. Make the questions easy to read and answer in a browser.

## Foundations

This skill includes the core grilling and domain-modeling workflow below. No other skill or specific browser vendor is required. Automatic submission requires an agent-controlled, user-visible browser and a live agent turn that can wait for browser events or poll. If the user also requests an installed foundation skill, read it and incorporate its local guidance without replacing this browser workflow.

Grilling: stress-test the plan, expose assumptions and edge cases, and follow every decision branch. Track prerequisites in a design tree. The frontier is every unresolved question whose prerequisites are settled; present these together, leaving dependent questions for later rounds. Investigate facts yourself; ask the user for decisions. Recommend an answer with reasoning, but never treat the recommendation or silence as consent.

Domain-modeling: challenge ambiguous terms, conflicting definitions, and overloaded names. Test definitions with concrete examples and cross-check claims against available code. Capture agreed vocabulary as it emerges, keep speculative answers out of the glossary, and preserve material decision rationale selectively.

Use AXI's concise TOON convention for agent-facing answer handoffs. Keep this skill as instructions: generate the HTML directly, without a bundled server, CLI, package scaffold, or separate runtime scripts. Small inline browser JavaScript for the form is enough.

## Run the interview

Before generating a round, read [references/live-session.md](references/live-session.md). Use Lavish Editor's input playbook and review loop for the page. Do not substitute a terminal interview.

1. Inspect project instructions, relevant code, CONTEXT-MAP.md or CONTEXT.md, and relevant decisions. Investigate facts using available tools and permitted delegation. Keep unresolved branches and prerequisites in a session-local `design-tree.md`; pending investigations block only their dependent questions.
2. Read [references/page-design.md](references/page-design.md) before generating HTML. Create `round-N.html` in a dedicated session folder under the project, normally `.grill-with-docs/<topic>-<unique-suffix>/`. Present the **whole current frontier** in one scrollable page. Give each question a stable ID, number, title, question, recommendation with its reason, and optional choices. Ask dependent questions only after their prerequisites are settled. Preserve earlier round files.
3. Open the round with `npx -y lavish-axi <html-file>` and leave its review session running. Tell the user only to answer in the page and press Submit. Lavish's browser UI carries the response back to the agent.
4. Run `npx -y lavish-axi poll <html-file>` in the foreground. When feedback arrives, read the complete response, validate the submitted answers, and save them to `answers-N.toon` with normal file tools. Drafts, unanswered questions, and "Discuss first" are not settled decisions.
5. Read every answer, reconcile contradictions, and update the tree. Before creating or editing a glossary or ADR, read [references/domain-docs.md](references/domain-docs.md) for routing, formats, and the ADR threshold. Capture resolved terms immediately. Generate the next frontier and open it in the same tab when possible. Revisions get new question IDs and reopen dependent decisions. On resume, read the tree and saved answers first.

## Shape the page

Use one self-contained HTML file with inline CSS and only the JavaScript its interactions need. Put questions directly in semantic HTML; escape text safely instead of injecting markup from answers. No network requests, framework, build step, or JSON question/answer files.

The page-design reference sets the reading layout and accessible controls. The live-session reference defines the Lavish input playbook handoff. Keep transport details out of the questionnaire; the user's normal handoff is one Submit action.

## TOON handoff

Use a compact fixed-column packet. This example illustrates the format, not questions to reuse:

```toon
session: booking-rules-a7c2
round: 1
status: submitted
answers[2]{id,choice,text,deferred}:
  ownership,team,"Keep access when a member leaves.",false
  cancellation,"","Explain the refund timing first.",true
```

Keep full answers intact. Use stable option IDs for `choice`, or an empty string for a custom or deferred answer. Match the row count to the round and retain one row per question. Encode booleans as booleans. For arbitrary string fields, always use double quotes and escape backslashes, double quotes, LF, CR, and tabs as `\\`, `\"`, `\n`, `\r`, and `\t`; encode remaining control characters as `\uXXXX`. Leave ordinary Unicode intact. This quoted-string subset of the [TOON specification](https://toonformat.dev/reference/spec.html) needs no dependency or network lookup. Use TOON for exported and saved answers, not JSON with a `.toon` extension. Markdown remains appropriate for the decision tree, glossary, and ADRs.

A stored packet is a snapshot. Freeze the round after submission; corrections belong in a new round. Never overwrite an answer file the agent already received.

## Finish

When every branch is resolved, present the synthesis, changed document paths, and an explicit confirm-or-revise question in the page. An empty frontier alone is not confirmation. After confirmation, report the agreed outcome and docs. Implementation follows the user's existing authorization.

Before presenting a generated round, verify its real content, no preselected answers, keyboard flow, and narrow layout. In a separate disposable test page, check that punctuation and a line break survive Submit, automatic capture, workspace save, acknowledgment, and next-round navigation without a chat message. Keep test answers out of the real interview. Report unavailable checks rather than claiming a connection that has not been established.
