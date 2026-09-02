---
name: konsierge-commit-conventions
description: >
  Generate terse, exact commit messages for Konsierge, contracts, and other repositories.
  Use when the user asks for a commit message or when another workflow needs to name a commit.
---

Write commit messages terse and exact. No fluff. Why over what. Match project convention first.

This skill owns only commit-message content. For branch creation, staging, committing, merging, pushing, or deployment verification in a Konsierge repository, use [`konsierge-git-flow`](../konsierge-git-flow/SKILL.md).

## Format Priority

Apply the first matching rule:

1. `contracts` repository rule
2. Konsierge `KON-\d+` branch rule
3. Default action-based rule

## Contracts Repository Rule

If committing inside the `contracts` repository, usually a git submodule inside a project, use:

`[PROJECT_NAME] <description>.`

Rules:

- `PROJECT_NAME` is uppercase project/domain name used by the contracts repo convention.
- Examples: `[TRAVELMART]`, `[CRM]`, `[PAYMENT]`, `[KINO-AFISHA]`.
- Do not prepend `KON-\d+` in contracts commits.
- Keep description short and action-led.
- Prefer project git log convention over generic rules when examples exist.
- Use a trailing period when the repository convention does.

Examples:

```text
[TRAVELMART] Fix business lounges types.
[TRAVELMART] Add new fields to business_lounge_attributes schema.
[CRM] Add supplier full schema.
[PAYMENT] Remove gw_order_status and gw_payment_status. Add gw_status.
[KINO-AFISHA] Fix timezones and city pagination.
```

## Konsierge Branch Rule

If this is a Konsierge project and the current branch contains `KON-\d+`, prefix the commit with the extracted ticket id.

Extract only the `KON-\d+` part:

- Branch `KON-0000` -> prefix `KON-0000`
- Branch `KON-1234-dev` -> prefix `KON-1234`
- Branch `feature/KON-1234-dev` -> prefix `KON-1234`

Format:

`<KON_ID>: <GLOBAL_ACTION>: <description>.`

Examples:

```text
KON-0000: Add: global callbacks.
KON-1234: Fix: payment status sync.
KON-1234: Add: global callbacks. Refactor: legacy payment system. Remove: legacy fields from order.
```

## Default Rule

If the project is not Konsierge, or the branch does not contain `KON-\d+`, do not add a branch prefix.

Format:

`<GLOBAL_ACTION>: <description>.`

Examples:

```text
Add: global callbacks.
Fix: payment status sync.
Refactor: legacy payment system.
Add: global callbacks. Refactor: legacy payment system. Remove: legacy fields from order.
```

## Global Actions

Allowed actions:

- `Add`
- `Remove`
- `Fix`
- `Refactor`
- `Change`

Action meaning:

- `Add`: new behavior, field, endpoint, schema, test, config, or capability
- `Remove`: deleted behavior, field, dependency, config, or dead code
- `Fix`: bug fix, regression fix, broken behavior, failing test, bad edge case
- `Refactor`: internal restructure with same behavior
- `Change`: behavior changed, contract changed, naming changed, defaults changed

Rules:

- Use only the allowed action names.
- Capitalize actions exactly as listed.
- Use `Fix`, not `Fixed`, `Fixes`, or `Repair`.
- Use `Add`, not `Added`, `Adds`, or `Create`.
- Use `Remove`, not `Deleted`.
- Use `Change` when behavior or public shape changes but `Add`, `Remove`, `Fix`, and `Refactor` do not fit.
- If several global changes exist, list each as its own short sentence.

## Description Rules

Description is caveman-short:

- State the meaningful change, not every touched file.
- Do not list implementation bullets.
- Do not enumerate changed paths.
- Keep one compact phrase per action.
- Prefer domain words over file names.
- Mention exact entity/schema/status when useful.
- No filler.

Good:

```text
KON-1234: Add: restaurant pass orders schemas.
KON-1234: Fix: refund status mapping.
KON-1234: Refactor: payment callback parsing.
KON-1234: Remove: legacy order status fields.
KON-1234: Add: webhook idempotency. Fix: duplicate payment events.
```

Bad:

```text
KON-1234: Add: changed app/models/order.rb and app/services/payment_service.rb.
KON-1234: Fix: fixes.
KON-1234: Change: update stuff.
KON-1234: Added: new callback logic.
feat(payment): add callback parser
```

## Body

Default: no body.

Add a body only when subject cannot carry critical context:

- Breaking change
- Security fix
- Data migration
- Revert
- Operationally risky behavior
- Required manual deploy step

Body rules:

- Keep it short.
- Wrap at 72..128 chars.
- Bullets use `-`, not `*`.
- Explain why, risk, or migration step.
- Do not repeat the subject.

Example:

```text
KON-1234: Change: payment status source.

BREAKING CHANGE: clients must read `gw_status`; legacy gateway status
fields are removed from order contracts.
```

## What Never Goes In

Drop:

- "This commit does X"
- "I", "we", "now", "currently"
- "As requested by..."
- "Generated with Claude Code" or any AI attribution
- Emoji
- File-by-file change lists
- Long explanations of obvious diff content
- Conventional Commit prefixes unless the project explicitly requires them

## Selection Rules

Before writing:

- Identify whether the repo is `contracts`.
- Identify whether this is a Konsierge project.
- Read the current branch when available.
- Extract `KON-\d+` from the branch when applicable.
- Infer the smallest accurate set of global actions from the diff.
- Follow nearby git log convention when it conflicts with generic style.

If unsure:

- Use `Change` for broad behavior updates.
- Use no `KON-\d+` prefix unless both Konsierge project and branch match are clear.
- For contracts, ask or infer `PROJECT_NAME` from surrounding paths, schemas, or recent git log.

## Auto-Clarity

Never compress away critical context for:

- Breaking changes
- Security fixes
- Data migrations
- Reverts
- Manual deployment steps

Use a short body for those cases, then stop.

## Boundaries

Only generates the commit message. Does not run `git commit`, stage files, amend commits, or inspect secrets unless explicitly asked.

Output the message as a code block ready to paste.

"stop caveman-commit" or "normal mode": revert to verbose commit style.
