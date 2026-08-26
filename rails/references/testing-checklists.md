# Ruby/Rails TDD Checklists

Use this reference when selecting test coverage, reviewing risk, or preparing the final verification note.

## Feature Coverage

- Happy path.
- Validation failure.
- Unauthorized/forbidden when policy/auth touched.
- Missing/malformed input.
- Not found.
- External dependency success/failure.
- Idempotency/retry when repeated calls possible.
- Old API response shape/schema.
- State transitions/timestamps.
- Empty/single/many collections.

## Payments / Financial

- Amount/currency.
- Payment rows/items.
- External transaction/link sync.
- Callback/webhook status mapping.
- Refund/cancel payloads.
- Duplicate callback/idempotency.
- Partial failure/retry.

## Webhooks / Callbacks

- Event persisted before processing.
- Controller validates/finds/stores/enqueues.
- Processing job lifecycle.
- Duplicate/malformed payload behavior.
- External failure reporting.
- Retry after failure.

## I18n

- Add all required locales.
- Use existing locale structure.
- Run project i18n missing/normalize checks if present.
- Do not finish with missing translations.

## Time, Jobs, Async

- Freeze/travel time for timestamp behavior.
- Use `perform_enqueued_jobs` when request behavior depends on jobs.
- Cover stale-record behavior when jobs reload persisted records.
- Cover retryable workflows with failure first, then successful retry.
- Avoid sleeps; use job adapters, polling helpers, or explicit state.

## Test Smells

- Mock-only spec proves no business state.
- Request spec asserts internals instead of response/state/contracts.
- Unit spec creates full app graph for pure method.
- Shared context hides key setup/payload.
- Test mutates global config/time without cleanup.
- Spec depends on order or seed data.
- Real network, sleeps, or current time where deterministic time needed.
- Migration spec prints noisy DSL output; use connection-level checks for DB state.

## Done

- Failing spec exists for bug/feature before or alongside implementation.
- Focused specs pass.
- Cross-layer specs pass when workflow crosses request/job/service/external boundary.
- Contract/schema checks pass for existing APIs.
- I18n checks pass when locales changed.
- No unexplained noisy test output.
- Full CI or equivalent broad run done for large changes, or final note says not run.
