# Queries / Repositories

Query/repository owns read-side complexity.

## Responsibilities

- Complex SQL.
- Search/filter logic.
- Index/list filtering.
- Pagination/order composition.
- Reusable read scopes.

## Public API

Follow the project style: named class methods, no `initialize`, no `.call`, no generic `resolve`.

Good method names:

- `SomeQuery.index(params)`
- `SomeQuery.history(client_token, params)`
- `SomeQuery.find_many_by(params)`
- `SomeQuery.search(params)`

## Rules

- Read-only.
- Keep scopes composable.
- Do not mutate in query.
- Do not hide authorization unless query is explicitly policy-aware.
- Keep controller list actions thin.
- Return `ActiveRecord::Relation` when callers may paginate/order/preload further.
- Return materialized domain objects only when repository intentionally hides Active Record internals.

## Good

```ruby
class ServiceQuery
  def self.index(params)
    q = Service.active.not_blocked

    q = q.where(category: params[:category]) if params[:category].present?
    q = q.search(params[:q]) if params[:q].present?
    q = q.limit(params[:limit]) if params[:limit]

    q
  end
end
```

Controller:

```ruby
services = ServiceQuery.index(safe_params.output)
render_response services, serializer: ServiceSerializer, view: :client
```

## Bad

```ruby
class ServiceQuery
  def self.index(params)
    Service.where("category = '#{params[:category]}'")
  end
end
```

```ruby
def index
  scope = Order.all
  scope = scope.where("status = '#{params[:status]}'")
  scope.each { |order| order.update!(seen: true) }
end
```

## Checklist

- No writes.
- SQL safe.
- Filters reusable.
- Controller only passes params/scope.
- Heavy read logic covered by specs.
- Relation vs array return type is intentional.
- No `initialize`/`.call` query API.

## Query vs Repository

Query object:

- builds one focused read;
- usually returns `ActiveRecord::Relation`;
- can be composed with scopes or other queries.

Repository:

- groups reusable read scopes for a model/domain concept;
- may be an included module if project keeps scopes in `app/repositories`;
- should stay read-oriented unless project explicitly uses repository as persistence boundary.

Use full repositories only when the project wants a stronger data-access boundary. For normal Rails code, scopes and query objects are often enough.
