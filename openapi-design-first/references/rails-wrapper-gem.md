# Rails OpenAPI Wrapper Gem

Use a wrapper gem to remove integration boilerplate, not to take ownership of an application's API contract.

## Gem Responsibilities

- Provide a Rails Engine or mountable Rack application for the configured JSON and interactive UI routes.
- Load and parse an application-owned OpenAPI YAML file with `openapi_first`.
- Serve embedded Swagger UI assets without requiring `rswag-specs` or `rswag-api`.
- Accept a callable credentials provider and protect the document, HTML, JavaScript, and CSS with one timing-safe authentication boundary.
- Provide RSpec helpers that compare a configurable Rails route scope with OpenAPI paths and methods in both directions.
- Expose configuration for document path, UI title, server defaults, route inclusion/exclusion, and optional UI settings.
- Keep external validation disabled by default for private contracts.

## Application Responsibilities

- Own the OpenAPI YAML, business tags, operation descriptions, schemas, servers, and audience decisions.
- Own credentials and secrets. The gem must receive them lazily and must never serialize them into HTML or configuration JSON.
- Define which routes are public consumer API, internal API, provider API, MCP, health, frontend, or operational UI.
- Decide whether runtime request/response validation is enabled. Default the gem to test-only parsing and route coverage.

## Signing Boundary

Do not offer automatic HMAC signing from `X-Client-Token` alone: a client token is input to the signature, not the secret key.

- Default: describe the signature scheme and leave `X-Request-Sign` caller-supplied.
- Never ship a shared application signing secret to browser code.
- Never expose an endpoint that signs with a secret loaded from application configuration. That creates a signing oracle even when the documentation route itself uses Basic Auth.
- An optional same-origin signing helper is acceptable when it requires the caller to supply the secret on every request and signs only with that supplied value. Restrict target paths, authenticate it like the rest of the documentation UI, filter secret and token parameters from logs, return `Cache-Control: no-store`, and never echo the secret.
- Keep the caller secret in a password input in browser memory only. Do not persist it through Swagger authorization state, cookies, local storage, or session storage. Prove canonicalization against fixtures from the production signing library.
- The helper should add `X-Request-Sign` through Swagger UI's request interceptor after reading `X-Client-Token`; it must fail closed when a secret is present but the client token is absent.

## Suggested Configuration Surface

Keep the public API small and callable-based where values may vary by environment:

```ruby
Konsierge::Openapi.configure do |config|
  config.document_path = Rails.root.join('docs/openapi.yml')
  config.credentials = -> { BasicAuthConfig.to_h.deep_symbolize_keys.fetch(:system) }
  config.route_filter = ->(route) { route.path.start_with?('/api/') }
  config.ui_options = {
    filter: true,
    tryItOutEnabled: true,
    validatorUrl: nil
  }
  config.signature = {
    enabled: true,
    allowed_path: %r{\A/api/client(?:/|\z)},
    signer: ->(secret, token) { Konsierge::Signature::Signers::Http.new(secret, token) }
  }
end
```

Prefer generator-installed request specs or shared matchers over generation of the OpenAPI document. The design-first artifact remains the source of truth.
