---
name: rails
description: >
  Rails and Ruby coding skill for AI agents. Use whenever the codebase or task uses Rails or Ruby:
  architecture and layer ownership, services, mutators, managers, mappers, policies, queries,
  serializers, jobs, transactions, naming, RSpec TDD, FactoryBot, integration-first tests,
  external boundary fakes, contracts/schemas, i18n, and verification workflow.
---

# Rails

Use whenever code or project uses Rails or Ruby. For non-Rails Ruby, apply Ruby/RSpec testing and pure object guidance; skip Rails-specific layers when not applicable.

## First Rules

- Read local project docs first: `AGENTS.md`, `CLAUDE.md`, `README.md`, architecture docs.
- If business rule or layer ownership unclear, ask. Do not invent behavior silently.
- Preserve dirty worktree. Do not revert unrelated edits.
- Use `rg` / `rg --files`.
- Keep changes inside correct layer. Do not break boundaries just to reduce line count.
- Prefer existing project patterns over new architecture.

## Layered Design Principles

From layered Rails architecture practice:

- Rails starts with few abstractions; mature applications add layers gradually as business complexity grows.
- A good layer has one owner responsibility, a small public interface, no circular/reverse dependency, non-leaky internals, and can be tested directly.
- Use semantic abstractions: names should match the business/application concept, not the implementation trick.
- Keep each method at one abstraction level. Do not mix HTTP params, SQL details, external clients, and domain decisions in one function.
- Separate application logic from business logic: request/input/view concerns live above domain rules.
- Callbacks and conditional validations are warning signs when they hide business scenarios or context-specific behavior.
- Do not fight Rails by default; extend Rails with explicit layers only when the existing model/controller/view split is too cramped.
- Abstractions have cost. Add one when it reduces real churn, coupling, duplication of concepts, or cross-layer leakage.
- Do not use `.call` as the public API for business services, queries, filters, or value objects. The method name must say what happens.

## Dependency Direction

Allowed:

```text
Controller -> Job / Service / Query / Serializer / Policy
Service    -> Mutator / Job / Outbox / Manager / Mapper / ValueObject / Model / Policy / Query
Mutator    -> Model / ValueObject
Manager    -> ExternalAPI / Mapper / DomainModel / ValueObject
Mapper     -> Model / ValueObject / Hash / DTO
Model      -> Concern / Presenter / Repository / StateMachine / ValueObject
Job        -> Service / Mutator / Model / Mapper / ValueObject / Manager
Outbox     -> Handler / Manager / Mapper / Mutator / Model / ExternalAPI
Policy     -> Model / Configuration / ValueObject
Query      -> Model / Repository / SQL
Serializer -> Model / Presenter / ValueObject / Blueprinter view
```

Forbidden:

- Controller directly calls external API client.
- Mutator calls external API, manager, HTTP, queue, or storage provider.
- Mapper/serializer/presenter mutates business state.
- Policy persists, mutates, or performs external writes.
- Job becomes second implementation of business flow.
- Outbox handler decides core business scenario instead of delivering persisted side effect.
- Low-level layer knows about HTTP response, status code, controller params, or render shape.
- Model owns workflow orchestration that belongs to service/business layer.

## Layer Decision

```text
HTTP params/response?      -> Controller
HTTP params validation?    -> Controller schema(...)
Response serialization?    -> render_response + Blueprinter serializer/view
Business pipeline step?    -> Service with named class method
Persist model state?       -> Mutator / Model
External API call?         -> Manager
Build payload/DTO?         -> Mapper
Read/filter/search?        -> Query / Repository / Scope with named class method
Context model behavior?    -> Shape / Form object
User-driven filters?       -> Filter object / Query
Application config?        -> AnywayConfig object / ValueObject
Business gate?             -> Policy / Scenario
Async/retry/delay?         -> Job / Outbox handler
API output shape?          -> Blueprinter serializer view
View/read formatting?      -> Presenter
State transition?          -> StateMachine event
Pure calculation?          -> initialized ValueObject / PORO
Multi-row consistency?     -> Transaction / lock
New shared concept?        -> Abstraction rule check
```

## Detailed References

Load only file needed for current change:

- Foundation principles: [references/foundation.md](references/foundation.md)
- Controllers: [references/controller.md](references/controller.md)
- Services: [references/service.md](references/service.md)
- Mutators: [references/mutator.md](references/mutator.md)
- Managers: [references/manager.md](references/manager.md)
- Mappers: [references/mapper.md](references/mapper.md)
- Policies / scenarios: [references/policy.md](references/policy.md)
- Jobs / async wrappers: [references/job.md](references/job.md)
- Outbox / durable integration delivery: [references/outbox.md](references/outbox.md)
- Models: [references/model.md](references/model.md)
- Presenters / serializers: [references/presenter_serializer.md](references/presenter_serializer.md)
- Queries / repositories: [references/query_repository.md](references/query_repository.md)
- State machines: [references/state_machine.md](references/state_machine.md)
- Value objects / POROs: [references/value_object.md](references/value_object.md)
- Shapes / context-specific model behavior: [references/shape.md](references/shape.md)
- Forms / filters / user input: [references/form_filter.md](references/form_filter.md)
- Configuration / infrastructure: [references/configuration.md](references/configuration.md)
- Gemfile / common gems: [references/gems.md](references/gems.md)
- Transactions / idempotency: [references/transactions.md](references/transactions.md)
- Abstractions / naming / workflow: [references/abstractions.md](references/abstractions.md)
- Testing coverage / smells / done checklist: [references/testing-checklists.md](references/testing-checklists.md)
- RSpec / FactoryBot / shared examples: [references/testing-examples.md](references/testing-examples.md)

## Global Coding Rules

- Methods with side effects: verbs; do not return meaningful business result.
- Value-returning methods: nouns/noun phrases describing returned data.
- Do not expose `.call` for business services, queries, filters, or value objects. It hides the operation name and makes code read worse.
- Prefer named class methods for service/query/mutator/mapper APIs: `PaymentService.create(...)`, `CallbackService.process(...)`, `PersonaServiceQuery.index(...)`.
- Prefer initialized value objects for calculations: `PriceCalculation.new(order).total`, not class-level generic execution methods.
- Controllers validate params with dry-rails `schema(:action)` in the controller and consume `safe_params`.
- API responses use konsierge-response `render_response` with Blueprinter serializers and explicit `view:` when response shape differs.
- Configuration uses Anyway Config through `ApplicationConfig < Anyway::Config` unless local project docs say otherwise.
- Rails `create/update/destroy` keep normal Rails semantics.
- Jobs: `Context::ActionJob`, not `ActionContextJob`.
- Temporary legacy alias allowed only with explicit `TODO:` removal note.
- Prefer temporary duplication to wrong abstraction.
- Extract only when concept has clear layer and name.
- Never call external API inside DB transaction.
- Preserve response shape and external contracts unless task explicitly changes them.
- Add integration-first tests for visible behavior; unit specs only for hard-to-reach pure logic.
- Let database constraints protect data invariants when appropriate, but keep business scenarios in application/domain code.
- Keep hidden global/current state out of models and low-level layers.

## Testing / TDD

Use TDD style for Ruby/Rails code:

1. **Red**: smallest failing spec for behavior/regression.
2. **Green**: minimal implementation.
3. **Refactor**: improve while green.
4. **Verify**: focused specs, then request/job/integration specs for crossed layers.

Prefer one high-value integration/request spec proving whole behavior over many narrow specs for nested implementation details.

- Endpoint spec should exercise route, controller, params, response code, schema, service flow, mappers, value objects, persistence, jobs, and external API payloads together when practical.
- Add unit specs only for behavior hard, slow, brittle, or impossible to prove through integration path.
- Stub real boundaries only: network, gateways, mailers, queues, storage, time, env, feature flags.
- Prefer `WebMock`, `stub_env`, schemas/contracts, fake adapters, and persisted data over `allow_any_instance_of`, `receive_message_chain`, or stubbing domain methods.
- Read [references/testing-checklists.md](references/testing-checklists.md) when selecting coverage for a feature, payment flow, webhook/callback, i18n change, async workflow, or final verification.
- Read [references/testing-examples.md](references/testing-examples.md) when writing or reviewing FactoryBot usage, RSpec structure, shared examples/contexts, expensive request specs, or `spec_helper` vs `rails_helper`.

## Coding Workflow

Before editing:

1. Find current owner layer.
2. Read surrounding class and callers.
3. Identify side effects: DB, external API, jobs, cache, files, logs.
4. Decide if behavior is gate, orchestration, mutation, payload mapping, external boundary, read query, presentation, state transition, or pure calculation.
5. Read matching reference file above.

During edit:

- Keep changes scoped.
- Follow local naming/exception style.
- Prefer explicit small objects over hidden callbacks.
- Add compensation for partial side effects when relevant.
- Do not add private helpers in service classes.

After edit:

- Run focused tests.
- Run broader tests for crossed layers.
- Run i18n checks if locale keys changed.
- State what was not run.
- Review code for layer violations, test smells, and missing coverage; fix issues and rerun focused tests when needed.

## Smells

- Controller calls external client.
- Service has private utility methods.
- Mutator sends HTTP request.
- Mapper saves record.
- Serializer decides business status.
- Policy updates DB.
- Job contains full workflow.
- Model grows into workflow coordinator.
- Query object changes data.
- New abstraction only reduces lines, not concepts.
- External call inside transaction.
- Test can pass while public behavior is broken.
