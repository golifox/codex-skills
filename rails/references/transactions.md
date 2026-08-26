# Transactions / Idempotency

Transactions own DB consistency. External side effects stay outside.

Database is part of the architecture. Use it deliberately for data consistency and performance.

## Transaction Rules

- Use transaction for multi-row local state changes.
- Use lock when concurrent updates can race.
- Keep transaction block small.
- Never call external API inside DB transaction.
- Do not enqueue jobs before commit unless framework guarantees after-commit behavior.
- Outbox rows may be created inside the same DB transaction when delivery intent must be atomic with state change; actual external delivery stays in the poller/handler.
- Prefer database constraints/indexes for invariants that must hold across every code path.
- Keep business scenarios out of triggers/procedures unless the project explicitly owns that architecture.

## Good

```ruby
Order.transaction do
  order.lock!
  OrderMutator.reserve!(order)
  InventoryMutator.decrement!(order.items)
  Order::Outbox.enqueue(order)
end
```

## Bad

```ruby
Order.transaction do
  order.update!(status: 'reserved')
  ExternalProvider.reserve(order) # external IO inside transaction
end
```

## Compensation

If external side effect succeeds and later step fails:

- record enough local state to detect partial success;
- call explicit compensation service/job;
- keep retry idempotent;
- report failure with context.

## Idempotency

- Inputs must be canonical and deterministic.
- Exclude runtime ids, generated ids, `created_at`, `updated_at`, and unordered hashes.
- Use persisted external ids to detect duplicate work.
- Add tests proving same business input gives same key/result.

## Checklist

- Lock/transaction around local race.
- External IO after commit.
- Compensation path exists.
- Idempotency stable.
- DB constraint/backing index exists for critical uniqueness/foreign-key invariants.
