# Konsierge Commit Conventions

Generates terse, action-led commit messages while preserving repository-specific conventions.

## What it does

The skill selects the first applicable format:

1. Contracts repository: `[PROJECT] <description>.`
2. Konsierge ticket branch: `KON-1234: Add: <description>.`
3. Other repository: `Add: <description>.`

It follows nearby repository history when that history defines a more specific convention. A body is added only when critical context cannot fit in the subject.

Outputs only the message. Does not stage, commit, or amend.

## How to invoke

Invoke `$konsierge-commit-conventions` or ask for a commit message.

## Example output

```text
KON-1234: Fix: payment status synchronization.
```

## See also

- [`SKILL.md`](./SKILL.md) — full LLM-facing instructions
- [`konsierge-git-flow`](../konsierge-git-flow/SKILL.md) — branch, delivery, and deployment workflow
