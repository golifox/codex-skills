# Рефакторинг каталога Codex skills

Дата: 2026-09-02
Статус: утверждённое направление, ожидает проверки владельцем

## Цель

Уменьшить постоянный контекст Codex и удалить редко используемые skills. Узкий специализированный skill остаётся активным только при наличии хотя бы одного подтверждённого содержательного применения. Массовое чтение при установке, аудите или валидации применением не считается.

## Ограничения

- Сохранить существующие несвязанные и незакоммиченные изменения.
- Не редактировать plugin cache вручную.
- Сначала перемещать удаляемые материалы в датированный архив, затем проверять работу Codex.
- Не считать plugin cache, старую версию пакета или одно чтение каталога доказательством использования.
- После каждого этапа измерять фактический активный каталог после перезапуска Codex.

## Источники skills

`~/.codex/skills` становится единственным каталогом собственных skills.

Legacy-каталог `~/.agents/skills` архивируется. Byte-identical копии не переносятся. Уникальный `context7-mcp` переносится в `~/.codex/skills`, после чего перекрывающий его `documentation-lookup` архивируется.

Системные skills в `~/.codex/skills/.system` не редактируются. Plugin cache не редактируется напрямую: ненужные плагины удаляются или отключаются через поддерживаемую конфигурацию и менеджер плагинов.

## Codebase Memory MCP

CodeGraph заменяется на `codebase-memory-mcp` версии 0.10.8.

Остаются только:

- MCP entry `codebase-memory-mcp`;
- один `codebase-memory/SKILL.md` в `~/.codex/skills`.

Автоматически добавленные installer-ом дублирующий skill в `~/.agents/skills`, глобальный блок в `~/.codex/AGENTS.md`, три graph-agent и два context-injection hook архивируются или удаляются. `auto_index` и `auto_watch` должны быть выключены; проекты индексируются явно.

CodeGraph удаляется из `config.toml` только после MCP smoke-проверки Codebase Memory. Его executable/package и локальные `.codegraph` данные сначала архивируются. Существующие `.codegraph` изменения внутри project worktree не трогаются автоматически.

Проверка замены:

1. Binary сообщает ожидаемую версию.
2. MCP проходит `initialize` и `tools/list`.
3. Доступны ожидаемые 15 tools.
4. Тестовый проект явно индексируется и отвечает на структурный запрос.
5. После удаления CodeGraph новый сеанс Codex не содержит его MCP entry.

## Активное ядро

Сохраняются:

- `rails`, `rtk`, `caveman`;
- Konsierge workflows, `youtrack-task-runner`, `add-symphony`;
- `openapi-design-first`, `api-documentation`;
- `create-adr`, `domain-modeling`, repository-knowledge skills;
- `prerelease`, `commit-message`;
- `orchestrating-agent-work`, `incremental-implementation`;
- по одному основному TDD, code-review и security skill;
- узкие skills с подтверждённым содержательным применением.

## Консолидация

Перед архивированием уникальные полезные правила переносятся в указанный основной skill:

- `documentation-lookup` -> `context7-mcp`;
- `tdd-workflow` -> `test-driven-development`;
- `code-review-and-quality` -> `code-review`;
- `auditing-access-control` -> `security-and-hardening`;
- `planning-and-task-breakdown`, `spec-driven-development`, `idea-refine`, `using-agent-skills` -> `brainstorming`, `orchestrating-agent-work`, `incremental-implementation`;
- `api-design` -> `openapi-design-first`, `api-documentation`;
- `coding-standards` -> `rails`, `code-review`.

Каждый основной `SKILL.md` должен содержать только trigger metadata и минимальный workflow. Подробные справочные материалы переносятся в `references/` и загружаются по необходимости.

## Кандидаты на архивирование

Если последняя проверка истории не обнаружит содержательного применения, архивируются:

- `backend-patterns`, `mysql-patterns`;
- `checking-owasp-compliance`, `stride-analysis-patterns`, `encrypting-and-decrypting-data`, `sast-configuration`, `nuke-on-rails`, `checkyourself`;
- `github-actions-generator`, `gitops-workflow`, `helm-generator`;
- `k8s-debug`, `k8s-yaml-generator`;
- `logql-generator`, `loki-config-generator`;
- `temporal-python-testing`;
- `frontend-design`, `improve-codebase-architecture`, `web-design-guidelines`;
- `find-skills`.

Последняя проверка должна связывать skill с исходным пользовательским запросом. Техническое чтение файла без применения workflow недостаточно.

## Плагины

Сохраняются `superpowers`, Chrome/Browser и другие runtime-плагины с подтверждённым применением.

Неиспользуемые Figma, Sites, Visualize, Template Creator и дубли Safety Net удаляются из регистрации и управляемого cache поддерживаемым способом. Отключение считается успешным только если их skills исчезли из каталога нового сеанса Codex.

## Порядок реализации

1. Снять воспроизводимый baseline: активные skills, plugins, MCP, agents, hooks и размеры trigger descriptions.
2. Подготовить датированный архив и manifest с исходными путями и SHA-256.
3. Минимизировать интеграцию Codebase Memory и проверить MCP.
4. Удалить CodeGraph из активной конфигурации и проверить новый сеанс.
5. Убрать legacy-дубли источников.
6. Перенести уникальные правила и консолидировать перекрывающиеся skills.
7. Архивировать неподтверждённые узкие skills.
8. Удалить или отключить неиспользуемые плагины поддерживаемым способом.
9. Валидировать каждый оставшийся собственный skill.
10. Перезапустить Codex и сравнить итоговый каталог, размер контекста и MCP tools с baseline.

## Критерии готовности

- Один собственный skill имеет один активный источник.
- CodeGraph отсутствует в активной MCP-конфигурации.
- Codebase Memory работает как MCP, без глобального context injection.
- Нет автоматически добавленных дублей `codebase-memory`.
- Каждый оставшийся узкий skill имеет зафиксированное доказательство применения.
- Все оставшиеся собственные skills проходят validator.
- Архив содержит manifest и позволяет точечно восстановить любой удалённый объект.
- Ни один существующий несвязанный dirty-файл не изменён и не попал в commit.
