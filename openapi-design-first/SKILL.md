---
name: openapi-design-first
description: Design, implement, migrate, or review OpenAPI contracts with a design-first workflow. Use for Rails API documentation, OpenAPI endpoints, contract validation, and preventing drift between an API description and runtime behavior.
---

# OpenAPI Design First

Treat the repository-owned OpenAPI description as the public interface contract. Write or amend it before changing behavior. In an existing application, first reconcile the intended contract with current routes, validators, serializers, tests, and consumers; do not silently change runtime behavior to match an assumed design.

## Rails Routing

For Rails work, use this skill with `rails` and the project's local instructions. Use `api-documentation` when prose documentation or a legacy `contracts/` tree is also in scope.

## Tool Choice

- Prefer an OpenAPI 3.1 YAML file as the canonical, reviewable artifact.
- Prefer `openapi_first` for parsing, request and response contract tests, and coverage in Ruby/Rails projects.
- Use `rswag` only when the user explicitly chooses test-generated, RSpec-owned documentation.
- Use `oas_rails` only when the user explicitly chooses controller and route introspection as the source.
- Evaluate `openapi-ruby` when a project explicitly wants Ruby component classes, generated specs, and validation from one toolkit. Do not introduce it merely to serve an existing YAML file.
- Do not combine multiple OpenAPI generators. One artifact must have one canonical owner.

## Workflow

1. Define scope precisely: included APIs, excluded UIs and engines, versioning, auth boundaries, and the required publication path.
2. Inventory current Rails routes and inspect controller schemas, serializers, response envelopes, existing JSON schemas, and request specs.
3. Write the OpenAPI contract with explicit path and query parameters, request bodies, response statuses, security requirements, deprecations, and reusable components.
4. Add route-coverage tests that compare the selected Rails route set with OpenAPI paths and methods in both directions.
5. Parse the document with an OpenAPI-aware library and lint it with a standards validator. Treat structural errors and inaccurate warnings as blocking; document intentional warnings.
6. Serve the same tracked artifact requested by tests and tooling. Protect documentation endpoints with an existing project auth pattern and keep credentials outside source control.
7. Verify missing, invalid, and valid authentication through real HTTP. Verify the response media type and representative contract content.

## Rails Compatibility Boundaries

- Do not enable request-validation middleware globally in an existing API without explicit authorization. Middleware can change status codes, error envelopes, parameter coercion, and whether undocumented routes are reachable.
- Preserve project-required validation such as dry-schema until a separate migration proves equivalent behavior.
- Start contract validation in tests. Expand to warn-only or runtime enforcement only after response schemas are precise and the current suite shows the impact.
- Do not publish to Bump.sh, create tokens, or change CI delivery without explicit scope.
- Never put Basic Auth credentials, tokens, examples containing PII, or production payloads in the OpenAPI file.

## Audience and Business Organization

- Define the documented route set by consumer audience. Exclude health checks, documentation endpoints, MCP transports, mounted operational UIs, and provider-facing APIs unless the requested contract explicitly includes them.
- When one explorer serves distinct audiences, expose separate definitions for those audiences (for example client including public routes, admin, and system). Keep API versions in the paths; do not create one definition per version.
- Keep the definitions derived from one application-owned contract or another deliberate single ownership model, not hand-maintained copies of the same schemas. Test that every selected operation belongs to exactly one definition and that excluded provider routes are absent from all definitions.
- Prefer tags for stable business capabilities such as profiles, services, payments, and order kinds. Keep API versions in paths, deprecation metadata, and compatibility notes instead of creating version-based UI sections.
- Add descriptions to declared tags and require every operation to use only a declared business tag. Test important domain assignments where path names can be misleading.
- Within each tag, present standard resource operations in the order index, show, create, update, destroy, then custom actions. Implement this with an explicit UI operation sorter or documented operation metadata; do not rely on YAML map insertion order.
- List intended servers explicitly with descriptions. Keep a safe current-host or local server first when `Try it out` must not default to production.

## Interactive Documentation UI

- Treat Swagger UI, Scalar, or another explorer as a presentation layer over the canonical OpenAPI artifact. It must not generate or become a second owner of the contract.
- In Rails, `rswag-ui` may be used by itself to serve bundled Swagger UI assets. Do not add `rswag-specs` or `rswag-api` merely to display an existing design-first document.
- Mount the UI at a predictable documentation route and configure it to read the same protected OpenAPI endpoint used by tests and tooling.
- Protect the HTML, JavaScript, CSS, and OpenAPI document with the same documentation access policy. Never place documentation credentials in a Swagger UI configuration object rendered into HTML. Inspect the chosen UI adapter: for `rswag-ui` 2.x, prefer an external Rack Basic Auth wrapper over `basic_auth_credentials`.
- Disable external validation for private specifications. Keep API requests same-origin unless the contract deliberately defines another server.
- Enable `Try it out` only when intended. Credentials for documentation access do not replace the API operation credentials described by the OpenAPI security schemes.
- A dynamic HMAC request signature cannot be derived from a client token alone. Never put a shared application signing secret in Swagger UI and never add a signing oracle backed by server configuration. Automatic signing is acceptable with an explicitly approved secret supplied by the caller, kept in a password field in browser memory, and submitted only to a same-origin helper that signs with that supplied value. Restrict the helper to intended API paths, filter secret and token parameters from logs, return `Cache-Control: no-store`, and prove canonicalization against the production signing library.
- Keep custom explorer controls visually subordinate to the upstream UI. Use a labeled password input, `autocomplete="off"`, an accessible text status, responsive layout, and no cookies, local storage, session storage, hidden HTML values, or Swagger authorization persistence for the signing secret.
- Treat the interactive documentation route as a UI surface, not a documented API operation, unless the product explicitly exposes it as an API.
- Verify unauthenticated and authenticated HTML and asset requests. In a real browser, confirm the document loads, filtering works, and a safe representative request can be prepared or executed without leaking credentials.

## Completion Evidence

- The OpenAPI parser accepts the document.
- The linter reports no errors.
- Selected Rails routes and OpenAPI operations match exactly.
- Request specs prove the documentation endpoint authentication boundary.
- A real HTTP request observes `401` without credentials and `200 application/json` with valid credentials.
- When an interactive UI is requested, a real browser renders it from the canonical document and its assets share the intended authentication boundary.
- Existing contract checks and the relevant Rails suite pass.

## Reusable Rails Integration

When extracting repeated serving, authentication, UI, route-coverage, or signing-adapter behavior into a Rails gem, read [references/rails-wrapper-gem.md](references/rails-wrapper-gem.md). Keep each application's OpenAPI document and business taxonomy application-owned.
