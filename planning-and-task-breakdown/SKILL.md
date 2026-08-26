---
name: planning-and-task-breakdown
description: >
  Break specs or clear requirements into ordered implementation tasks. Use for Rails/Ruby work that
  is too large to start safely, touches multiple files or layers, needs sequencing, or could be
  parallelized across agents or sessions.
---

# Planning and Task Breakdown

Decompose work into small, verifiable Rails/Ruby tasks.

## Planning Rules

- Plan before editing code.
- Read the spec, local docs, and relevant source.
- Map Rails layer ownership with `rails`.
- Prefer vertical slices over horizontal layer dumps.
- Keep each task small enough for one focused session.
- Every task needs acceptance criteria and verification command.

## Rails Dependency Graph

```text
Migration/model state
    |
    +-> Policy and validation
    |
    +-> Service/mutator/query
            |
            +-> Controller/request endpoint
                    |
                    +-> Serializer/response contract
                            |
                            +-> Job/external boundary integration
```

Order tasks by dependency, but slice by user-visible behavior when possible.

## Task Template

```markdown
## Task [N]: [Short title]

**Description:** [What this task accomplishes.]

**Acceptance criteria:**
- [ ] [Specific behavior]
- [ ] [Specific behavior]

**Verification:**
- [ ] `bin/rspec spec/requests/admin/refunds/approve_spec.rb`
- [ ] `bin/rspec spec/services/refunds/approve_spec.rb`

**Rails layers touched:**
- Controller:
- Service:
- Mutator/model:
- Policy:
- Serializer:

**Dependencies:** [Task numbers or None]
**Estimated scope:** XS/S/M. Split if more than 5 files.
```

## Example Vertical Tasks

```markdown
### Phase 1: Approve payout
- [ ] Task 1: Add request spec for approved payout response and state transition.
- [ ] Task 2: Implement `Payouts::Approve.approve` and controller action.
- [ ] Task 3: Add policy coverage for forbidden approval attempts.

### Checkpoint
- [ ] `bin/rspec spec/requests/admin/payouts spec/services/payouts`

### Phase 2: External gateway sync
- [ ] Task 4: Add fake gateway manager and failure spec.
- [ ] Task 5: Send gateway payload outside DB transaction.
```

## Red Flags

- "Implement the feature" as one task.
- Task touches unrelated layers without one visible behavior.
- No verification command.
- Migration, external API change, and UI all mixed in one step.
- Plan ignores existing Rails patterns.

## Verification

- Every task has acceptance criteria.
- Every task has a command or concrete manual verification.
- Dependencies are ordered.
- No task is larger than about 5 files.
- Risky Rails boundaries are early.
- Human reviewed the plan before implementation when scope is substantial.
