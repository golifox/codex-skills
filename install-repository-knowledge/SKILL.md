---
name: install-repository-knowledge
description: Install or check the Konsierge repository knowledge structure, rules, and local linter. Use when a repository needs the protocol scaffold or its installation must be verified; use migrate-repository-knowledge for reorganizing existing documentation.
---

# Install Repository Knowledge

Устанавливай минимальный scaffold протокола, не мигрируя существующие
документы. Нормативные правила находятся в
[references/protocol.ru.md](references/protocol.ru.md); установщик помещает их
байтово идентичную копию в целевой репозиторий.

## Выполнение

1. Прочитай инструкции целевого репозитория. Проверь корень Git-репозитория,
   текущую ветку и `git status`; сохрани unrelated и dirty changes.
2. Запусти dry-run из директории этого skill:

   ```bash
   python3 scripts/install.py --repo /absolute/path/to/repository
   ```

3. Если план содержит `CONFLICT`, перечисли конфликтующие пути и остановись.
   Не заменяй расходящиеся owned-файлы и не исправляй malformed marker-блоки
   догадкой.
4. Если изменение целевого репозитория входит в текущую авторизацию, примени
   уже проверенный план:

   ```bash
   python3 scripts/install.py --repo /absolute/path/to/repository --apply
   ```

5. Запусти установленную проверку:

   ```bash
   /absolute/path/to/repository/bin/docs-lint \
     --root /absolute/path/to/repository
   ```

6. Сообщи созданные или обновлённые managed-артефакты, ошибки linter и
   предупреждения. `unmanaged-documentation` — кандидат для отдельной миграции,
   а не ошибка установки.

## Границы

- Не перемещай, не переименовывай и не переписывай существующую документацию.
- Не классифицируй файлы провайдера и не выдумывай provenance при установке.
- Не меняй `.gitlab-ci.yml` или другой CI: протокол использует локальный linter.
- Не создавай пустые domain/architecture/operations каталоги.
- Не коммить, не push и не публикуй изменения без соответствующего явного
  запроса.

Для инвентаризации и перемещения существующих документов используй отдельный
skill `migrate-repository-knowledge`.
