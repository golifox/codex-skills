# Value Objects / POROs

Value object owns pure calculation, normalization, and domain data without persistence side effects.

Value objects are downward extraction: they create smaller domain concepts without adding an upper workflow layer.

## Public API

Value objects should be initialized and then expose named methods.

Do not use `.call`.

Good shape:

```ruby
calculation = OrderPriceCalculation.new(order, now: Time.current)
calculation.total
calculation.currency
calculation.expired?
```

## Responsibilities

- Pure calculation.
- Data normalization.
- Immutable-ish domain values.
- Small parser/formatter when not presentation-specific.
- Idempotency input canonicalization.

## Rules

- No DB writes.
- No external API calls.
- Prefer explicit input over hidden global state.
- Easy to test with `spec_helper`.
- Return value should be clear from method name.
- Prefer immutable data and equality by value when practical.
- Use value objects for concepts with behavior, not for arbitrary hashes.
- Memoization is acceptable for expensive pure calculations.

## Good

```ruby
class OrderPriceCalculation
  attr_reader :order, :now

  def initialize(order, now: Time.current)
    @order = order
    @now = now
  end

  def total
    @total ||= order.items.sum(&:amount_cents)
  end

  def currency
    order.currency
  end

  def expired?
    order.expires_at.present? && order.expires_at <= now
  end
end
```

Value mapper for provider constants:

```ruby
class Tax < BaseValueMapper
  define_mapping(
    none:  {bank: 0, description: 'No VAT'},
    vat_0: {bank: 1, description: 'VAT 0%'}
  )
end

tax = Tax.new(:vat_0)
tax.bank
tax.description
```

```ruby
class CanonicalHash
  attr_reader :value

  def initialize(value)
    @value = value
  end

  def to_h
    canonicalized(value)
  end

  private

  def canonicalized(object)
    case object
    when Hash then object.sort.to_h.transform_values { |v| canonicalized(v) }
    when Array then object.map { |v| canonicalized(v) }
    else object
    end
  end
end
```

## Bad

```ruby
class MoneyTotal
  def self.update_total(order)
    order.update!(total_cents: order.items.sum(&:amount_cents))
  end
end
```

## Checklist

- Pure.
- Deterministic.
- Initialized with explicit input.
- No Rails app dependency unless needed.
- Method names describe returned values.
- Object can be understood without controller/job context.
- No `.call`.
