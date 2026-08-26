# Configuration / Infrastructure

Configuration owns typed access to settings. Infrastructure owns low-level providers and framework integrations.

Use Anyway Config as the default configuration abstraction.

## Configuration Responsibility

- Encapsulate settings from ENV/YAML/credentials/database.
- Validate required values.
- Coerce types.
- Provide domain-friendly methods.
- Hide provider/source details from upper layers.

## Anyway Config Pattern

Base class:

```ruby
class ApplicationConfig < Anyway::Config
  class << self
    delegate_missing_to :instance

    private

    def instance
      @instance ||= new
    end
  end
end
```

Concrete config:

```ruby
class PaymentsConfig < ApplicationConfig
  config_name :payments

  attr_config enabled: false,
              timeout_seconds: 5,
              callback_url: nil

  required :callback_url
  coerce_types enabled: :boolean, timeout_seconds: :integer
end
```

Usage:

```ruby
PaymentService.create(order, config: PaymentsConfig)
PaymentManager.create_transaction(order, timeout: PaymentsConfig.timeout_seconds)
```

## Rules

- Do not scatter `ENV.fetch`, credentials, YAML parsing, or feature flags across controllers/services/models.
- Treat config providers as infrastructure details.
- Prefer `ApplicationConfig < Anyway::Config` with explicit `config_name`, `attr_config`, `required`, and coercions.
- Pass config into lower objects when it affects behavior.
- Snapshot config on persisted workflows when later changes must not alter old orders/tasks/events.
- Do not read infrastructure config from models.

## Bad

```ruby
class Order < ApplicationRecord
  def paid_by_external_provider?
    ENV["PAYMENTS_ENABLED"] == "1" && Rails.application.credentials.payments[:provider] == "x"
  end
end
```

The model now knows infrastructure and deployment details.

## Infrastructure Responsibility

- Low-level clients.
- Storage, queue, cache, mail, websocket providers.
- Logging, monitoring, instrumentation adapters.
- Framework-level configuration.

Application layers should depend on stable adapters/managers/config objects, not provider libraries directly.

## Database As Layer

Use database-level abstractions for:

- uniqueness and foreign-key invariants;
- indexes and performance;
- immutable audit/data middleware;
- constraints that protect data regardless of application path.

Avoid putting business scenarios into database triggers/procedures unless the project has explicitly chosen that architecture.

## Checklist

- Can caller use config without knowing the source?
- Are required values validated early?
- Are types coerced once?
- Does domain code avoid `ENV`/credentials/provider constants?
- Are old persisted workflows protected from mutable config where needed?
- Is Anyway Config used unless project has a stronger local convention?
