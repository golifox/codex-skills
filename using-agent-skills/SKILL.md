---
name: using-agent-skills
description: >
  Select and sequence installed agent skills. Use at session start, when deciding which skill applies,
  or when orchestrating Rails/Ruby work across interview, idea refinement, spec, planning,
  incremental implementation, TDD, review, security, and the rails skill.
---

# Using Agent Skills

Use this meta-skill to pick the right workflow before acting.

## Rails Default

If the repository, files, or task use Ruby or Rails, always load `rails` first. Then add the phase-specific skill below.

## Skill Map

```text
Unclear intent                         -> interview-me
Rough idea, need options               -> idea-refine
Feature/change needs requirements      -> spec-driven-development
Spec exists, needs ordered tasks       -> planning-and-task-breakdown
Implementing multi-file/layer change   -> incremental-implementation + test-driven-development
Writing or changing behavior           -> test-driven-development
Security-sensitive boundary            -> security-and-hardening
Reviewing code                         -> code-review-and-quality
Rails or Ruby code anywhere            -> rails
```

## Typical Rails Lifecycle

1. `rails`: understand local architecture and layer rules.
2. `interview-me`: clarify intent if underspecified.
3. `idea-refine`: compare directions when the solution shape is unclear.
4. `spec-driven-development`: write requirements and acceptance criteria.
5. `planning-and-task-breakdown`: create small ordered tasks.
6. `incremental-implementation`: build one vertical slice at a time.
7. `test-driven-development`: write failing specs and verify behavior.
8. `security-and-hardening`: apply for auth, input, external APIs, PII, payments, uploads, webhooks, LLM output.
9. `code-review-and-quality`: review before final handoff or merge.

Not every task needs every skill. A small Rails bug fix often needs `rails`, `test-driven-development`, and `code-review-and-quality`.

## Operating Rules

- Check skill fit before editing.
- Skills are workflows, not suggestions.
- Multiple skills can apply; use the smallest set that covers the risk.
- Surface assumptions before non-trivial work.
- Stop and ask when requirements conflict.
- Verify with commands, not confidence.
- Do not modify unrelated code.

## Example

User: "Add refund approvals."

Use:

```text
rails
interview-me if actor/success is unclear
spec-driven-development
planning-and-task-breakdown
incremental-implementation
test-driven-development
security-and-hardening because money/admin action
code-review-and-quality
```

Expected Rails task shape:

```text
request spec -> route/controller -> policy -> Refunds::Approve.approve -> mutator/model -> gateway manager fake -> serializer
```

## Verification

- Correct skill sequence chosen.
- `rails` included for Ruby/Rails code.
- Security skill included for untrusted input, auth, PII, money, uploads, webhooks, or external integrations.
- TDD skill included for behavior changes.
- Review skill included before final handoff on substantial code changes.
