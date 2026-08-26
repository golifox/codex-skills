# Abstractions / Naming / Workflow

Use abstractions only when they clarify ownership and behavior.

## Abstraction Rules

- Prefer temporary duplication to wrong abstraction.
- Extract only when concept has clear layer and name.
- Do not add abstraction if you cannot say: “this represents business concept X”.
- Do not add abstraction if it has no stable public interface.
- Keep each method at one abstraction level.
- Do not use `.call` as a public API for business services, queries, filters, or value objects.
- Shared business flow belongs in business logic/service layer.
- State mutation belongs in mutator/model layer.
- External interaction belongs in manager.
- Payload/data transformation belongs in mapper.
- Generic pure logic can live in `lib/` or explicit PORO layer.
- Do not build parallel architecture when existing layer can be extended.
- Keep type-specific behavior behind small adapter/interface, not scattered conditionals.
- Avoid hidden global state. Business decisions should be explicit in params, config snapshot, model fields, or service inputs.
- Over-abstraction is real: new layers must reduce churn/coupling, not just line count.

## Extraction Direction

Downward extraction:

- split model concept into value object/delegate/domain object;
- keep dependency direction inside domain layer;
- useful when model owns too many small domain concepts.

Upward extraction:

- move workflow/application concerns into service/form/filter/query/presenter;
- useful when model/controller talks to concerns above or beside its responsibility.

If a model calls an external API or reads request context, downward extraction is not enough. Add an upper layer.

## Naming

- Jobs: `Context::ActionJob`, not `ActionContextJob`.
- Side-effect methods: verbs; no meaningful business return.
- Value-returning methods: nouns/noun phrases.
- Service/query public APIs must name the operation: `PaymentService.create(...)`, `CallbackService.process(...)`, `ServiceQuery.index(...)`.
- Value objects should be initialized and queried: `PriceCalculation.new(order).total`, not class-level generic execution methods.
- Rails `create/update/destroy` keep normal Rails meaning.
- Temporary legacy alias needs explicit `TODO:` removal note.

## Communication

- Ask when business behavior unclear.
- State layer choice before large edit.
- Point out boundary tradeoff if request pushes logic into wrong layer.
- Keep implementation notes concrete: owner layer, side effects, tests run.

## Coding Workflow

Before edit:

1. Find owner layer.
2. Read callers/callees.
3. Identify side effects: DB, external API, jobs, cache, files, logs.
4. Pick layer by responsibility.
5. Add integration-first test for visible behavior.

During edit:

- Keep scope small.
- Follow local exception/naming style.
- Prefer explicit object over callback magic.
- Preserve external contracts.

After edit:

- Run focused specs.
- Run broad specs for crossed layers.
- Run i18n checks if locales changed.
- Say what was not run.

## Smells

- New abstraction only reduces line count.
- Helper name describes implementation, not business concept.
- Object knows HTTP, DB, and external API at once.
- Branching by type spread across many files.
- Side effects hidden behind value-returning method.
