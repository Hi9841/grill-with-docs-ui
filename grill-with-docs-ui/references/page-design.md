# Page design

Design for reading and deciding, not for operating a developer dashboard. Keep all independent questions in the document flow. Use space and typography to separate them, not stacks of nested cards.

## Reading layout

Use a centered reading column around 46rem wide, with at least 1.25rem side padding on phones. Use an available system font stack so the file works offline. Body and inputs start at 1rem, line-height 1.55 to 1.65. Question headings are around 1.4rem; the page title around 2rem. Supporting text must remain readable, normally at least 0.875rem. Keep the browser's zoom available.

Start with a meaningful title and one sentence explaining the round. Put round number, answered count, and connection state in a quiet secondary row, not a terminal-style session-ID banner. Keep internal IDs in DOM attributes. For long rounds, add compact text anchor links, not badge-like navigation buttons.

Separate question sections with generous vertical space, around 2.5rem, and at most a subtle divider. Each has a short numbered heading, the decision being asked, an understated recommendation, and the answers. Recommendations use a small text label and one reason, without bright green panels, emoji, or extra card borders. Keep material tradeoffs visible; shorten repetition rather than hiding information needed to decide.

Use the project's palette if appropriate. Without one, start with a warm off-white page, near-ink text, and one muted accent for selections, focus, and the primary action. Respect a requested dark theme with the same restrained hierarchy. Use semantic CSS tokens, preferably OKLCH, and verify text contrast instead of making secondary text faint. Avoid gradients, glass, heavy shadows, decorative motion, and monospace interface copy.

## Question controls

Use native radio inputs with full-row labels, grouped by a fieldset and legend. Option titles should carry the distinction; add one short sentence only when needed. Prefer a flat option list with subtle separators and a restrained selected background. The outer question is not another card. Leave every choice unselected, including recommendations.

Include "Write my own answer" and "Discuss first" as mutually exclusive options, not independent checkboxes that can conflict with a selected answer. A custom choice reveals a labeled, required textarea. Put optional elaboration behind a native `details` element labeled "Add context" so empty textareas do not dominate every question. Preserve hidden draft text when switching choices. Provide a quiet "Clear answer" button for resetting the selection.

Use visible native focus indicators, 44px touch targets, and labels bound to each control. Put validation errors beside the question, reference them with `aria-describedby`, mark the invalid control, and focus the first invalid control. Custom answers containing only whitespace are unanswered. Deferred choices are valid submissions but stay unresolved in the interview.

## Footer and feedback

Use one primary button, "Submit round", next to answered progress and a short status. Drafts save automatically; omit a separate Save draft action. A sticky footer is optional: reserve its space and ensure it never obscures the final input or a focused error on small screens or at zoom. An ordinary in-flow footer is safer when space is tight.

After Submit, preserve the question context and display "Submitted. Waiting for the agent." After the agent verifies the saved file, show "Answers saved. Preparing the next round." These are different states, not optimistic success messages. Put routine updates in a stable `role="status"` region. The next page opens in the same tab with its title at the top; the agent continues without a chat prompt.

Keep TOON and technical status attributes hidden from the normal form. A backup download may appear under recovery details during a connection failure, but is never a required step or a substitute for the automatic handoff.

## Check the generated page

Inspect desktop and narrow layouts in one pass. Verify readable real copy, 320px reflow, 200% zoom, no preselection, accessible names and roles, keyboard-only completion, visible focus, inline errors, and custom/deferred answers. Check text contrast, selected-state contrast, and status announcements. Fix related defects together and confirm once. Record anything unavailable, including screen-reader testing; a screenshot alone does not prove accessibility.
