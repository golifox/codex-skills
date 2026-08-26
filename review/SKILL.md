---
name: review
description: >
  Ultra-compressed but rigorous code review. Focuses on correctness, security,
  maintainability, tests, static checks, and project conventions. Each finding is terse,
  specific, and actionable: location, problem, impact, fix. Use when user says
  "review this PR", "code review", "review the diff", "/review", or invokes
  /caveman-review. Auto-triggers when reviewing pull requests.
---

Review code changes with maximum signal and minimum noise.

Default style: terse, precise, actionable. One finding per line. No throat-clearing.

## Output Shape

Group findings by severity:

### Blocking
Must fix before merge.

### Non-blocking
Important, but not necessarily merge-blocking.

### Suggestions
Optional readability, maintainability, testing, or documentation improvements.

### Checks
Mention relevant tests, linters, formatters, i18n checks, or verification gaps.

If no findings:

`No findings. Checked security, correctness, tests, static checks, and project conventions.`

## Finding Format

Use one line per finding when possible:

`<file>:L<line>: <severity>: <problem>. <impact>. <fix>.`

For single-file reviews:

`L<line>: <severity>: <problem>. <impact>. <fix>.`

For ranges:

`<file>:L<start>-<end>: <severity>: <problem>. <impact>. <fix>.`

Severity labels:

- `bug:` broken behavior, regression, incident risk
- `security:` auth, input, data leak, injection, secrets, unsafe external/file/network behavior
- `risk:` fragile behavior, race, missing null check, swallowed error, weak failure handling
- `test:` missing or weak coverage for meaningful behavior
- `maintainability:` unclear structure, misplaced responsibility, duplicated domain rule
- `nit:` style, naming, minor cleanup; author can ignore
- `q:` genuine question; not a disguised suggestion

## Caveman Rules

Drop:
- "I noticed that..."
- "It seems like..."
- "You might want to consider..."
- "This is just a suggestion..."
- "Great work..."
- Restating what the diff already shows
- Hedging: "perhaps", "maybe", "I think"

Keep:
- Exact file and line
- Exact symbol/function/variable names in backticks
- Concrete fix
- Practical impact when not obvious
- Project convention references when relevant
- Speculative concerns clearly marked as `speculative`

Bad:

`I noticed that the user object might be nil here and this could potentially cause an issue.`

Good:

`app/services/users/importer.rb:L42: bug: `user` can be nil after `find_by`. This crashes on `.email`. Add guard or use `find_by!` with explicit failure handling.`

Bad:

`This function is pretty long and could maybe be refactored.`

Good:

`app/jobs/sync_job.rb:L88-L140: maintainability: 50-line method mixes validation, normalization, and persistence. Split into `validate`, `normalize`, and `persist`.`

## Review Checklist

### Security

Check:
- Unsafe input handling
- Missing authentication or authorization
- Data leaks or unsafe logging
- Insecure defaults
- SQL/NoSQL injection
- Unsafe file or network operations
- Secret exposure
- Dependency risk
- User data, permissions, admin paths, internal/system APIs
- External API calls, webhooks, payments, background jobs
- Sensitive operation validation, auditability, and failure handling

If speculative:

`<file>:L<line>: security: speculative: <risk>. Confirm by checking <condition>. Fix by <action>.`

Use normal paragraphs only for CVE-class or high-impact security findings that need explanation, attack path, or references. Then resume terse mode.

### Correctness

Check:
- Intended behavior matches implementation
- Happy path and failure path
- nil/null, empty values, invalid input
- Edge cases and boundary values
- Race conditions
- Retries and idempotency
- Error handling
- API errors, malformed responses, timeouts
- Duplicate events and partial failures
- State transitions, persistence, callbacks, background jobs, side effects

Flag:
- Logic gaps
- Regressions
- Incomplete implementation
- Behavior diverging from project conventions

### Business Logic

Check:
- Business rules are explicit and readable
- Domain terms, statuses, flags, and conditions are named consistently
- Important decisions are visible in the right layer
- Rules are not hidden in low-level helpers, callbacks, or generic abstractions

Flag:
- Hidden assumptions
- Implicit side effects
- Unclear branching
- Duplicated domain rules
- Clever logic where simple logic works better

### Simplicity

Check:
- Unnecessary abstractions
- Excessive indirection
- Premature generalization
- Single-use abstractions with no clear value
- Patterns harder to reason about than the problem requires

Do not suggest large rewrites unless they materially improve correctness, security, or maintainability.

### Code Quality

Check:
- Naming, structure, readability
- Cohesion and coupling
- Consistency with surrounding code
- AGENTS.md instructions
- Correct layer placement: controller, service, interactor, model, serializer, job, policy, validator, client
- Explicit error handling
- Consistent exceptions, result objects, return values, logs
- Duplication, dead code, unclear conditionals, hidden global state, unnecessary mutation
- Safe and useful logging

### Tests

Check whether tests cover:
- Main happy path
- Invalid input
- Authorization failures
- Validation failures
- External API failures
- Timeouts
- Malformed responses
- Missing records
- Empty and nil values
- Duplicate requests
- Unexpected states
- Boundary values
- Unsupported enum/status values
- Dangerous payloads
- Empty collections
- Single item vs many items
- Large values
- Special characters
- Timezone/date boundaries
- Idempotent repeated calls
- Retries and races
- Partial failures
- Business rules directly
- Security-sensitive behavior
- Webhook/request signatures
- Payment checks
- Admin-only behavior
- Regression coverage for bug fixes

Check contract/schema coverage where relevant:
- Request payload schema
- Response payload schema
- External API contract schema
- Webhook payload schema
- Serializer/output schema
- JSON schema validation via project matchers such as `match_request_payload_schema`

Test quality rules:
- Prefer behavior and business intent over implementation details
- Avoid brittle, broad, mock-only tests
- Tests must be isolated and deterministic
- No real network, real time, shared global state, or order dependence
- Time-dependent logic should use time helpers/freezing
- Background jobs, mailers, notifications, webhooks, and external APIs need fakes/stubs with clear expectations
- Database behavior should be tested at the right level: validations, scopes, constraints, migrations, callbacks, transactions

### Static Checks

Check likely failures in:
- Tests
- Linter
- Formatter
- Type checker
- Static analysis
- i18n tasks when translations or user-facing strings change

Flag:
- Formatting drift
- Unused imports/requires
- Dead code
- Unreachable branches
- Missing translations
- New strings not localized
- Translation keys not reused

Mention commands only when relevant:

`Checks: run `bundle exec rspec spec/...` and `bundle exec rubocop path/...`.`

### Documentation

Suggest docs only when they clarify:
- Non-obvious behavior
- Public APIs
- Configuration
- Operational concerns
- Business rules
- Schema changes
- Environment variables
- README/API/changelog updates

Do not ask for comments that restate obvious code. Prefer comments explaining why.

### Scope

Review only visible code and provided context unless asked otherwise.

Do not check:
- Whether files were added to Git
- Whether untracked files exist

Say when something cannot be verified from the diff/context. Do not guess.

## Style Rules

Prioritize high-impact issues over minor style comments.

Every finding must answer:
- What is wrong
- Why it matters
- How to fix it

Keep this compressed into one line unless clarity would suffer.

Distinguish:
- Blocking bugs/security issues
- Non-blocking risks
- Optional suggestions

Do not over-optimize for theoretical purity when the code is simple, correct, readable, and consistent.

Do not approve, request changes, or write the fix unless the user explicitly asks.

## Auto-Clarity

Drop terse mode only for:
- Serious security findings needing attack path or reference
- Architectural disagreement needing rationale
- Onboarding context where the author needs the why
- Speculative concerns that need verification steps

For those, write one concise paragraph, then return to one-line findings.

## Examples

`app/controllers/payments_controller.rb:L31: security: missing authorization before `refund!`. Any authenticated user could refund another account. Check ownership/admin policy before calling `refund!`.`

`app/jobs/webhook_job.rb:L54: bug: duplicate webhook events are not idempotent. Retries can create duplicate charges. Store and check provider event id before processing.`

`app/clients/vendor_client.rb:L77: risk: 429 responses are treated as hard failures. Temporary rate limits drop syncs. Retry with bounded backoff.`

`spec/services/importer_spec.rb:L12: test: only happy path is covered. Invalid CSV rows can silently skip validation. Add bad-row and empty-file cases.`

`app/models/order.rb:L93: maintainability: `paid?` duplicates status logic from `PaymentState`. Future status changes can diverge. Reuse the domain helper.`

`config/locales/en.yml:L18: nit: new user-facing string is hard-coded elsewhere. Reuse this translation key in the view.`
