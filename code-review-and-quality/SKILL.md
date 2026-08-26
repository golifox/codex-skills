---
name: code-review-and-quality
description: >
  Review Rails/Ruby changes for correctness, readability, architecture, security, performance, and
  tests. Use before merging, after agent-generated code, after refactors or bug fixes, and whenever
  code quality needs a senior review.
---

# Code Review and Quality

Review findings first, ordered by severity. Do not rubber-stamp.

## Five Axes

1. Correctness: behavior matches spec, edge cases, failure paths, transactions, idempotency.
2. Readability: names, small methods, simple control flow, no cleverness.
3. Rails architecture: correct layer ownership from `rails`, no dependency direction violations.
4. Security: auth, authorization, input validation, secrets, injection, unsafe external data.
5. Performance: N+1 queries, unbounded reads, missing pagination, slow jobs, transaction scope.

## Review Order

1. Read spec/task and changed tests.
2. Review public behavior before private implementation.
3. Check Rails layers:
   - Controller validates params and maps HTTP.
   - Service orchestrates with named public method.
   - Mutator/model persists state.
   - Manager owns external API call.
   - Mapper builds payloads.
   - Policy gates access.
   - Serializer formats output.
4. Check tests prove behavior, not internals.
5. Check verification commands and output.

## Rails Findings Examples

```text
Critical: `RefundsController#approve` calls the payment gateway inside the DB transaction.
If the gateway times out, the row lock stays open and can block refund processing. Move the
gateway call to a manager outside the transaction and persist an outbox/event first.
```

```text
Important: The request spec stubs `Refunds::Approve.approve`, so it can pass while the
real approval flow is broken. Exercise the native service path and stub only the gateway
boundary with WebMock or a fake manager.
```

```text
Nit: `data` can be `refund_payload` here; the current name makes the mapper harder to scan.
```

## Severity

- Critical: security, data loss, broken public behavior, unsafe deploy.
- Important: likely bug, missing regression test, layer violation, performance issue.
- Nit: optional style/readability improvement.
- FYI: context only.

## Review Checklist

```markdown
### Correctness
- [ ] Behavior matches spec/task.
- [ ] Edge and error paths covered.
- [ ] Transaction and retry behavior safe.

### Tests
- [ ] Request/service/model/job specs cover visible behavior.
- [ ] External boundaries are faked, internals are not over-stubbed.
- [ ] Bug fixes include regression spec.

### Rails Architecture
- [ ] Layer ownership follows `rails`.
- [ ] No external API inside transaction.
- [ ] No `.call` public API for business services/queries.

### Security
- [ ] Params validated.
- [ ] Auth and policy checks present.
- [ ] No secrets or sensitive logs.

### Performance
- [ ] No N+1 queries.
- [ ] Lists are scoped and paginated.
- [ ] Jobs do not duplicate business workflows.
```

## Verification

- Findings include file/line references when reviewing actual code.
- Required issues are separated from optional suggestions.
- Tests/commands run are named.
- If no issues, say that and mention residual test risk.
