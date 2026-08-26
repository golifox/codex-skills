---
name: incremental-implementation
description: >
  Deliver Rails/Ruby changes in small verified slices. Use when implementing any feature, refactor,
  or behavior change that touches more than one file, more than one Rails layer, or feels too large
  to land safely in one edit.
---

# Incremental Implementation

Build one working slice at a time. Each slice leaves the app runnable and testable.

## Increment Cycle

```text
Choose slice -> write/adjust spec -> implement -> run focused test -> review -> next slice
```

## Rails Slicing

Prefer vertical slices:

1. Request spec for visible behavior.
2. Minimal controller route/action.
3. Service or query/mutator with named public method.
4. Policy/serializer/model changes only as needed.
5. External manager fake and payload assertion.

Avoid horizontal batches like "all models", then "all controllers", then "all tests".

## Rules

- Touch only files required by the slice.
- Keep implementation boring and local.
- Do not introduce abstraction before the concept has a clear Rails layer and name.
- Do not call external APIs inside DB transactions.
- Preserve response shape unless the spec says otherwise.
- Use feature flags or disabled paths for incomplete user-visible work.
- Run the focused command after each meaningful edit.

## Example Slice

```text
Slice: admin approves refund

1. Add failing request spec:
   `bin/rspec spec/requests/admin/refunds/approve_spec.rb`
2. Add route and controller action.
3. Add `Refunds::Approve.approve(refund:, actor:)`.
4. Add policy check and audit row.
5. Fake gateway manager and assert payload.
6. Run focused request spec, then related service spec.
```

## Scope Discipline

Do not:

- Clean up adjacent files.
- Rename unrelated methods.
- Remove comments you do not understand.
- Add "nice to have" behavior.
- Split or move code just to reduce line count.

When you notice unrelated work, mention it as follow-up, not part of the slice.

## Verification

- Slice implements one behavior.
- Focused specs pass.
- Related crossed-layer specs pass.
- No new skipped tests.
- No unrelated files changed.
- Remaining slices are clearly named.
