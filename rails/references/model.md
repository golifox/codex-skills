# Models

Model owns persistence and narrow domain invariants.

Treat models as domain models backed by persistence, not as a dumping ground and not as persistence-only structs.

## Responsibilities

- Schema-backed attributes.
- Associations.
- Validations.
- Consistency rules that must hold for the record.
- Transition guards/state-machine definitions when local to entity.
- Simple scopes.
- Narrow domain helpers.
- Including state machine/concerns.
- Persistence-level invariants.
- DB-backed validations/associations when project uses `database_validations`.
- JSON/JSONB typed properties when project uses `active_record_properties`.
- Money fields when project uses `money-rails`.
- Audit/soft-delete declarations when project uses `paper_trail`, `logidze`, or `discard`.

## Avoid

- Full workflow orchestration.
- External API calls.
- HTTP response logic.
- Serializer/view formatting.
- Large presenter-only methods.
- Many conditional callbacks for business pipeline.
- Request/form-only validations.
- `current_user`, session, params, or job context.

## Rules

- Keep universal invariants in the model.
- Move context-specific validations to shape/form.
- Move non-trivial state changes to mutator.
- Move workflow orchestration to service.
- Move complex reusable reads to query/repository.
- Extract custom validators when validations become multi-step but remain model-level.
- Use callbacks only for local technical consistency, not hidden business workflow or external IO.
- Prefer `validates_db_presence_of` / `validates_db_uniqueness_of` when project uses database_validations.
- Prefer explicit `kept` / `discarded` scopes over `default_scope` for soft deletion.

## Good

```ruby
class Order < ApplicationRecord
  include Order::StateMachine
  include Discardable

  has_paper_trail skip: %i[updated_at]
  monetize :price_rate

  validates_db_presence_of :number

  scope :paid, -> { where(status: 'paid') }

  def overdue?
    due_at.present? && due_at.past?
  end
end
```

## Bad

```ruby
class Order < ApplicationRecord
  after_commit :export_to_provider

  def export_to_provider
    ExternalProvider.create(self)
    update!(exported: true)
  end
end
```

## Checklist

- Invariants local to record.
- Workflow in service/mutator.
- Presentation in presenter/serializer.
- External IO outside model.
- Scopes remain composable.
- Context-specific behavior extracted.
