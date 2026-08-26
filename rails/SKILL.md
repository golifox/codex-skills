---
name: rails
description: >
  Rails and Ruby coding skill for AI agents. Use whenever the codebase or task uses Rails or Ruby:
  architecture and layer ownership, services, mutators, managers, mappers, policies, queries,
  serializers, jobs, transactions, naming, RSpec TDD, FactoryBot, integration-first tests,
  external boundary fakes, contracts/schemas, i18n, and verification workflow.
---

# Rails

This is a compressed entrypoint. The previous full guide is preserved at `references/full-skill.md`.

## Operating Rules

- Use this skill only when the frontmatter description matches the user's task.
- Start from the user's repository and current files; prefer local project conventions over generic examples.
- Keep the active context small. Do not read `references/full-skill.md` by default.
- Read `references/full-skill.md` only when the task needs the original detailed checklist, templates, command matrix, or domain-specific edge cases.
- If the skill has `scripts/`, prefer running the relevant script over recreating its logic by hand.
- If the skill has `references/` besides `full-skill.md`, load only the reference that matches the current tool, framework, provider, or failure mode.
- For Rails OpenAPI creation, migration, validation, or serving, load and follow `openapi-design-first`.
- For Rails interactive API documentation, keep the contract design-first and add only a presentation UI as described by `openapi-design-first`; do not switch the contract owner to generated rswag specs.
- When Rails API work also changes prose documentation or an existing `contracts/` schema tree, load and follow `api-documentation`.
- Preserve user-owned worktree changes. Report blocked validation honestly instead of pretending a tool ran.

## Minimal Workflow

1. Identify the exact artifact or behavior the user wants changed, generated, validated, or reviewed.
2. Inspect the local repository before acting.
3. Apply the smallest change or run the narrowest validation that satisfies the request.
4. Verify through the matching surface: tests, linter, CLI command, dry run, or generated artifact inspection.
5. Summarize the result, verification, and any skipped checks with the reason.

## Full Reference

Load `references/full-skill.md` when the short workflow is insufficient.
