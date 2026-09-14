# Domain documentation

Use these formats when recording interview outcomes. Follow the project's existing conventions when they differ.

## Glossary

If `CONTEXT-MAP.md` exists, read it to find the relevant bounded context and its glossary. Otherwise use the relevant existing `CONTEXT.md`; create a root glossary only when a resolved term needs recording. Avoid unrelated context files.

Record each agreed term immediately, with its meaning and any important boundary or avoided synonym. Challenge conflicts before replacing existing definitions. Keep the glossary about domain language, not implementation plans, feature specifications, or interview notes. Unresolved questions belong in the session's `design-tree.md`.

```markdown
# Booking context

Language for reserving a shared resource.

## Language

### Reservation

A time-bounded claim on a resource, held by a team rather than an individual member. Avoid "appointment", which implies a person-to-person meeting.
```

Use one or two sentences per term where possible. Follow a context map's linking conventions if a new context file is genuinely needed; do not invent a context hierarchy for a small project.

## Decision records

Offer an ADR only when all three conditions hold:

1. Reversing the decision would be costly or difficult.
2. The choice would surprise a future reader without its rationale.
3. There was a genuine tradeoff between plausible alternatives.

When accepted, use the project's ADR location and numbering convention. Otherwise use `docs/adr/NNNN-short-slug.md`, incrementing the largest existing number. Preserve earlier records; explain supersession rather than silently rewriting historical rationale.

```markdown
# 0001: Keep reservations owned by teams

Reservations remain attached to a team when a member leaves. Individual ownership would simplify personal notifications, but could orphan shared bookings during membership changes. Team ownership preserves continuity at the cost of explicit team-level permissions.
```

Include the decision, relevant context, and why it won. Add sections only when they make the reasoning easier to follow. Routine or readily reversible choices can stay in the session summary.
