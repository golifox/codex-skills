---
name: spec-driven-development
description: >
  Create a specification before coding. Use when starting a Rails/Ruby feature, bug fix, refactor,
  integration, migration, or significant change without concrete requirements, acceptance criteria,
  commands, test strategy, and boundaries.
---

# Spec-Driven Development

Write a small spec before code. The spec is the shared contract for what will change and how it will be verified.

## Gated Workflow

```text
SPECIFY -> PLAN -> TASKS -> IMPLEMENT
   |        |       |          |
 review   review  review     verify
```

Do not advance when requirements, boundaries, or success criteria are still unclear.

## Specify

Start by surfacing assumptions:

```text
ASSUMPTIONS:
1. This is a Rails API change, not a UI change.
2. Authorization uses existing policy classes.
3. The visible contract is the JSON response and persisted state.
Correct me now or I will proceed with these.
```

Write a spec covering:

1. Objective: what changes, for whom, and why.
2. Rails shape: controller, service, mutator/model, policy, query, serializer, job, manager.
3. Commands: exact project commands.
4. Test strategy: request/service/model/job specs and external fakes.
5. Boundaries: always, ask first, never.
6. Success criteria: testable outcomes.

## Rails Spec Template

```markdown
# Spec: [Feature]

## Objective
[What user-visible behavior changes and why.]

## Rails Shape
- Entry point: `POST /admin/refunds/:id/approve`
- Controller: validates params and renders response.
- Service: `Refunds::Approve.approve(...)` orchestrates.
- Mutator/model: persists state transition.
- Policy: gates admin permission.
- Manager: calls external gateway outside DB transaction.
- Serializer: preserves response shape.

## Commands
- Focused test: `bin/rspec spec/requests/admin/refunds/approve_spec.rb`
- Related service test: `bin/rspec spec/services/refunds/approve_spec.rb`
- Full relevant suite: `bin/rspec spec/requests/admin/refunds spec/services/refunds`

## Testing Strategy
- Request spec proves auth, params, response, persistence, job/gateway boundary.
- Unit/service specs only for hard-to-reach branching.
- WebMock/fake manager for external gateway.

## Boundaries
- Always: preserve existing response contract, validate params, check policy.
- Ask first: schema changes, dependency additions, gateway contract changes.
- Never: call external gateway inside DB transaction, skip regression spec.

## Success Criteria
- [ ] Approve happy path changes status and records audit.
- [ ] Forbidden users receive 403.
- [ ] Gateway failure leaves consistent state and reports error.

## Open Questions
- [Question]
```

## Implementation Handoff

After the spec is accepted:

- Use `planning-and-task-breakdown` to create ordered tasks.
- Use `incremental-implementation` to build vertical slices.
- Use `test-driven-development` and `rails` for tests and layer choices.

## Verification

- Spec has objective, Rails shape, commands, tests, boundaries, success criteria.
- Acceptance criteria are specific and testable.
- External contracts and data changes are explicit.
- Human reviewed the spec before implementation.
