---
name: api-documentation
description: Write, reconcile, and review API documentation across OpenAPI files, endpoint guides, examples, and legacy JSON schema contracts. Use when documentation must match implementation without duplicating competing sources of truth.
---

# API Documentation

Write documentation for a consumer who must call the API correctly without reading application code. Separate observed current behavior from proposed behavior, and never present an intended contract as already shipped.

## Evidence Order

For an existing API, inspect evidence in this order:

1. Rails routes and mounted engines for reachability.
2. Controller validation, authentication, signatures, policies, and error handling.
3. Serializers and response helpers for output shape.
4. Request specs and real request traces for observable behavior.
5. Existing JSON schemas and prose documentation for additional intent and drift detection.

For a new design-first API, the approved OpenAPI document is the intended contract. Implementation and tests must converge on it before the behavior is called complete.

## Endpoint Documentation

Document each operation with:

- method and exact path;
- purpose and lifecycle effects;
- every auth mechanism and required header;
- path, query, header, and body fields with requiredness, types, formats, enums, defaults, and constraints;
- successful and meaningful error statuses using the real response envelope;
- idempotency, pagination, deprecation, webhook verification, and file media types where applicable;
- sanitized examples only when they clarify a non-obvious shape.

Prefer reusable schemas and parameters over copied field lists. Prose guides should explain workflows and business meaning, then link to the machine-readable contract instead of restating it.

Interactive API explorers are views of the machine-readable contract, not separate documentation sources. Configure them to load the canonical OpenAPI endpoint, preserve its access controls, avoid embedding credentials, and disable external validators for private specifications. Verify the rendered UI and a safe `Try it out` flow in a real browser. For HMAC authentication, never derive a signature from the public client token or expose a server-configured signing secret. If approved, use a separate password field whose caller-supplied secret stays in browser memory and a same-origin, no-store signing helper that uses only that supplied secret.

Organize interactive sections by stable business domain rather than API version. Define the documented audience explicitly and omit health, documentation, MCP, operational UI, and provider routes unless consumers of this contract are expected to call them.

## Existing Contract Trees

When a repository has a `contracts/` directory or another JSON-schema package, read [references/contracts.md](references/contracts.md) before deciding whether OpenAPI replaces, references, or coexists with it.

## Quality Gates

- Compare documentation paths and methods to the selected runtime route set in both directions.
- Validate OpenAPI and JSON Schema with format-aware tools.
- Run repository contract checks and affected request specs.
- Check relative references from the same location and packaging layout used in CI.
- Report remaining drift, incomplete schemas, and intentional legacy behavior explicitly.
- Never include credentials, tokens, PII, full production payloads, or internal stack traces.
