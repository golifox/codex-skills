---
name: interview-me
description: >
  Extract real intent before planning or coding. Use when a Rails/Ruby or product request is
  underspecified, conventional, ambiguous, or when the user says "interview me", "grill me",
  "stress-test my thinking", or asks to clarify what should be built.
---

# Interview Me

Use before specs, plans, or code when the requested outcome is not yet concrete.

## Goal

Find the gap between what the user asked for and what they actually need. Do this before Rails models, controllers, services, migrations, or tests exist, because changing intent after code is expensive.

## Process

1. State a one-sentence hypothesis and confidence percentage.
2. Ask one focused question at a time.
3. Attach your best guess to every question.
4. Listen for "should want" answers: scalable, clean, modern, dashboard, best practice.
5. Restate intent in the user's words.
6. Continue until the user explicitly confirms.

## Question Format

```text
HYPOTHESIS: You want a Rails workflow that lets admins approve refund requests without manual console work.
CONFIDENCE: ~45% - missing: actor, success criteria, and failure handling.

Q: Is the main user an internal support agent or the customer requesting the refund?
GUESS: internal support agent, because the request mentions approval and likely maps to an admin controller plus policy.
```

Ask only one question. Wait for the answer.

## Restate Format

```markdown
Here is what I now think you want:

- Outcome: support agents can approve or reject refund requests from the admin UI.
- User: internal support agents.
- Why now: console-driven refunds are slow and error-prone.
- Success: request spec proves approve/reject states, policy gates, audit row, and gateway payload.
- Constraint: do not change the customer-facing refund flow.
- Out of scope: automatic refund risk scoring.

Yes / no / refine?
```

## Stop Rule

Stop interviewing only when you can predict the user's reaction to the next three questions. If several rounds do not raise confidence, say what is missing and step back.

## Rails Handoff

After confirmation:

- Use `idea-refine` if the direction still has multiple possible shapes.
- Use `spec-driven-development` if the intent is concrete enough for acceptance criteria.
- Use `planning-and-task-breakdown` after the spec exists.
- Use `rails` whenever the result touches Ruby or Rails code.

## Verification

- Hypothesis and confidence were stated.
- Every low confidence estimate named what is missing.
- Questions were one at a time with guesses attached.
- Restate included outcome, user, why now, success, constraint, and out of scope.
- User gave an explicit yes before downstream work.
