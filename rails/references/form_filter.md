# Forms / Filters / User Input

Forms and filters own user-provided input transformation when controllers or models would otherwise absorb too much application logic.

## Form Objects

Use form objects for non-trivial input flows:

- model-less input;
- input that creates/updates multiple models;
- input with presentation-specific validations;
- form feedback that does not equal domain validation.

Form object responsibility:

- expose attributes accepted by the UI/API action;
- validate user input;
- normalize or coerce input;
- call lower layers through named service methods;
- expose errors meaningful to the caller.

## Good Form

```ruby
class FeedbackForm
  include ActiveModel::Model

  attr_accessor :name, :email, :message

  validates :name, :email, :message, presence: true
  validates :message, length: {maximum: 160}

  def submit
    return false unless valid?

    FeedbackService.submit(name:, email:, message:)
    true
  end
end
```

## Bad Form Leakage

```ruby
class User < ApplicationRecord
  validates :terms_accepted, acceptance: true
  validates :email_confirmation, presence: true
end
```

Do not put one registration form's input rules into the base domain model if other contexts create the same model legitimately.

## Filter Objects / Query Objects

Use filter/query objects for user-driven query building:

- index/list filters;
- sorting;
- search params;
- faceted filters;
- query defaults and sanitization.

Follow project query style: named class method, no `initialize`, no `.call`.

## Good Query Filter

```ruby
class OrderQuery
  STATUSES = %w[draft paid completed].freeze
  SORT_FIELDS = %w[id created_at total_cents].freeze

  def self.index(params)
    q = Order.all

    q = q.where(status: params[:status]) if STATUSES.include?(params[:status])
    q = q.where(customer_id: params[:customer_id]) if params[:customer_id].present?

    sort = SORT_FIELDS.include?(params[:sort]) ? params[:sort] : "created_at"
    q.order(sort => :desc)
  end
end
```

```ruby
def index
  orders = OrderQuery.index(safe_params.output)

  render_response orders, serializer: OrderSerializer, view: :client
end
```

## Bad Filter

```ruby
def index
  orders = Order.all
  orders = orders.where("status = '#{params[:status]}'")
  orders = orders.order("#{params[:sort]} desc")

  render_response orders, serializer: OrderSerializer, view: :client
end
```

## Rules

- Controllers pass params/scope; filters own sanitization.
- Filters are read-only.
- Filters must not authorize unless explicitly named as policy-aware.
- Filters return relation/collection, not HTTP response.
- For reusable complex SQL, prefer query object under the filter.
- Query/filter public methods must describe the use case: `index`, `history`, `search`, `find_many_by`.

## Checklist

- Is this input user/API facing?
- Are there defaults or whitelist rules?
- Would putting this in model create interface-specific scopes?
- Can controller tests avoid enumerating every filter combination?
- No `.call` query/filter API.
