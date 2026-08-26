# Shapes / Context-Specific Model Behavior

Shape owns context-specific behavior of a model when the base domain model should stay clean.

Use a shape when the same persisted entity behaves differently in a specific application context.

## Responsibilities

- Context-specific validations.
- Context-specific defaults.
- Context-specific input normalization.
- Form-like behavior backed by one underlying model.
- Keeping application logic out of domain model.

## When To Use

Use a shape when:

- registration requires confirmation/acceptance fields, but imports do not;
- admin editing requires extra fields, but normal editing does not;
- one screen needs stricter validation than the persisted model invariant;
- input should be normalized differently for one context.

Do not add conditional model validations for these cases unless the condition is a true domain invariant.

## Shape vs Form Object

Shape:

- wraps one underlying model concept;
- represents a contextual version of that model;
- keeps Rails model naming/behavior when useful.

Form object:

- may have no model;
- may combine several unrelated models;
- is closer to presentation/user input.

## Good

```ruby
class UserRegistrationShape < User
  include ApplicationShape

  validates :email_confirmation, presence: true
  validates :terms_accepted, acceptance: true

  def email=(value)
    super(value.to_s.strip.downcase)
  end
end
```

```ruby
class Imports::UserMutator
  def self.create(attrs)
    User.create!(attrs.slice(:email, :name))
  end
end
```

## Bad

```ruby
class User < ApplicationRecord
  validates :terms_accepted, acceptance: true, unless: :imported?
  validates :email_confirmation, presence: true, if: :from_registration?
end
```

This makes application contexts leak into the domain model.

## Rules

- Keep unconditional domain invariants in the model.
- Put context-specific input rules into shape/form layer.
- Do not use shape to bypass real model consistency.
- Do not call external APIs from shape.
- Keep shape names contextual: `UserRegistrationShape`, `OrderAdminShape`.

## Checklist

- Is behavior context-specific, not universal?
- Does base model remain valid without this context?
- Are validations/defaults/normalizers application-level?
- Would a conditional validation make the model harder to reason about?
