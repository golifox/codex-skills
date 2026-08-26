# Presenters / Serializers

Presenter owns read formatting. Serializer owns API output shape.

Representation layer prepares data for a consumer. It must not decide domain state.

## Presenter Responsibilities

- View-facing read helpers.
- Formatting display values.
- Delegates for associated display fields.
- View-component/component props preparation when project pattern uses presenters.
- No state mutation.

## Presenter Variant 1: Included Module

Use when the project keeps presenter methods as modules under `app/presenters` and includes them into models.

```ruby
module OrderPresenter
  def order_price
    Money.from_cents(price_cents, currency).format
  end

  def display_status
    I18n.t("orders.statuses.#{status}")
  end
end
```

```ruby
class Order < ApplicationRecord
  include OrderPresenter
end
```

Rules:

- Keep only read/formatting helpers here.
- Do not mutate state.
- Do not call external APIs.
- Do not hide business decisions in display methods.

## Presenter Variant 2: Decorator Module

Use when the project uses `gem 'auto_decorator'` and keeps presentation outside the model instance.

```ruby
module OrderDecorator
  def order_price
    Money.from_cents(price_cents, currency).format
  end

  def callback_headers
    {
      Authorization: "Basic #{shop.basic_auth_key}"
    }.merge(Current.external_http_headers)
  end
end
```

With auto-decorator enabled by the project, prefer `<MODEL_NAME>Decorator` module naming under `app/decorators`. Do not mix module-presenter and decorator styles for the same model without a migration reason.

## Serializer Responsibilities

- API fields.
- Backward-compatible response shape.
- Version-specific output.
- Reading model/presenter/decorator only.
- Choosing explicit Blueprinter views when response shape differs by consumer.

## Serializer Rules

- Use Blueprinter strictly.
- Define views explicitly when output differs by API version/client/admin/public context.
- Use `render_response record, serializer: SomeSerializer, view: :some_view, **options`.
- Do not use JSONAPI serializers or ad hoc hashes for normal API output.
- Keep old API serializers backward-compatible.
- Serializer aliases like `as_hash` may exist for non-controller payloads such as outbox/webhook bodies; controllers still use `render_response`.

## Good Serializer

```ruby
class OrderSerializer < BaseSerializer
  view :client do
    fields :status, :created_at, :updated_at
    field :order_price, name: :price

    association :profile, blueprint: ProfileSerializer, view: :client
  end

  view :admin do
    fields :status, :created_at, :updated_at, :internal_comment
  end
end
```

```ruby
render_response order, serializer: OrderSerializer, view: :client
```

## Bad

```ruby
class OrderSerializer < BaseSerializer
  view :client do
    field :status do |order|
      order.complete! if order.ready?
      order.status
    end
  end
end
```

## Checklist

- Read-only.
- Old API shape preserved.
- New fields gated by correct Blueprinter view.
- Formatting not buried in model unless project uses included presenter modules.
- Expensive queries preloaded before serialization when possible.
- `render_response` used for controller responses.
