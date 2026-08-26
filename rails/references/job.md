# Jobs

Job owns async/retry boundary. It should be thin.

Job is an internal inbound layer: it starts a unit of work from queue/time/event, similar to how controller starts one from HTTP.

For durable external delivery with persisted attempts, prefer the outbox layer: [outbox.md](outbox.md).

## Responsibilities

- Wrap service/manager call asynchronously.
- Run delayed expiration/cancel/resend.
- Retry a small integration step when no outbox exists.
- Report failures with context.
- Define execution context for background work.

## Rules

- Reload record when important state can be stale.
- Use state-machine `may_*?` guards when safe transition expected.
- Keep business decisions in service/policy.
- Do not duplicate business flow from service.
- Make job idempotent when retries possible.
- Call named service methods, not `.call`.

## Good

```ruby
class OrderExportJob < ApplicationJob
  def perform(order)
    order.reload
    OrderService.export(order)
  end
end
```

## Bad

```ruby
class OrderExportJob < ApplicationJob
  def perform(order)
    return unless order.user.allowed?
    order.update!(status: 'exporting')
    ExternalClient.post(...)
    order.update!(status: 'exported')
  end
end
```

## Execution Context

Jobs do not have request/session context. Pass or load everything explicitly:

- record id or persisted event id;
- actor id if the operation needs one;
- config snapshot if behavior must not depend on current config;
- idempotency key/external id when retrying integration work.

Do not read controller/global state from job bodies.

## Checklist

- Thin wrapper.
- Idempotent/retry safe.
- Reloads stale records.
- No second business implementation.
- Error reporting explicit.
- No `.call` public API.
