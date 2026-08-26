# Managers

Manager owns external system boundary. It may know local domain models and external clients.

Gateway classes in a project can play the same role when they wrap one external provider flow.

## Responsibilities

- Call external API/client/library.
- Convert local payload into client call.
- Convert external errors to project-specific errors.
- Report/log external failures with context.
- Keep retry/backoff behavior if boundary owns it.
- Pass request correlation headers from `Current.external_http_headers` when local project uses it.

## Allowed Calls

- External API client.
- Mapper for payload/response conversion.
- Domain model/value object for needed data.

## Forbidden

- Controller response rendering.
- Mutating unrelated business state.
- Complex workflow orchestration.
- Inline large payload assembly when mapper exists.

## Good

```ruby
class BillingManager
  class Error < StandardError; end

  def self.create_charge(order)
    payload = BillingMapper.charge_payload(order)
    ExternalBillingClient.create_charge(payload)
  rescue ExternalBillingClient::Error => e
    ErrorReporter.report_once(e, context: {order_id: order.id})
    raise Error, e.message
  end
end
```

Gateway-style:

```ruby
class Gateway::Bank
  def self.register(transaction)
    payload = Transaction::BankMapper.register_payload(transaction)
    Konsierge::HTTP::Manager::Bank.register(payload, headers: Current.external_http_headers)
  rescue Konsierge::HTTP::Error => e
    raise Transaction::RegistrationError, e.message
  end
end
```

## Bad

```ruby
class OrdersController
  def create
    ExternalBillingClient.create_charge(...)
  end
end
```

## Checklist

- External call centralized.
- Error translation explicit.
- Context logged/reported.
- Payload mapping delegated.
- No controller/mutator direct external client.
