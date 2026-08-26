# Foundation Principles

These rules summarize general ideas from layered Rails design practice and Painless Rails style architecture.

## Why Layers Exist

Rails gives a small starting set: controller, model, view, job, mailer. That is productive early, but large applications need more names for different kinds of work.

Add layers to control change:

- Controllers change when HTTP/API behavior changes.
- Services change when business scenarios change.
- Mutators change when persistence shape changes.
- Managers change when external integrations change.
- Mappers change when payload contracts change.
- Queries change when read/filter/search behavior changes.
- Presenters/serializers change when representation changes.

The goal is not purity. The goal is predictable ownership.

## Good Layer

A good layer:

- has one clear responsibility;
- exposes a small public interface;
- hides implementation details;
- avoids circular or reverse dependencies;
- can be tested directly when needed;
- has a naming convention that lowers decision cost;
- reduces churn in surrounding layers.

If the new object has no stable responsibility or interface, it is probably just a file split.

## Semantic Abstractions

Prefer names from the product/application language:

```ruby
InvoiceService.approve(invoice)
```

Avoid names that describe only implementation:

```ruby
InvoiceService.update_status_and_send_email(invoice)
```

Implementation details belong inside the owning layer or a lower specialized layer.

Avoid generic `.call` for business APIs. It says nothing about the operation and forces the reader to open the class to understand the verb.

## Single Level Of Abstraction

One method should speak at one level.

Good:

```ruby
def complete(order)
  OrderPolicy.ensure_completable!(order)
  OrderMutator.complete(order)
  OrderExportJob.perform_later(order)
end
```

Bad:

```ruby
def complete(order)
  return unless params[:force] || order.user.active?
  order.update!(status: "completed")
  ExternalClient.post(JSON.dump(order: order.attributes))
  render_response order, serializer: OrderSerializer, view: :client
end
```

The bad example mixes params, domain policy, persistence, external API, serialization, and HTTP response.

## Application Logic vs Business Logic

Business logic describes domain rules and scenarios.

Application logic describes how users, requests, jobs, forms, views, APIs, and infrastructure interact with the domain.

Examples of application logic:

- HTTP params parsing;
- request authentication;
- form-only validations;
- UI sorting/filter params;
- JSON schema shape;
- background retry settings;
- configuration source loading.

Keep application logic above the model/domain layer. Do not put form-only validations, controller params, current user, or external request payloads into domain models.

## Gradual Extraction

Do not create every possible layer upfront.

Extract when one of these is true:

- controller/model tests describe behavior outside that layer's responsibility;
- callbacks hide scenario order;
- one model gets context-specific validations or behavior;
- query chains become complex or duplicated;
- external payload mapping spreads across actions;
- service code mixes orchestration with persistence, payload building, and integration calls;
- configuration source details leak everywhere.
- integration retry/delivery state needs persistence: use outbox, not ad hoc jobs.

## Rails Compatibility

Extend Rails, do not fight it:

- simple CRUD may stay in model/controller;
- simple scopes may stay in models;
- simple templates may stay templates;
- Active Record is acceptable when it keeps code simple;
- dry-rails controller schemas, Blueprinter serializers, konsierge-response helpers, and AnywayConfig objects are normal Rails extensions in this style;
- introduce stronger boundaries only when complexity justifies the cost.

## Specification Test

Use tests as architecture feedback.

If a request/controller spec must cover many branches that are not HTTP concerns, move those branches to lower layers and test them there or through a higher integration flow.

If a model spec must cover external payloads, jobs, or user-interface context, extract those concerns.

## Database And Infrastructure

The database is part of the architecture, not an invisible detail.

Use database constraints/indexes/types/triggers only for data-level consistency or performance, not as a hidden place for business scenarios.

Infrastructure providers are implementation details. Hide them behind managers, adapters, configuration objects, or framework abstractions.

## Global State

Use current/global request state sparingly.

- Set it only near inbound boundaries.
- Read it only in explicitly allowed upper layers.
- Never require models or low-level objects to know `current_user`, request, session, or job context.
