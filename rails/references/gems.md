# Gemfile / Common Gems

Use existing project gems before adding new abstractions or dependencies.

## Gemfile Style

- Group gems by responsibility with comments: core, ActiveRecord extensions, background processing, external services, presentation, utilities, internal Konsierge gems, dry-rb, monitoring, development/test.
- Keep internal gems in a `%w[...]` block with `gitlab: lib` when they share source options.
- Put linters/security tools under development or development/test with `require: false`.
- Keep test-only helpers in `group :test`.
- Add stdlib gems explicitly when Ruby removes them from default distribution.
- Do not add a gem for a tiny wrapper when project already has a local layer.

## Core Rails / Runtime

- `rails`, `pg`, `puma`, `rack-cors`, `bootsnap`, `thruster`: app runtime.
- `solid_queue`, `solid_cache`: Rails-native jobs/cache.
- `propshaft`, `react_on_rails`, `shakapacker`: frontend/assets when project has frontend surface.

Without:

```ruby
Thread.new { OrderService.expire(order) }
```

With:

```ruby
OrderExpireJob.perform_later(order)
```

## Background / MQ

- `solid_queue`: ActiveJob backend.
- `kicks`, `bunny`, `bunny-mock`: RabbitMQ consumers/producers and tests when project uses MQ.

Without:

```ruby
payloads.each { |payload| SomeConsumer.new.process(payload) }
```

With:

```ruby
SomeJob.perform_later(record)
```

or project MQ worker when the boundary is RabbitMQ-specific.

## dry-rails / dry-schema

Task: controller-level params validation.

Without:

```ruby
return render_error('bad id', status: 400) unless params[:id].to_s.match?(/\A\d+\z/)
```

With:

```ruby
schema(:show) do
  required(:id).filled(Types::Id)
end

order = Order.find(safe_params[:id])
```

## konsierge-response + Blueprinter

Task: stable API envelope and explicit serializer views.

Without:

```ruby
response_body = {data: {id: order.id, status: order.status}}
```

With:

```ruby
render_response order, status: 200, serializer: OrderSerializer, view: :client
```

```ruby
class OrderSerializer < BaseSerializer
  view :client do
    fields :status, :created_at
  end
end
```

## kaminari / Oj / Hashie

Task: pagination and JSON/hash handling.

Without:

```ruby
items = Service.all[offset, limit]
JSON.parse(body, symbolize_names: true)
```

With:

```ruby
items = Service.page(page).per(per)
payload = Oj.load(body)
```

Use these in query/controller/mapper boundaries, not in domain rules unless needed.

## anyway_config

Task: typed config object over ENV/YAML/credentials.

Without:

```ruby
timeout = Integer(ENV.fetch('PAYMENT_TIMEOUT_SECONDS', '5'))
```

With:

```ruby
class PaymentsConfig < ApplicationConfig
  config_name :payments
  attr_config timeout_seconds: 5
  coerce_types timeout_seconds: :integer
end

PaymentManager.create(order, timeout: PaymentsConfig.timeout_seconds)
```

## konsierge-outbox

Task: persisted external delivery with retry/attempts/handlers.

Without:

```ruby
ExternalClient.post(payload)
transaction.update!(callback_sent_at: Time.current)
```

With:

```ruby
Transaction::Outbox.enqueue(transaction)
```

```ruby
class Transaction::Outbox
  def self.enqueue(transaction, wait: nil)
    Konsierge::Outbox.enqueue(
      event_type: 'transaction.callback',
      entity: transaction,
      http_method: 'post',
      url: transaction.shop.url,
      body: TransactionSerializer.as_hash(transaction, view: :webhook),
      headers: transaction.shop_callback_headers,
      wait:
    )
  end
end
```

## konsierge-http / Faraday / net-http-persistent

Task: external HTTP through configured clients/managers.

Without:

```ruby
Net::HTTP.post(uri, payload.to_json)
```

With:

```ruby
Konsierge::HTTP::Manager::Payment.register(payload, headers: Current.external_http_headers)
```

Wrap direct provider calls in manager/gateway methods.

## konsierge-signature

Task: request/response signing at API boundary.

Without:

```ruby
headers['X-Signature'] = OpenSSL::HMAC.hexdigest('SHA256', secret, body)
```

With:

```ruby
render_response transaction, sig: true, serializer: TransactionSerializer, view: :compact
```

## konsierge-contracts

Task: contract/schema verification for payloads in specs and integrations.

Without:

```ruby
expect(payload[:amount]).to be_present
expect(payload[:currency]).to eq('RUB')
```

With:

```ruby
expect(payload).to match_contract_schema('payment/transactions/create/request_schema')
```

## AASM

Task: explicit state machine transitions.

Without:

```ruby
transaction.update!(state: 'paid', paid_at: Time.current)
```

With:

```ruby
transaction.to_paid! if transaction.may_to_paid?
```

Keep AASM definitions in state-machine concern/module.

## database_validations

Task: DB-backed presence/uniqueness validation.

Without:

```ruby
validates :uid, presence: true, uniqueness: true
```

With:

```ruby
validates_db_presence_of :uid
validates_db_uniqueness_of :uid
```

Still add database indexes/constraints.

## active_record_properties

Task: typed accessors over JSON/JSONB properties.

Without:

```ruby
agent['phone']
agent['inn']
```

With:

```ruby
has_properties column: :agent do
  property :phone, type: :string
  property :inn, type: :string
end
```

## active_form_model / validators

Task: form-like validation and common validators.

Without:

```ruby
errors.add(:email, :invalid) unless email.include?('@')
```

With:

```ruby
class InviteForm
  include ActiveModel::Model

  attr_accessor :email

  validates :email, email: true
end
```

Prefer controller `schema` for API params; use the local form base/form-model gem for richer form/application input objects.

## money-rails

Task: money values over integer/decimal amount columns.

Without:

```ruby
"#{price_rate / 100.0} #{price_currency}"
```

With:

```ruby
monetize :price_rate
humanized_money_with_symbol(transaction.price)
```

## discard

Task: explicit soft delete.

Without:

```ruby
record.update!(deleted_at: Time.current)
Model.where(deleted_at: nil)
```

With:

```ruby
record.discard!
Model.kept
```

Avoid `default_scope`; call `kept` / `discarded` explicitly.

## paper_trail / logidze

Task: audit/version history.

Without:

```ruby
Audit.create!(item: transaction, changes: transaction.previous_changes)
```

With:

```ruby
has_paper_trail versions: {class_name: 'Transaction::Version'}, skip: %i[updated_at]
```

or project-specific Logidze setup.

## auto_decorator

Task: presentation helpers outside model body.

Without:

```ruby
class Transaction < ApplicationRecord
  def receipt_email
    client_email.presence || receipt_provider&.email
  end
end
```

With:

```ruby
module TransactionDecorator
  def receipt_email
    client_email.presence || receipt_provider&.email
  end
end
```

Keep decorator methods read-only.

## pg_search / pg_query

Task: PostgreSQL search and query tooling.

Without:

```ruby
where("name ILIKE '%#{params[:q]}%'")
```

With:

```ruby
Service.search(params[:q])
```

Put reusable search/filter composition in query/repository layer.

## Uploads / Images / QR

- `carrierwave`, `carrierwave-aws`, `fog-aws`: uploads/storage.
- `image_processing`, `mini_magick`, `image_optimizer`: image transformations/optimization.
- `rqrcode`: QR generation.

Without:

```ruby
File.binwrite(path, uploaded_file.read)
```

With:

```ruby
class DocumentUploader < CarrierWave::Uploader::Base
  storage :fog
end
```

Keep upload/image logic out of services unless the service is explicitly an import/export workflow.

## strong_migrations / data_migrate

Task: safer schema/data migrations.

Without:

```ruby
add_column :orders, :active, :boolean, default: true, null: false
```

With:

```ruby
add_column :orders, :active, :boolean
change_column_default :orders, :active, true
```

Use data migrations for data changes, not ad hoc console snippets.

## Monitoring

- `yabeda`, `yabeda-*`, `prometheus_exporter`: metrics.
- `mission_control-jobs`, `solid_queue_monitor`: job visibility.

Without:

```ruby
Rails.logger.info("job finished in #{duration}")
```

With:

```ruby
Yabeda.orders.completed.increment(tags: {kind: order.kind})
```

Follow existing metrics names and labels.

## Test / Quality

- `rspec-rails`, `factory_bot_rails`, `webmock`, `stub_env`, `test-prof`, `db-query-matchers`, `shoulda-matchers`.
- `prosopite`: N+1 detection.
- `brakeman`, `bundler-audit`, `rubocop-*`, `database_consistency`, `fasterer`, `reek`: checks.

Without:

```ruby
allow(PaymentManager).to receive(:create).and_return(...)
```

With:

```ruby
stub_request(:post, payment_url).to_return_json(body: response_body)
```

Prefer integration flow + WebMock/contracts over method stubs.
