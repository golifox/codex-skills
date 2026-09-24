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
- For a bug or failing test whose cause is uncertain, use [hypothesis-driven-debugging](../hypothesis-driven-debugging/SKILL.md) before attempting a fix. Once the cause is supported, use the normal Rails implementation and regression-test workflow within the authorized scope.

## Ruby Interfaces and Layer Boundaries

- Do not use `private_class_method`. When a class needs private class methods, place its class-method API inside one `class << self` block: public methods first, then `private`, then private methods. Convert existing `def self.method` declarations in that class to this style when introducing private class methods.
- Use meaningful operation or result names instead of `.call` for application-owned services, queries, mappers, and value objects. Preserve `.call` where required by a library or framework interface.
- Prefer dependencies toward lower layers over peer-to-peer orchestration. In particular, do not chain mapper classes; shared deterministic concepts belong in a value object, and record-owned data or predicates may belong in the model. Do not move orchestration into models merely to avoid a service dependency.
- Keep a simple calculation or conditional selection used in one place in a named local variable next to its use, for example `refunded_amount_rate = case ... in ... else ... end`. Do not extract a private method just to name that value or shorten the caller. Inline single-use pass-through methods; remove their unused definitions after inlining. Extract a method only for reuse or a substantial, independently meaningful responsibility.
- Put business values, reference data, state groups, and business limits in `Store`. Put reusable type and format constraints in `Types`, implemented with dry-types; use constructor types when normalization or sanitization is part of the input type. Do not scatter these data constants or regular expressions through services, mappers, controllers, or models.
- When relocating constants, inspect every consumer and preserve validation, sanitization, inheritance, and loading behavior. A whole-string validation type does not replace substring redaction. Keep historical migrations self-contained rather than coupling them to the current `Store` or `Types`.

```ruby
class SomeService
  class << self
    def perform
      # Public operation
    end

    private

    def eligible?
      # Local predicate
    end
  end
end
```

## Minimal Workflow

1. Identify the exact artifact or behavior the user wants changed, generated, validated, or reviewed.
2. Inspect the local repository before acting.
3. Apply the smallest change or run the narrowest validation that satisfies the request.
4. Verify through the matching surface: tests, linter, CLI command, dry run, or generated artifact inspection.
5. Summarize the result, verification, and any skipped checks with the reason.

## Full Reference

Load `references/full-skill.md` when the short workflow is insufficient.
