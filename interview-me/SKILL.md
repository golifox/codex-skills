---
name: interview-me
description: Clarify an underspecified Rails/Ruby or product request before planning or coding. Use when intent or acceptance criteria are ambiguous, or the user asks for an interview, grilling, or a challenge to their assumptions.
---

# Interview Me

Identify the desired outcome, who needs it, why it matters, constraints, and
observable acceptance criteria. Read project facts before asking about them.

## Process

1. State a short working interpretation and name the material unknowns.
2. Group independent questions into a short round, usually two or three. Give a
   recommended answer and reason for each; make assumptions explicit.
3. Wait for prerequisite answers before asking dependent questions. If only one
   decision blocks progress, ask that question alone.
4. Replace vague goals such as "scalable" or "modern" with concrete scenarios,
   expected results, limits, and failure behavior.
5. Restate the outcome and decisions using the user's terms. Preserve answers
   and authorization already given; do not ask the same thing in another form.

## Example Round

```text
Working interpretation: support agents need to approve refunds without console access.
Missing decisions: who may approve and whether partial refunds are in scope.

1. Who may approve: all support agents or supervisors?
   Recommendation: supervisors, because this operation changes customer funds.
2. Should this first version support partial refunds?
   Recommendation: full refunds only, if that covers the current support cases.
```

An unanswered recommendation remains a proposal. Do not implement a materially
different product or permission model on the assumption that silence accepts it.
Continue independent, authorized investigation while waiting.

## Stop and Handoff

Stop when the outcome, scope, constraints, and acceptance criteria are concrete
enough to act. Ask for confirmation only of material decisions the user has not
resolved or actions beyond existing authorization. A clear request to implement,
together with resolved decisions, is sufficient; no ritual final "yes" is needed.
If the user asked only for an interview or design, finish with the resulting brief.

Summarize the outcome, intended user, success criteria, constraints, out-of-scope
work, and any remaining questions. Use a file when the work needs to survive a
session boundary; otherwise keep the brief in the conversation.

- Use [brainstorming](../brainstorming/SKILL.md) when clarified intent still leaves
  consequential design alternatives. Carry the brief forward without repeating
  the interview.
- Use [incremental-implementation](../incremental-implementation/SKILL.md) for a
  Rails/Ruby change spanning several layers.
- Use [orchestrating-agent-work](../orchestrating-agent-work/SKILL.md) for work
  requiring coordination or durable continuation.
- Use [rails](../rails/SKILL.md) for Ruby/Rails implementation.

## Verification

- Questions concern material unknowns that project evidence cannot answer.
- Independent questions are grouped; dependent questions follow their answers.
- Recommendations are distinguishable from confirmed decisions.
- The brief supplies acceptance criteria and preserves scope and authorization.
