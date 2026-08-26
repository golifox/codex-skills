# State Machines

State machine owns status/state definitions and transitions.

Use AASM when the project has it.

## Responsibilities

- States.
- Legal transitions.
- Guards.
- Transition timestamps/history if project pattern uses them.
- Status-related events.
- State scopes when they are part of transition lifecycle.

## Rules

- Module name: `ModelName::StateMachine`.
- Model includes module.
- Use existing transition events.
- Do not update status directly when event exists.
- Keep heavy workflow out of transition callbacks.
- Use project column name (`state` or `status`) consistently.

## Good

```ruby
class Order < ApplicationRecord
  include Order::StateMachine
end

module Order::StateMachine
  extend ActiveSupport::Concern

  included do
    include AASM

    aasm column: :state, whiny_transitions: true, timestamps: true do
      state :created, initial: true
      state :paid

      event :pay do
        transitions from: :created, to: :paid
      end
    end
  end
end
```

## Bad

```ruby
order.update!(status: 'paid')
ExternalClient.export(order)
```

## Checklist

- Event used instead of direct status write.
- Guard clear and testable.
- Timestamps/history preserved.
- External IO not inside transition unless project explicitly owns it there.
- Scopes like `processing` / `will_be_expired` stay near state definition when they describe lifecycle state.
