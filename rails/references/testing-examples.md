# Ruby/Rails TDD Examples

Use this reference when writing or reviewing concrete RSpec and FactoryBot patterns.

## Contents

- [Test Structure](#test-structure)
- [Common assertions](#common-assertions)
- [Factories](#factories)
- [RSpec Structure](#rspec-structure)
- [Expensive Specs](#expensive-specs)
- [Shared Examples / Contexts](#shared-examples--contexts)
- [Spec Helpers](#spec-helpers)

## Test Structure (Arrange-Act-Assert)

- prepare test data (let, let_it_be, include_context)
- act (call subject)
- assert (expectation)

## Common Assertions

```ruby
it { is_expected.to be_true } 
it 'enqueues a job' do
    will_be_expected.to have_enqueued_job(described_class).with(*service_keys)
end

it 'creates user with correct attributes' do
  expect(user).to have_attributes(...)
end

it 'creates order with correct description' do
  expect(order.description).to match(/#{order.id}/)
  expect(order.description).to include(order.id)
end

expect(response).to have_http_status(200)

it { will_be_expected.to change { order.reload.payments_count }.to(1) }

expect(a_request(:patch, create_users_uri)).to have_been_made.at_least_once
```

## Mocks
Stub http requests in shared_context primary (if maybe uses by another tests):

```ruby
RSpec.shared_context 'crm create payment mock' do
  let(:crm_url) { Konsierge::HTTP.config.crm.url }
  let(:crm_create_payment_uri) { URI.join(crm_url, 'api/system/v1/payments') }
  let(:payment_id) { Faker::Number.number(digits: 4) }

  before do
    stub_request(:post, crm_create_payment_uri)
      .to_return(status: 200, body: {id: payment_id, result: {id: payment_id}, error: nil}.to_json)
  end
end

RSpec.shared_context 'crm create payment error mock' do
  let(:crm_url) { Konsierge::HTTP.config.crm.url }
  let(:crm_create_payment_uri) { URI.join(crm_url, 'api/system/v1/payments') }

  before do
    stub_request(:post, crm_create_payment_uri)
      .to_return(status: 400, body: {result: nil, error: 'Payment create error!'}.to_json)
  end
end
```

Use contract payload matching for request:

```ruby
stub_request(:post, crm_v1_dragonpass_order_create_request_uri)
.with do |request|
    payload = JSON.parse(request.body)
    expect(payload).to match_contract_schema('travelmart/crm/dragonpass_order/create_request_schema')
end
.to_return(status: 200, body: {result: {id: request_id}}.to_json)
```


```
Mock these:                    Don't mock these:
                               ├── Internal utility functions
├── HTTP requests              ├── Business logic
├── File system operations     ├── Data transformations
├── External API calls         ├── Validation functions
└── Time/Date (when needed)    └── Pure functions
```

## Factories

Good: light factory with explicit role trait.

```ruby
factory :user do
  email { "user-#{SecureRandom.hex(4)}@example.test" }

  trait(:admin) { role { 'admin' } }
end

RSpec.describe UserPolicy do
  let(:user) { build_stubbed(:user, :admin) }
  let(:record) { build_stubbed(:article) }

  it { expect(described_class.new(user, record).update?).to be(true) }
end
```

Bad: default factory creates a hidden expensive graph.

```ruby
factory :user do
  after(:create) do |user|
    create(:account, user:)
    create(:profile, user:)
    create_list(:notification, 10, user:)
  end
end

let(:user) { create(:user) }
```

Good: pure object behavior uses `build_stubbed`.

```ruby
RSpec.describe InvoiceTotal do
  let(:invoice) do
    build_stubbed(:invoice, line_items: [
      build_stubbed(:line_item, amount_cents: 1000),
      build_stubbed(:line_item, amount_cents: 500)
    ])
  end

  it { expect(described_class.call(invoice)).to eq(1500) }
end
```

Bad: pure behavior creates unnecessary persisted graph.

```ruby
let(:invoice) { create(:invoice, :with_customer, :with_subscription, :with_payment_method, :with_line_items) }
```

## RSpec Structure

Good: public method, named subject, visible setup, observable behavior.

```ruby
RSpec.describe OrderService do
  describe '.create' do
    subject { described_class.create(params) }

    let(:params) { attributes_for(:order) }

    context 'with valid params' do
      it will_be_expected.to change(Order, :count).by(1)
    end

    context 'without customer id' do
      let(:params) { super.merge(customer_id: nil) }

      it will_be_expected.to raise_error(Orders::Create::ValidationError)
    end
  end
end
```

Bad: generic names do not describe behavior.

```ruby
RSpec.describe Orders::Create do
  describe 'tests' do
    context 'case 1' do
      it('works') {}
    end
  end
end
```

Good: cheap pure specs can keep failure points precise.

```ruby
RSpec.describe SlugNormalizer do
  it { expect(described_class.call('Hello World')).to eq('hello-world') }
  it { expect(described_class.call('Hello, World!')).to eq('hello-world') }
end
```

or use input-expect matrix

```ruby
RSpec.describe SlugNormalizer do
  [
    ['Hello World', 'hello-world],
    ['Hello, World!', 'hello-world']
  ].each do |input, expected|
    it { expect(described_class.call(input)).to eq(expected) }
  end
end
```

## Expensive Specs

Good: one request performs the expensive action once and checks the visible contract.

```ruby
RSpec.describe 'POST /api/v1/orders' do
  subject(:request) { post '/api/v1/orders', params:, headers: }

  it 'creates order, returns valid response, and enqueues export' do
    expect { request }.to change(Order, :count).by(1).and have_enqueued_job(ExportOrderJob)
    expect(response).to have_http_status(201)
    expect(response.parsed_body).to match_json_schema('order')
    expect(Order.last).to have_attributes(status: 'pending', customer_id: customer.id)
  end
end
```

Bad: repeated request mutates state multiple times and can hide failures.

```ruby
it('returns created') { post '/api/v1/orders', params:; expect(response).to have_http_status(201) }
it('creates order') { post '/api/v1/orders', params:; expect(Order.count).to eq(1) }
it('enqueues job') { post '/api/v1/orders', params:; expect(ExportOrderJob).to have_been_enqueued }
```

## Shared Examples / Contexts

Good: shared example captures one behavior contract.

```ruby
RSpec.shared_examples 'searchable by query' do
  it 'returns matching records first' do
    matching = create(factory_name, title: 'Ruby testing')
    create(factory_name, title: 'Python testing')

    expect(described_class.search('Ruby')).to eq([matching])
  end
end
```

Bad: shared example bundles unrelated checks.

```ruby
RSpec.shared_examples 'everything works' do
  it 'does unrelated checks' do
    expect(subject.valid?).to be(true)
    expect(subject.to_json).to include('id')
    expect(subject.destroy).to be_truthy
  end
end
```

Good: shared context contains a clear external boundary fake.

```ruby
RSpec.shared_context 'payment gateway approves charge' do
  before do
    stub_request(:post, %r{/charges}).to_return_json(status: 200, body: {id: 'txn_123'})
  end
end
```

Bad: shared context hides a whole unrelated world.

```ruby
RSpec.shared_context 'full order world' do
  let!(:admin) { create(:user, :admin) }
  let!(:customer) { create(:customer, :with_profile, :with_subscription) }
  let!(:order) { create(:order, :with_items, :with_payment, :with_shipments) }
  before { allow(Everything).to receive(:call).and_return(true) }
end
```

## Spec Helpers

Good: pure Ruby behavior uses `spec_helper`.

```ruby
require 'spec_helper'

RSpec.describe MoneyTotal do
  it { expect(described_class.call([100, 50])).to eq(150) }
end
```

Bad: pure behavior loads Rails by habit.

```ruby
require 'rails_helper'
```

## Test Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|---|---|---|
| Testing implementation details | Breaks on refactor | Test inputs/outputs |
| Snapshot everything | No one reviews snapshot diffs | Assert specific values |
| Shared mutable state | Tests pollute each other | Setup/teardown per test |
| Testing third-party code | Wastes time, not your bug | Mock the boundary |
| Skipping tests to pass CI | Hides real bugs | Fix or delete the test |
| Using `skip: true/xit/pending` permanently | Dead code | Remove or fix it |
| Overly broad assertions | Doesn't catch regressions | Be specific |