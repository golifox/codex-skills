# Mappers

Mapper owns deterministic data conversion.

## Responsibilities

- Build external API payloads.
- Convert external response to local attributes/DTO.
- Normalize hashes/arrays.
- Build deterministic idempotency inputs if project uses mapper for that.
- Map local value objects/enums to provider-specific values.
- Build serializer/outbox payloads when payload is not a public API response.

## Allowed Inputs

- Model.
- Value object.
- Hash/DTO.
- Configuration snapshot.

## Forbidden

- Persistence.
- External API calls.
- Business state mutation.
- Time/randomness unless passed as explicit input.

## Good

```ruby
class BillingMapper
  def self.charge_payload(order)
    {
      order_id: order.id,
      amount_cents: order.total_cents,
      currency: order.currency
    }
  end
end
```

Provider payload:

```ruby
class Transaction::BankMapper
  def self.register_payload(transaction)
    {
      orderNumber: transaction.uid,
      amount: transaction.price_rate,
      currency: transaction.price.currency.iso_numeric,
      returnUrl: transaction.success_url
    }.compact_blank
  end
end
```

## Bad

```ruby
class BillingMapper
  def self.charge(order)
    payload = {amount: order.total_cents}
    ExternalBillingClient.charge(payload)
    order.update!(exported: true)
  end
end
```

## Checklist

- Pure/deterministic output.
- No side effects.
- Easy unit test.
- Complex payload not built in controller/service.
- Canonical ordering for hashes used in idempotency.
