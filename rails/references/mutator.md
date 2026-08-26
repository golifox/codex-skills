# Mutators

Mutator owns model state changes. It is explicit replacement for callback-heavy mutation.

Use mutator when `create/update/destroy/save` is not enough to leave local models in a correct state.

## Responsibilities

- Create/update/destroy model state.
- Persist derived fields.
- Run DB transaction for local consistency.
- Use value objects/models for calculations needed for persistence.
- Keep small state updates explicit.
- Assign local ids/defaults and build required associated records.
- Normalize persisted error/metadata attributes.

## Allowed Calls

- Model.
- Value object.
- State-machine event when mutating status.
- Other mutator only when ownership is clear and local.

## Forbidden

- External API / manager / HTTP / queue / storage.
- HTTP response behavior.
- Building external payloads.
- Long workflow orchestration.

## Good

```ruby
class OrderMutator
  def self.complete(order, now: Time.current)
    Order.transaction do
      order.completed_at = now
      order.to_completed! if order.may_to_completed?
      order.save!
      order.reload
    end
  end
end
```

## Bad

```ruby
class OrderMutator
  def self.complete(order)
    order.update!(status: 'completed')
    ExternalGateway.notify(order) # manager/service responsibility
  end
end
```

## Checklist

- Only local state changes.
- Transaction used for multi-write mutation.
- No external boundary.
- State-machine events used when available.
- Return mutated model only when useful locally.

## When To Extract

Extract a mutator when mutation requires:

- creating/updating associated records;
- derived fields persisted together;
- assigning generated ids/default associations;
- normalizing provider errors into persisted columns;
- canceling/replacing previous local state;
- recalculating counters;
- replacing callback chains with explicit ordered code;
- local transaction/lock around several writes.

Do not extract a mutator just to wrap `Model.create!(attrs)`.
