---
name: idea-refine
description: >
  Refine vague ideas into sharp, buildable concepts. Use when a Rails/Ruby feature idea is still
  broad, when multiple product directions are possible, or when the user asks to ideate, refine an
  idea, compare options, or stress-test a plan before writing a spec.
---

# Idea Refine

Use after intent is roughly known and before committing to a spec or implementation.

## Workflow

1. Restate the idea as a "How might we..." problem.
2. Ask 3-5 sharpening questions if user, success, or constraints are missing.
3. Generate 5-8 meaningfully different directions.
4. Cluster the strongest directions into 2-3 options.
5. Stress-test each option for user value, Rails feasibility, risk, and scope.
6. Produce a one-page recommendation after the user chooses a direction.

## Rails Lenses

Use these lenses when ideating inside a Rails/Ruby codebase:

- Can this be a thin vertical slice through controller, service, mutator, serializer, and request spec?
- Does the concept require a new model, or can existing state support it?
- Is this orchestration, mutation, query, policy, mapper, manager, or presentation?
- Can the MVP avoid external API calls inside transactions?
- Which behavior is visible enough to prove with a request spec?
- What should remain out of scope to avoid premature abstractions?

## Example Variations

For "add approvals for payouts":

- Admin-only approval queue with `Payouts::Approve` service and request specs.
- Policy-gated state machine event on `Payout`, with audit rows.
- Background review job that flags risky payouts, but humans still approve.
- Read-only dashboard first, approval action later.
- CSV export for finance instead of building a workflow UI.

## One-Pager Template

```markdown
# [Idea Name]

## Problem Statement
[How might we help specific user achieve specific outcome?]

## Recommended Direction
[Chosen option and why it is the simplest useful Rails slice.]

## Rails Shape
- Controller/API:
- Service:
- Mutator/model:
- Policy:
- Query/serializer:
- External boundary:

## Key Assumptions to Validate
- [ ] [Assumption] - [how to test or learn]

## MVP Scope
[Smallest version that proves value.]

## Not Doing
- [Thing] - [reason]

## Open Questions
- [Question]
```

Save to `docs/ideas/[idea-name].md` only after user confirmation.

## Verification

- Target user and success criteria are named.
- Multiple directions were explored.
- Hidden assumptions and kill risks are explicit.
- Recommendation maps to Rails layer concepts from `rails`.
- Not Doing list is present.
- User confirmed direction before spec or code.
