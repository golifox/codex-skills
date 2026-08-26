# Controllers

Controller owns HTTP boundary. Keep it thin and explicit.

Controller is an inbound layer: it translates request context into an application/business action.

## Responsibilities

- Validate and normalize params with dry-rails `schema(:action)` in the controller.
- Authenticate/authorize request boundary.
- Verify signatures/basic auth/session when applicable.
- Call service/query/serializer/policy.
- Translate known business errors to HTTP response.
- Render response with `render_response` from konsierge-response and Blueprinter serializer/view.

## Allowed Calls

- Service action for business flow.
- Query/repository for read-only lists.
- Policy for access/business gate.
- Serializer/presenter for output.
- Job only for explicit async command when project pattern allows.

## Forbidden

- Direct external API client call.
- Price/calculation/business workflow.
- Direct mutation of model internals beyond trivial Rails CRUD when no layer exists.
- Duplicated validation/gates that belong to policy/service/model.
- Building large payloads inline.
- Manual serializer rendering when `render_response` can do it.

## Pattern

```ruby
module Api
  module Client
    module V1
      class OrdersController < BaseController
        schema(:create) do
          required(:return_url).filled(:string)
          required(:items_count).filled(Types::PositiveInteger)
          optional(:search_id).filled(Types::UUID7)
        end

        def create
          order = OrderService.create(safe_params.output, client_token:)

          render_response order, serializer: OrderSerializer, view: :client, status: 201
        rescue OrderService::ValidationError => e
          render_error(e.message, status: 400, error_key: e.error_key)
        end
      end
    end
  end
end
```

Read action with query:

```ruby
module Api
  module Client
    module V1
      class ServicesController < BaseController
        schema(:index) do
          optional(:q).filled(:string)
          optional(:limit).filled(Types::PositiveInteger)
        end

        def index
          services = ServiceQuery.index(safe_params.output)

          render_response services, serializer: ServiceSerializer, view: :client
        end
      end
    end
  end
end
```

## Bad

```ruby
def create
  order = Order.create!(params[:order])
  ExternalGateway.create_order(order.attributes)

  render_response order, serializer: OrderSerializer, view: :client
end
```

## Checklist

- Params validated once at boundary.
- Response shape unchanged unless intended.
- Known errors mapped, unknown errors not swallowed.
- No external API client.
- No duplicated business calculations.
- Uses `render_response`, not manual serializer rendering.
- Blueprinter serializer/view selected explicitly when response is serialized.
- Use local normalized params accessor: `safe_params.output` / `safe_params.to_h` / `clean_params`, depending on controller base class.
- Use `sig: true` in `render_response` only when endpoint contract requires a signed response.

## Specification Test

If a controller/request spec needs many contexts for model state, external payload variants, or business branches, that behavior probably belongs below the controller.

Keep controller specs focused on:

- route/action is reachable;
- auth/signature/params boundary;
- known errors map to response status/body;
- service/query/serializer is wired correctly when local style tests that.

Cover full public behavior with request specs, but do not let controller become owner of all branches.
