---
name: repository-knowledge-migrate
description: Inventory and migrate existing repository documentation into the installed Konsierge knowledge protocol. Use for classifying legacy or provider materials and reorganizing them only after the user approves an explicit migration map; use install-repository-knowledge for scaffold installation.
---

# Migrate Repository Knowledge

Мигрируй только репозиторий, в котором уже установлены
`docs/repository-knowledge.md`, `.repository-knowledge.json` и `bin/docs-lint`.
Установленный протокол — источник правил; не подменяй его инструкциями этого
skill.

## Инвентаризация без изменений

1. Прочитай репозиторные инструкции, установленный протокол, конфигурацию и
   source manifest. Проверь текущую ветку и `git status`; сохрани unrelated и
   dirty changes.
2. Запусти `bin/docs-lint --root <repository>`. Используй
   `unmanaged-documentation` как вход в инвентаризацию, но проверь также
   Markdown, PDF, DOCX, JSON/YAML contracts, collections, fixtures и значимые
   root-файлы.
3. Найди потребителей каждого рассматриваемого пути в коде, конфигурации,
   initializers, build scripts, generators, тестах и инструментах публикации.
4. Для каждого артефакта выбери подтверждённый класс:

   - `project-knowledge` можно предложить к перемещению к странице-владельцу;
   - `provider-snapshot` по умолчанию остаётся на месте и только каталогизируется
     после проверки provenance, прав и SHA-256;
   - `provider-derived` требует связи с snapshot, его версией и честного статуса
     соответствия;
   - `project-contract` сохраняет runtime/tooling-bound путь, пока карта не
     включает безопасное обновление всех потребителей;
   - `synthetic-fixture` требует проверки отсутствия secrets, credentials и PII;
   - root-файл остаётся на месте, если его путь или имя требуются инструментом.

Не считай соседство с provider-файлом доказательством происхождения. Если класс,
версия, права или source не подтверждены, пометь значение `unknown` или
`review-required`.

## Обязательная карта и подтверждение

До любого изменения покажи полную предлагаемую карту:

```text
old path | class | target path or keep | owner page | tags | required updates
```

В `required updates` перечисли ссылки, индексы, registry, manifest и найденных
runtime/tooling consumers. Отдельно перечисли:

- snapshots с неизвестным provenance или правами;
- несовпадения версии snapshot и derived-документа;
- restricted материалы;
- credential-like и PII-like fixtures;
- решения, для которых ещё нужен владелец.

Остановись после карты и запроси явное одобрение пользователя. Общая просьба
«мигрировать документацию» разрешает инвентаризацию, но не заменяет одобрение
конкретных `old path -> target path or keep` решений.

## Выполнение после одобрения

1. Перечитай `git status` и карту; не включай новые или изменённые вне карты
   файлы.
2. Делай небольшие смысловые партии. Для согласованного перемещения tracked-файла
   используй `git mv`; не перезаписывай существующую цель.
3. В той же партии исправь относительные ссылки и всех согласованных
   потребителей пути, добавь страницу в индексы, обнови `docs/tags.md` и
   двусторонние code tags только при реальной необходимости.
4. Обнови source manifest для подтверждённых snapshots, derived-документов и
   synthetic fixtures. Для неизменяемого snapshot сравни SHA-256 до и после;
   его bytes не должны измениться.
5. Запусти `bin/docs-lint --root <repository>` после каждой партии. Исправь
   подтверждённые ошибки в пределах партии до перехода к следующей.
6. В конце покажи фактические перемещения, оставленные на месте артефакты,
   предупреждения linter и нерешённые review items.

## Границы безопасности

- Не редактируй provider snapshots и не копируй restricted provider-текст в
  наши страницы.
- Не объявляй материал public, provider-supplied, current или synthetic без
  доказательства.
- Не добавляй реальные DARI pools, credentials, secrets или PII в Git либо
  fixtures.
- Не перемещай runtime/tooling-bound contracts без согласованного обновления и
  проверки всех потребителей.
- Не меняй CI, не коммить, не push и не deploy сверх текущей явной авторизации.
