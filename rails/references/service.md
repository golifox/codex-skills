# Services

Service class is a container of named business actions. Each public class method is one business service function.

Service represents a business scenario, not a generic utility object.

## Public API

Do not use `.call` for services.

Use verbs and business names:

```ruby
PaymentService.create(order)
PaymentService.handle_callback(payload)
CallbackService.process(callback, force: true)
OrderService.complete(order)
```

`.call` is too generic: it hides the operation verb and forces readers to inspect the class.

## Responsibilities

- Orchestrate business pipeline.
- Coordinate mutators, managers, jobs, outbox, policies, queries, mappers, models.
- Enforce idempotency at workflow level.
- Trigger state transitions.
- Schedule async integration steps.
- Run compensation after partial side effects.
- Branch by provider/acquirer only when this service owns the business scenario; push payloads/calls into mappers/gateways/managers.

## Rules

- Public methods are named business steps.
- No `private` / `private_class_method` helpers for implementation detail.
- Do not build large external payload inline; use mapper/model payload.
- Do not hide domain branches inside generic helper.
- Duplicate between service actions is allowed until shared business concept is clear.
- Do not accept HTTP request/response objects; pass parsed Ruby data or domain objects.
- If a method name is not a business action, it probably does not belong in service layer.
- Prefer the project style: `SomeService.create/update/complete/process`, not one class per verb.
- It is acceptable for a service method to enqueue outbox after a persisted state transition.

## Good

```ruby
class OrderService
  def self.complete(order)
    OrderPolicy.ensure_completable!(order)
    order = OrderMutator.complete(order)
    OrderExportJob.perform_later(order)
    order
  end

  def self.completed(order)
    OrderMutator.completed(order)
    BalloonService.create(order)
  end
end
```

## Bad

```ruby
class OrderService
  def self.complete(order)
    payload = {id: order.id, lines: order.items.map { ... }}
    ExternalClient.post(payload)
    order.update!(status: 'completed')
  end

  private_class_method def self.payload(order); end
end
```

## Error Handling

- Preserve existing service errors.
- Convert external errors in manager, not in controller/mutator.
- If side effect A succeeds and B fails, call explicit compensation service/job.
- Do not swallow unknown errors.

## Service Shape

Prefer a small set of named methods on a domain service class:

```ruby
class PaymentService
  def self.create(order)
    payment = PaymentMutator.create(order)
    PaymentManager.create_transaction(payment)
    payment
  end

  def self.handle_callback(payload)
    callback = PaymentCallbackMapper.normalized_payload(payload)
    payment = PaymentService.resolve_callback_payment(callback)
    PaymentMutator.mark_paid(payment, callback:)
  end
end
```

Avoid object state unless the project standard needs it. Services are operations by nature; accidental instance state often makes retry/idempotency harder.

Provider-specific flow:

```ruby
class TransactionService
  def self.register(transaction)
    case transaction.acquirer
    in Store::ALFA_BANK
      Gateway::AlfaBank.register(transaction)
    in Store::GAZPROM_BANK
      Gateway::GazpromBank.register(transaction)
    else
      Rails.error.unexpected("Unknown acquirer: #{transaction.acquirer}", context: {transaction_id: transaction.id})
    end

    Transaction::Outbox.enqueue(transaction)
    transaction.reload
  end
end
```

## Checklist

- Method name is real business action.
- Each collaborator belongs to allowed lower layer.
- No private service helpers.
- Payload assembly delegated.
- Compensation/idempotency considered.
- No `.call` public API.
