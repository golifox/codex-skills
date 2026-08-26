# Existing JSON Schema Contracts

Do not assume an OpenAPI file makes an existing `contracts/` tree obsolete. Contract files may be packaged as a shared gem, loaded by response validators, or used by services outside the current repository.

## Inventory Before Editing

- List schema files and inspect their declared dialect, relative references, custom keywords, and response envelope conventions.
- Search the application, tests, build scripts, submodules, and adjacent packages for every contract loader and path reference.
- Run the repository's existing contract check before changing ownership.
- Record which schemas describe public API responses, external provider payloads, CRM messages, webhooks, or internal events. OpenAPI should not absorb unrelated message contracts.

## Choose One Ownership Model

Use one of these models explicitly:

1. OpenAPI owns public HTTP schemas. Legacy contract files remain temporarily for existing consumers and are generated or migrated from OpenAPI.
2. Standalone JSON Schema owns reusable data shapes. OpenAPI 3.1 references or bundles those schemas, provided every consumer supports the dialect and reference layout.
3. Coexistence by boundary. OpenAPI owns HTTP operations and public request and response shapes; `contracts/` owns non-HTTP messages and external integration schemas.

Avoid permanent hand-maintained copies of the same object in both locations. If temporary duplication is unavoidable, add a deterministic comparison or generation check.

## Safe Migration

1. Map each documented operation to its current request and response schema files.
2. Normalize incompatible keywords and dialect differences deliberately. Do not blindly copy Draft 4 or custom keywords into OpenAPI 3.1.
3. Make relative references resolvable from the artifact location used by CI and consumers.
4. Add validation against representative success and error responses.
5. Migrate one schema family at a time and keep compatibility until all known consumers move.
6. Delete a legacy contract only after source search finds no consumers and contract checks, request specs, packaging checks, and the full relevant suite pass.

## Rails Repositories

Keep controller dry-schema as the runtime request gate unless migration is explicitly requested. OpenAPI and JSON Schema validation may begin in tests without changing client-visible errors. When runtime validation is proposed, compare status codes, coercion, unknown-field handling, content types, and the application's established error envelope first.
