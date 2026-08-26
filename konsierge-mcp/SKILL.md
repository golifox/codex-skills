---
name: konsierge-mcp
description: Use when building, reviewing, documenting, or upgrading the reusable `konsierge-mcp` Ruby/Rails gem or Rails MCP producer apps for `konsierge-ai-rails`, especially `/mcp`, `/mcp/digest`, Rails::Engine integration, NameError fixes after `Konsierge::Mcp::ActiveRecord::*` or `Konsierge::Mcp::Rails::*` constant removal, tool metadata, `_meta.availability` service rules, `_meta.confirmation`, prepare/confirm flows, idempotency keys, confirmation TTL/locking/state machines, DB metadata, generators, and MCP tool sync contracts.
---

# Konsierge Mcp

This is a compressed entrypoint. The previous full guide is preserved at `references/full-skill.md`.

## Operating Rules

- Use this skill only when the frontmatter description matches the user's task.
- Start from the user's repository and current files; prefer local project conventions over generic examples.
- Keep the active context small. Do not read `references/full-skill.md` by default.
- Read `references/full-skill.md` only when the task needs the original detailed checklist, templates, command matrix, or domain-specific edge cases.
- If the skill has `scripts/`, prefer running the relevant script over recreating its logic by hand.
- If the skill has `references/` besides `full-skill.md`, load only the reference that matches the current tool, framework, provider, or failure mode.
- Preserve user-owned worktree changes. Report blocked validation honestly instead of pretending a tool ran.

## Minimal Workflow

1. Identify the exact artifact or behavior the user wants changed, generated, validated, or reviewed.
2. Inspect the local repository before acting.
3. Apply the smallest change or run the narrowest validation that satisfies the request.
4. Verify through the matching surface: tests, linter, CLI command, dry run, or generated artifact inspection.
5. Summarize the result, verification, and any skipped checks with the reason.

## Full Reference

Load `references/full-skill.md` when the short workflow is insufficient.
