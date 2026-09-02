---
name: code-review
description: Use when reviewing a branch, pull request, commit range, worktree diff, or Rails/Ruby change for correctness, specification compliance, architecture, security, performance, and test quality.
---

# Code Review

Review findings first. Separate required defects from optional improvements. Never rubber-stamp.

## Establish Scope

1. Resolve the user-supplied fixed point. If absent, infer the safest merge-base from branch/upstream evidence; ask only when ambiguity changes the reviewed diff.
2. Capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`. Include staged or unstaged changes when the user asks for worktree review.
3. Locate the originating issue, specification, acceptance criteria, and repository standards. Report missing sources instead of inventing them.
4. Preserve dirty work. Review is read-only unless the user separately requests fixes.

## Review Axes

### Correctness and Specification

- Public behavior matches requirements and existing contracts.
- Edge cases, failure paths, transactions, retries, ordering, and idempotency are correct.
- No missing requirement, partial implementation, or unrequested behavior.

### Architecture and Maintainability

- Repository conventions override generic preferences.
- Names expose intent; control flow stays simple; duplication represents a real shared concept before extraction.
- Flag likely code smells as judgment calls, not automatic violations.

For Rails, check layer ownership from `rails`: controllers map HTTP, services orchestrate, mutators/models persist, managers own external calls, mappers build payloads, policies authorize, serializers format output, and queries own reads. External calls must not extend database transactions.

### Security and Performance

- Authentication, authorization, input validation, secret handling, injection, SSRF, and sensitive logging are safe.
- No N+1 queries, unbounded reads, missing pagination, oversized transactions, or duplicate job workflows.

### Tests

- Tests prove visible behavior and regressions, not private implementation.
- External boundaries are faked; internal domain collaborators are not over-stubbed.
- Verification commands are relevant and their actual result is reported.

## Findings Contract

Order findings by severity:

- Critical: security, data loss, unsafe deploy, or broken public behavior.
- Important: likely bug, missing regression coverage, architecture violation, or material performance risk.
- Nit: optional readability improvement.

Every actionable finding includes:

```text
[Severity] Short title
File and line: exact location
Evidence: observed behavior or diff
Impact: concrete failure mode
Fix: smallest safe correction
```

Do not report style enforced by existing tooling. Do not inflate speculative concerns. If there are no findings, say so and state residual verification risk.

## Verification

- Fixed point and reviewed paths are explicit.
- Findings cite exact files and lines.
- Specification gaps and code-quality findings remain distinguishable.
- Commands run and skipped checks are named.
- Review performs no mutation without explicit authorization.
