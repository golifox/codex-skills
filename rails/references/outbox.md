# Outbox

Outbox owns durable delivery of external side effects.

Use outbox when an integration side effect must survive process crashes, be retried, store attempts, preserve idempotency, or run in ordered groups.

## Responsibilities

- Persist external delivery intent.
- Store request method/url/body/headers/query params.
- Store idempotency key, grouping/order, retry settings, wait time, and status.
- Run handlers before/after attempts.
- Record attempts and final errors.
- Call local mutators/services after delivery result.

## Ownership

Service decides that a side effect should be delivered.

Outbox stores and delivers it.

Handler reacts to delivery lifecycle.

Manager still owns external API client abstraction when delivery is not raw HTTP or when payload/error translation is domain-specific.

## Pattern

```ruby
class Notification::Outbox
  def self.enqueue(notification, wait: nil)
    Konsierge::Outbox.enqueue(
      event_type:      'notification.deliver',
      entity:          notification,
      http_method:     :post,
      url:             NotificationsConfig.delivery_url,
      body:            NotificationSerializer.as_hash(notification, view: :webhook),
      headers:         notification.callback_headers,
      handler_classes: [Notification::OutboxHandler],
      max_attempts:    5,
      wait:
    )
  end
end
```

```ruby
class Notification::OutboxHandler < Konsierge::Outbox::Handler
  def before_attempt(context)
    context.outbox.reload
    context.outbox.entity.reload
  end

  def after_success(context)
    NotificationMutator.delivered(context.outbox.entity)
  end

  def after_final_failure(context)
    reason = context.outbox.last_error || context.error
    NotificationMutator.failed(context.outbox.entity, reason.to_s)
  end
end
```

## Rules

- Do not put core business scenario decisions into outbox handlers.
- Do not enqueue outbox rows before local state is valid.
- Use mapper/config objects for body/url/headers when construction is non-trivial.
- Serializer views are acceptable for webhook/outbox bodies when payload equals public contract.
- Keep handlers idempotent: retries and repeated callbacks must not corrupt local state.
- Store enough context to debug failed attempts.
- Use grouping when multiple delivery events must be ordered.
- Do not use outbox for cheap local async work; use job.
- Configure defaults in `config/initializers/konsierge/outbox.rb`.
- Ensure `Outbox::PollerJob` is scheduled when the project uses recurring polling.

## Outbox vs Job

Use job when:

- work is local;
- retry state does not need a domain-visible audit trail;
- enqueueing a service method is enough.

Use outbox when:

- external delivery needs persisted status/attempts;
- idempotency key matters;
- delivery order matters;
- final failure must update domain state;
- request body/headers/status/error must be auditable.

## Checklist

- Enqueue point is explicit service/integration step.
- Body/headers/url are deterministic.
- Idempotency key/grouping chosen when needed.
- Handler only reacts to delivery lifecycle.
- Final failure path updates local state or reports error.
- Tests run poller/handler path, not only enqueue.
