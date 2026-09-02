# ADR Format

Preserve an existing repository convention. When none exists, store ADRs in `docs/adr/` with sequential four-digit names such as `0001-event-sourced-orders.md`.

Write the entire ADR, including headings and explanations, in Russian. Preserve API names, classes, commands, parameters, and other technical identifiers in their original form.

## Template

```markdown
# ADR NNNN: Краткое название решения

- Статус: Предложено | Принято | Отклонено | Заменено ADR NNNN
- Дата: YYYY-MM-DD

## Контекст

Проблема, ограничения и подтверждённое текущее состояние.

## Решение

Выбранный подход и его существенные правила.

## Последствия

Положительные эффекты, компромиссы, риски и операционные обязанности.

## Альтернативы

Рассмотренные варианты и причины отказа.

## Критерии приёмки

Проверяемые условия последующей реализации.
```

That's it. An ADR can be a single paragraph. The value is in recording *that* a decision was made and *why*, not in filling out sections.

Omit `Альтернативы` when no alternatives were actually discussed. Omit `Критерии приёмки` when no implementation follows from the ADR.

## Numbering

Scan `docs/adr/` for the highest existing number and increment by one.

## When to record an ADR

All three of these must be true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If a decision is easy to reverse, skip it: you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

### What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library: just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite. These stop the next engineer from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and picked REST for subtle reasons, record it; otherwise someone will suggest GraphQL again in six months.
