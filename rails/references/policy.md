# Policies / Scenarios

Policy owns deterministic gate. Scenario/checker owns blockers around existing state.

## Policy Responsibilities

- Authorization.
- Business gate.
- Configuration validity.
- Enabled/disabled checks.
- Raising/returning explicit domain errors.

## Scenario Responsibilities

- Post-draft or state-specific blockers.
- First blocker selection.
- Checks based on persisted model/config state.

## Forbidden

- Persistence mutation.
- External writes.
- External API calls.
- HTTP rendering.
- Hidden updates while checking.

## Good

```ruby
class OrderPolicy
  def self.ensure_creatable!(user, config)
    raise DisabledError unless config.enabled?
    raise ForbiddenError unless user.allowed?
  end
end
```

## Bad

```ruby
class OrderPolicy
  def self.ensure_creatable!(order)
    order.update!(checked_at: Time.current)
    ExternalAuditClient.track(order)
  end
end
```

## Checklist

- Reads only.
- Error type communicates business reason.
- Misconfiguration not hidden as ordinary validation.
- Uses effective persisted state, not stale/global defaults.
