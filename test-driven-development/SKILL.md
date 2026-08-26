---
name: test-driven-development
description: >
  Drive Rails/Ruby development with tests. Use when implementing logic, fixing bugs, changing
  behavior, adding edge cases, or proving a regression with RSpec, request specs, service specs,
  model specs, job specs, FactoryBot, WebMock, or Rails test helpers.
---

# Test-Driven Development

Write the failing spec first, then the minimum code, then refactor.

## Cycle

```text
RED -> GREEN -> REFACTOR -> VERIFY
```

## RED

Write the smallest failing spec for visible behavior or regression.

```ruby
RSpec.describe 'POST /admin/tasks/:id/complete' do
  subject(:request) { post admin_task_complete_path(task), headers: auth_headers(admin) }

  let(:admin) { create(:user, :admin) }
  let(:task) { create(:task, status: 'pending', completed_at: nil) }

  it 'marks the task complete and records the timestamp' do
    freeze_time do
      expect { request }.to change { task.reload.status }.from('pending').to('completed')

      expect(response).to have_http_status(:ok)
      expect(task.reload.completed_at).to eq(Time.current)
    end
  end
end
```

The first run must fail for the expected reason.

## GREEN

Add minimal Rails code in the right layer:

```ruby
class Tasks::Complete
  def self.complete(task:, actor:)
    Task.transaction do
      task.update!(status: 'completed', completed_at: Time.current)
    end
  end
end
```

Prefer named methods (`complete`, `approve`, `index`) over generic `.call`, matching `rails`.

## REFACTOR

With specs green:

- Improve names.
- Move orchestration to service, persistence to mutator/model, payloads to mapper.
- Remove duplication only when the abstraction has a real concept.
- Keep tests behavior-focused.

## Rails Test Choice

- Request spec: auth, params, HTTP status, response schema, persistence, jobs, external payload.
- Service spec: orchestration, idempotency, retries, state transitions.
- Model spec: validation, association, scope, intentional callback.
- Job spec: async wrapper, retry, reload/stale-record behavior.
- Policy spec: authorization gates.
- Query/serializer spec: deterministic read/output behavior.

## Boundary Doubles

Stub only real boundaries:

- Network and gateways with WebMock or fake manager.
- Mailers, jobs, storage, time, env, feature flags.
- Do not stub internal domain collaborators by default.

## Commands

Use project commands first. Defaults:

```bash
bin/rspec spec/requests/admin/tasks/complete_spec.rb
bin/rspec spec/services/tasks/complete_spec.rb
bin/rspec spec/jobs/task_export_job_spec.rb
bin/rails test
```

## Verification

- New behavior has a failing spec before implementation or a regression spec for bug fix.
- Focused specs pass.
- Cross-layer specs pass when workflow crosses request/job/service/external boundary.
- No skipped tests.
- Final answer states what was and was not run.
