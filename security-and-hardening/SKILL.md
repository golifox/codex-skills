---
name: security-and-hardening
description: >
  Harden Rails/Ruby code against vulnerabilities. Use when handling user input, authentication,
  authorization, sessions, PII, payments, file uploads, webhooks, external APIs, LLM output,
  background jobs, or any untrusted data crossing a Rails boundary.
---

# Security and Hardening

Treat every external input as hostile, every secret as sensitive, and every authorization check as mandatory.

## Threat Model First

1. Map trust boundaries: controllers, params, uploads, webhooks, jobs, external APIs, LLM output.
2. Name assets: credentials, PII, payment data, admin actions, money movement.
3. Run STRIDE quickly: spoofing, tampering, repudiation, disclosure, denial of service, privilege escalation.
4. Turn abuse cases into specs.

## Rails Controls

- Validate params at the controller boundary with the project's schema style.
- Authorize every protected action with policy/scenario objects.
- Use ActiveRecord parameterization; never concatenate SQL with user input.
- Use Rails escaping; do not render unsanitized user HTML.
- Keep secrets in credentials/env, never in code or logs.
- Use secure, httpOnly, sameSite cookies for sessions.
- Add rate limits for auth, password reset, webhooks, and expensive endpoints.
- Verify webhook signatures before processing.
- Keep external API calls out of DB transactions.
- Treat LLM output as untrusted data and validate before use.

## Examples

Bad SQL:

```ruby
User.where("email = '#{params[:email]}'")
```

Good:

```ruby
User.find_by(email: safe_params[:email])
User.where('created_at >= ?', safe_params[:since])
```

Bad authorization:

```ruby
def update
  account = Account.find(params[:id])
  account.update!(safe_params)
end
```

Good:

```ruby
def update
  account = Account.find(params[:id])
  authorize!(account, to: :update?)
  Accounts::Update.update(account:, params: safe_params, actor: current_user)
end
```

Webhook boundary:

```ruby
def create
  Webhooks::VerifySignature.verify!(request:)
  event = WebhookEvent.create!(provider: 'stripe', payload: request.raw_post)
  ProcessWebhookJob.perform_later(event.id)
  head :accepted
end
```

## Ask First

- New auth flow or role model.
- Storing new PII/payment data.
- New external integration or webhook.
- CORS/session/security-header changes.
- File uploads.
- Rate limit changes.
- Admin or elevated permissions.

## Never

- Commit secrets.
- Log tokens, passwords, full card numbers, or raw sensitive payloads.
- Trust client-side validation.
- Disable security controls for convenience.
- Expose stack traces to users.
- Execute LLM output as SQL, shell, Ruby, HTML, or file paths.

## Security Checklist

```markdown
### Authentication and Authorization
- [ ] Protected endpoints authenticate user.
- [ ] Policy check proves user owns or may access resource.
- [ ] Admin actions require explicit admin permission.

### Input and Output
- [ ] Params validated at boundary.
- [ ] SQL is parameterized.
- [ ] HTML output escaped or sanitized.
- [ ] File uploads check size, type, and storage permissions.

### Data and Secrets
- [ ] No secrets in source, logs, or specs.
- [ ] Sensitive fields excluded from serializers.
- [ ] PII/payment data handled according to project policy.

### Integrations
- [ ] Webhook signatures verified.
- [ ] External calls have timeout/retry/idempotency strategy.
- [ ] SSRF risk checked for user-influenced URLs.

### Rails Runtime
- [ ] Security headers/session settings intact.
- [ ] Auth endpoints rate-limited.
- [ ] Errors do not reveal internals.
```

## Verification

- Security-relevant behavior has request/service specs.
- Abuse cases are covered.
- Focused security tests pass.
- Dependency/security scanner run when project provides one.
- Residual risk is stated if not fully verified.
