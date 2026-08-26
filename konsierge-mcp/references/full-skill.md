---
name: konsierge-mcp
description: Use when building, reviewing, documenting, or upgrading the reusable `konsierge-mcp` Ruby/Rails gem or Rails MCP producer apps for `konsierge-ai-rails`, especially `/mcp`, `/mcp/digest`, Rails::Engine integration, NameError fixes after `Konsierge::Mcp::ActiveRecord::*` or `Konsierge::Mcp::Rails::*` constant removal, tool metadata, `_meta.availability` service rules, `_meta.confirmation`, prepare/confirm flows, idempotency keys, confirmation TTL/locking/state machines, DB metadata, generators, and MCP tool sync contracts.
---

# Konsierge MCP

Use this skill for two related jobs:

- implementing or reviewing the reusable `konsierge-mcp` gem;
- implementing Rails MCP producer apps that expose tools consumed by `konsierge-ai-rails`.

Keep the boundary strict:

- MCP producer/gem owns domain validation, tool metadata, server manifest, digest, and authoritative confirmations.
- `konsierge-ai-rails` owns AI runtime, chat confirmation UX, hidden context argument injection, tool sync, and tariff expansion.
- Real side effects happen only in `confirm_*`, never in `prepare_*`.

## Gem Architecture

Use public namespace `Konsierge::Mcp`.

Use a `Rails::Engine` for Rails integration. Keep Rails-specific controllers, concerns, and ActiveRecord models under the gem's `app/` tree so Zeitwerk exposes the public `Konsierge::Mcp` constants directly.

Follow Konsierge gem conventions from `konsierge-http` and `konsierge-signature`: `Config`, generator structure, and Zeitwerk entrypoint.

Use `promocodes` only as behavior reference for MCP runtime; do not move its domain code into the gem.

Core dependencies:

```ruby
spec.add_dependency 'activesupport', '>= 4.0'
spec.add_dependency 'anyway_config', '>= 2.0'
spec.add_dependency 'mcp', '>= 0.20.0'
spec.add_dependency 'oj', '>= 3.0'
spec.add_dependency 'zeitwerk', '~> 2.0'
spec.add_dependency 'konsierge-logger', '>= 0.1.0'
spec.add_dependency 'konsierge-idempotency', '>= 0.1.0'
spec.add_dependency 'aasm', '>= 5.0'
spec.add_dependency 'activerecord', '>= 6.1'
spec.add_dependency 'actionpack', '>= 6.1'
spec.add_dependency 'railties', '>= 6.1'
```

Use GitLab sources for internal Konsierge gems while developing locally, matching existing Konsierge gem conventions.

## Rails Integration

The engine auto-adds routes to the host app router through its initializer. Keep the same HTTP surface:

```ruby
match '/mcp', to: 'mcp#handle', via: %i[get post delete]
get '/mcp/digest', to: 'mcp/digest#show'
```

Do not generate host app controllers for `/mcp` or `/mcp/digest`; the engine owns its controllers and internal concerns.

Public concern constants do not include the old `Rails::` namespace. Use `Konsierge::Mcp::Authentication`, `Konsierge::Mcp::Whitelist`, `Konsierge::Mcp::Handler`, and `Konsierge::Mcp::DigestHandler` only when direct references are unavoidable.

Authentication and whitelist concerns must read config at request time. Do not use `http_basic_authenticate_with` in generated controllers because it reads values at class load time.

`Authentication` returns `401` when credentials are missing or wrong. `Whitelist` returns `403` when the whitelist is blank or `request.remote_ip` is not allowed.

Handler uses streamable HTTP transport:

```ruby
transport = MCP::Server::Transports::StreamableHTTPTransport.new(
  Konsierge::Mcp::Server.build,
  stateless: true
)
status, headers, body = transport.handle_request(request)
render json: body.first, status:, headers:
```

Digest handler returns:

```ruby
render json: {digest: Konsierge::Mcp::Server::Digest.call}
```

## Configuration

`Konsierge::Mcp.config` is backed by `Anyway::Config`.

```ruby
module Konsierge
  module Mcp
    class Config < Anyway::Config
      config_name :konsierge_mcp
      env_prefix 'KONSIERGE_MCP'

      attr_config :name,
                  :title,
                  :version,
                  :instructions,
                  :logger,
                  :availability_resolver,
                  basic_auth: {},
                  whitelist_ips: [],
                  tools: [],
                  log_level: ::Logger::INFO,
                  logging_enabled: true

      coerce_types whitelist_ips: {type: :string, array: true},
                   logging_enabled: :boolean
    end
  end
end
```

Resolve callable values at runtime for:

- `instructions`
- `basic_auth`
- `whitelist_ips`
- `tools`
- `availability_resolver`

Host app initializer example:

```ruby
Konsierge::Mcp.configure do |config|
  config.name = 'promocodes_client_requests'
  config.title = 'Promocodes Client Requests'
  config.version = '1.0.0'
  config.instructions = -> { Konsierge::Mcp::ServerConfig.current&.instructions }
  config.basic_auth = {
    name: ENV.fetch('KONSIERGE_MCP_BASIC_AUTH_NAME'),
    password: ENV.fetch('KONSIERGE_MCP_BASIC_AUTH_PASSWORD')
  }
  config.whitelist_ips = ENV.fetch('KONSIERGE_MCP_WHITELIST_IPS', '').split(',')
  config.availability_resolver = ->(tool_name) { Configuration.availability_for_tool(tool_name) }
  config.tools = [
    Mcp::Tools::AvailablePartnersTool,
    Mcp::Tools::PrepareAssignableRequestTool,
    Mcp::Tools::ConfirmAssignableRequestTool
  ]
end
```

## Upgrade From Pre-Engine Versions

The move to `app/` and `Rails::Engine` renamed public constants only. Runtime behavior, HTTP contract, routes, configuration API, database tables, migrations, statuses, basic auth, whitelist, `/mcp`, and `/mcp/digest` are unchanged.

Breaking constant renames:

| Old | New |
| --- | --- |
| `Konsierge::Mcp::ActiveRecord::Confirmation` | `Konsierge::Mcp::Confirmation` |
| `Konsierge::Mcp::ActiveRecord::ServerConfig` | `Konsierge::Mcp::ServerConfig` |
| `Konsierge::Mcp::ActiveRecord::ToolDefinition` | `Konsierge::Mcp::ToolDefinition` |
| `Konsierge::Mcp::Rails::Authentication` | `Konsierge::Mcp::Authentication` |
| `Konsierge::Mcp::Rails::Whitelist` | `Konsierge::Mcp::Whitelist` |
| `Konsierge::Mcp::Rails::Handler` | `Konsierge::Mcp::Handler` |
| `Konsierge::Mcp::Rails::DigestHandler` | `Konsierge::Mcp::DigestHandler` |

Host app upgrade steps:

```bash
bundle update konsierge-mcp
rg 'Konsierge::Mcp::ActiveRecord::|Konsierge::Mcp::Rails::' app lib config
```

Replace old constants by the table above. The common initializer fix is:

```ruby
# old
config.instructions = -> { Konsierge::Mcp::ActiveRecord::ServerConfig.current&.instructions }

# new
config.instructions = -> { Konsierge::Mcp::ServerConfig.current&.instructions }
```

If tests raise `NameError: uninitialized constant Konsierge::Mcp::ActiveRecord::...`, a direct old constant reference remains. For clean installs, run only:

```bash
rails g konsierge:mcp:install
rails db:migrate
```

## Manifest And Digest

Use one canonical manifest for server construction and digest.

Manifest shape:

```ruby
{
  server: {
    name: 'promocodes_client_requests',
    title: 'Promocodes Client Requests',
    version: '1.0.0',
    instructions: '...'
  },
  tools: [
    {
      name: 'available_partners',
      description: '...',
      inputSchema: {},
      outputSchema: {},
      annotations: {},
      _meta: {}
    }
  ]
}
```

Rules:

- resolve callable server values before building manifest;
- sort tools by `name`;
- normalize nested hash key order recursively before digest;
- merge enabled DB metadata rows into tool hashes when names match;
- DB metadata may override display/sync metadata, but not executable Ruby class;
- build a fresh `MCP::Server` per request; do not memoize without digest invalidation.

Digest must be exactly:

```ruby
Konsierge::Idempotency.key(Konsierge::Mcp::Server::Manifest.build)
```

Do not add a SHA256 fallback.

Specs must prove digest changes when server instructions, tool description, schemas, annotations, `_meta.confirmation`, or `_meta.availability` change.

## Tool Base

Host app tools inherit from `Konsierge::Mcp::Tool < MCP::Tool`.

`Tool.to_h` must:

- remove `$schema` and `:$schema` from input/output schemas;
- preserve static `.tool_meta`;
- preserve `_meta.confirmation`;
- add `_meta.availability` from `config.availability_resolver`;
- merge enabled `mcp_tool_definitions` metadata when the table and row exist.

Availability resolver contract:

```ruby
config.availability_resolver = lambda do |tool_name|
  [{service_key: 'q_gpbank', tariff_keys: ['gpb_card']}]
end
```

Output contract:

```ruby
_meta: {
  availability: [
    {service_key: 'q_gpbank', tariff_keys: ['gpb_card']}
  ]
}
```

Only emit availability when the resolver returns an array with usable rules. A usable rule has `service_key` and non-empty `tariff_keys`. Keep only `service_key` and `tariff_keys`; drop all other rule keys.

Wildcard semantics are consumer-owned:

- `service_key: '*'` unlocks all services;
- `tariff_keys` containing `'*'` unlocks all tariffs for the service;
- emit wildcards verbatim.

`konsierge-ai-rails` ignores rules without `service_key` or with empty `tariff_keys`.

## Result Protocol

Success:

```ruby
Konsierge::Mcp::Result.success(structured_content = {})
```

Behavior:

```ruby
MCP::Tool::Response.new(
  [{type: 'text', text: Oj.dump(structured_content)}],
  structured_content: structured_content
)
```

Do not add `success: true` to successful structured content.

Failure:

```ruby
Konsierge::Mcp::Result.failure(message:, error_key: :unknown, status: 400)
Konsierge::Mcp::Result.error(...)
```

Structured content:

```ruby
{
  success: false,
  error_message: message,
  error_key: error_key.to_s,
  status: status
}
```

Mark the response with `error: true`; this becomes `isError: true` in MCP JSON-RPC output.

## Service Base

`Konsierge::Mcp::Service` exposes `prepare` and `confirm`. Do not use generic `.call` for confirmation services.

```ruby
def self.prepare(...)
  raise NotImplementedError, "#{name}.prepare must be implemented"
end

def self.confirm(...)
  raise NotImplementedError, "#{name}.confirm must be implemented"
end

def self.success_result(payload = {})
  Konsierge::Mcp::Result.success(payload)
end

def self.error_result(message, error_key = :unknown, status = 400)
  Konsierge::Mcp::Result.failure(message:, error_key:, status:)
end
```

## Confirmation Flow

Use prepare/confirm for any operation that creates, sends, pays, cancels, assigns, changes state, calls an external provider with consequences, or depends on text a human must approve.

Contract:

```text
prepare_* -> returns confirmation.idempotency_key
confirm_* -> accepts idempotency_key only
```

`prepare_*` receives business arguments, validates them, stores payload, and returns useful structured confirmation data. It must not perform the irreversible action.

`confirm_*` accepts no business arguments beyond `idempotency_key`; it loads stored payload, re-checks current domain conditions, and performs the side effect under lock.

Confirmation metadata:

```ruby
_meta: {
  confirmation: {
    tool_name: 'confirm_item_request',
    arguments_mapping: {
      idempotency_key: {
        source: 'result',
        path: 'confirmation.idempotency_key'
      }
    },
    expires_at_mapping: {
      source: 'result',
      path: 'confirmation.expires_at'
    }
  }
}
```

The MCP producer returns structured data. `konsierge-ai-rails` builds the final chat text and hides technical fields from the user.

Do not expose technical fields in user-facing text: `idempotency_key`, `client_token`, raw ids, `customer_id`, `payload`, `status`, MCP/tool names, or JSON.

## Confirmation Persistence

Use `Konsierge::Mcp::Confirmation`.

Table name:

```ruby
self.table_name = 'mcp_confirmations'
```

Migration columns:

```ruby
create_table :mcp_confirmations do |t|
  t.string :idempotency_key, null: false
  t.references :actor, polymorphic: true
  t.string :confirmation_type, null: false
  t.string :confirmation_action, null: false
  t.jsonb :payload, null: false, default: {}
  t.string :status, null: false, default: 'awaiting'
  t.integer :lock_version, null: false, default: 0
  t.datetime :expires_at, null: false
  t.datetime :approved_at
  t.datetime :declined_at
  t.datetime :cancelled_at
  t.datetime :processing_at
  t.datetime :confirmed_at
  t.datetime :processing_error_at
  t.datetime :expired_at
  t.timestamps
end

add_index :mcp_confirmations, :idempotency_key, unique: true
add_index :mcp_confirmations, :status
add_index :mcp_confirmations, :expires_at
add_index :mcp_confirmations, %i[confirmation_type confirmation_action]
```

Use AASM. Required lifecycle:

```text
awaiting -> cancelled
awaiting -> declined
awaiting -> expired
awaiting -> processing
processing -> confirmed
processing -> processing_error
```

Terminal statuses:

- `cancelled`
- `confirmed`
- `declined`
- `processing_error`
- `expired`

Terminal statuses must reject further transitions.

## Confirmation Manager

`Konsierge::Mcp::ConfirmationManager.prepare` creates the confirmation with a new idempotency key, actor, type, action, payload, and TTL.

`Konsierge::Mcp::ConfirmationManager.confirm(idempotency_key, confirmation_type:)` must:

- find by `idempotency_key` and `confirmation_type`;
- return `confirmation_not_found` with `404` if absent;
- lock the row with `with_lock`;
- expire awaiting rows after TTL and return `confirmation_expired` with `410`;
- return `confirmation_not_awaiting` with `409` for non-awaiting rows;
- move `awaiting -> processing` before the domain block;
- yield the confirmation to the host app domain block;
- move successful domain result to `confirmed`;
- move failed domain result to `processing_error`;
- attach confirmation to successful domain result.

Host apps supply only domain behavior:

```ruby
Konsierge::Mcp::ConfirmationManager.confirm(idempotency_key, confirmation_type: 'Assignment') do |confirmation|
  payload = confirmation.payload.symbolize_keys
  AssignableService.create(...)
end
```

Always re-check current domain conditions inside confirm before side effects.

## DB Metadata

First version includes:

- `mcp_server_configs`
- `mcp_tool_definitions`

Do not add `mcp_tool_availabilities` in the first version.

Class declarations are valid without DB rows. DB metadata overrides class metadata only when rows exist and are enabled.

`Konsierge::Mcp::ServerConfig`:

- table: `mcp_server_configs`;
- `current` returns enabled row with `key = 'default'`;
- blank/missing rows must not break the gem.

`Konsierge::Mcp::ToolDefinition`:

- table: `mcp_tool_definitions`;
- enabled row is found by `name`;
- validate uniqueness of `name`;
- validate JSON columns are hashes;
- may override description, input schema, output schema, annotations, and metadata;
- never changes which Ruby class executes a tool call.

## Generators

Install generator command:

```bash
rails g konsierge:mcp:install
```

Creates:

- `config/initializers/konsierge/mcp.rb`
- migration for `mcp_confirmations`, `mcp_server_configs`, `mcp_tool_definitions`

Routes and controllers are provided by the engine; do not create host controllers during clean install.

Tool generator command:

```bash
rails g konsierge:mcp:tool prepare_assignable_request
```

Generated file:

```text
app/services/mcp/tools/prepare_assignable_request_tool.rb
```

Generated class inherits `Konsierge::Mcp::Tool`. Keep `_tool` suffix.

Service generator command:

```bash
rails g konsierge:mcp:service assignment_confirmation
```

Generated file:

```text
app/services/mcp/assignment_confirmation_service.rb
```

Generated class inherits `Konsierge::Mcp::Service`.

## Consumer Setup

In `konsierge-ai-rails`, create only the server record manually:

```ruby
McpServer.create!(
  key: 'example_app',
  name: 'Example App',
  endpoint_url: 'https://example-app.internal/mcp',
  auth_type: 'bearer',
  auth_token: Rails.application.credentials.dig(:mcp, :example_app_token),
  enabled: true,
  routing_description: 'Use for item requests available to the customer tariff.'
)
```

Write `routing_description` as business routing text, not protocol text.

Do not fill `instructions` manually. `konsierge-ai-rails` pulls instructions from MCP `initialize` during sync and stores them.

Run sync:

```ruby
server = McpServer.find_by!(key: 'example_app')
Mcp::ToolsSyncService.sync(server_ids: [server.id])
```

Sync stores tools, creates `McpToolConfig` for matching availability service rules, copies confirmation metadata, and disables tools missing from the remote server.

Deployment order: producer apps using `konsierge-mcp` must be deployed before or together with the `konsierge-ai-rails` consumer because legacy non-array `_meta.availability` is treated as empty availability.

## Implementation Order

For the gem, implement in this order:

1. Gem skeleton and Zeitwerk loader.
2. Config and runtime callable resolution.
3. Rails::Engine, routes, controllers, and concerns under `app/`.
4. Result protocol.
5. Tool base and availability metadata.
6. Server manifest and digest.
7. ActiveRecord models exposed as `Konsierge::Mcp::Confirmation`, `ServerConfig`, and `ToolDefinition`.
8. Confirmation manager.
9. MCP request specs for `tools/list`, `tools/call`, and `/mcp/digest`.
10. Install, tool, and service generators.
11. README and migration guide.
12. Full verification.

Focused verification commands:

```bash
bundle exec ruby -e "require 'konsierge-mcp'; puts Konsierge::Mcp::VERSION"
bundle exec rspec spec/konsierge/mcp/config_spec.rb
bundle exec rspec spec/requests/konsierge/mcp/auth_spec.rb
bundle exec rspec spec/konsierge/mcp/result_spec.rb
bundle exec rspec spec/konsierge/mcp/tool_spec.rb
bundle exec rspec spec/konsierge/mcp/server
bundle exec rspec spec/konsierge/mcp/active_record
bundle exec rspec spec/konsierge/mcp/confirmation_manager_spec.rb
bundle exec rspec spec/requests/konsierge/mcp
bundle exec rspec spec/generators/konsierge/mcp
```

Final verification:

```bash
bundle exec rspec
bundle exec rubocop
bundle exec rake
```

## Readiness Checklist

Before considering a gem or integration ready, verify:

- `/mcp` is authenticated and IP-guarded.
- `/mcp/digest` is deterministic.
- `Server.build` and digest use the same manifest.
- `$schema` is removed from schemas.
- `tools/list` output is consumed by `konsierge-ai-rails`.
- `_meta.availability` is an array of `{service_key, tariff_keys}` rules.
- `_meta.confirmation` maps prepare result to confirm `idempotency_key`.
- `Result.success(hash)` returns raw structured content.
- `Result.failure(...)` produces `isError: true`.
- Dangerous actions use prepare/confirm.
- Confirmation manager owns lock, TTL, and terminal states.
- Engine auto-adds `/mcp` and `/mcp/digest`; clean installs do not generate host controllers.
- Public constants use `Konsierge::Mcp::*`, not `Konsierge::Mcp::ActiveRecord::*` or `Konsierge::Mcp::Rails::*`.
- `McpServer.routing_description` is business-specific.
- `Mcp::ToolsSyncService.sync(server_ids: [server.id])` is run after server creation.

## Out Of Scope For First Version

- Domain logic from `promocodes`.
- `mcp_tool_availabilities`.
- Admin UI for DB metadata editing.
- Multiple independent MCP servers mounted in one host app.
