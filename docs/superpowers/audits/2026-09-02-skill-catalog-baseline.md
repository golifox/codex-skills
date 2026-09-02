# Baseline каталога Codex skills

Дата: 2026-09-02
Ветка: `skill-catalog-refactor`
Codex: `0.152.1`

## Метрики до изменений

- Пользовательские skills в `~/.codex/skills`: 76.
- Размер пользовательских `SKILL.md`: 327119 bytes.
- Размер их YAML descriptions: 17679 bytes.
- Legacy skills в `~/.agents/skills`: 9.
- System skills: 6.
- Skills, найденные в plugin cache: 98. Cache включает неактивные и старые версии, поэтому это не effective count.
- Активные plugins: 10.
- Активные MCP: 10.
- Agent TOML в `~/.codex/agents`: 20, включая 3 Codebase Memory agents.
- CBM hooks: 2 команды плюс Windows-варианты.
- Codebase Memory: `0.10.8`; `auto_index=true`, `auto_watch=true`, `ui_enabled=true`.
- Одновременно активны три code-intelligence MCP: `codegraph`, `codemem`, `codebase-memory-mcp`. `codemem` принадлежит пользователю и сохраняется.

## Правило evidence

`explicit` означает исходный пользовательский запрос или durable memory. `focused` означает чтение skill в сессии с узким набором skills и соответствующим типом задачи. Массовые installation/audit/catalog reads не считаются использованием.

## Пользовательские skills

| Skill | Bytes | Desc | Decision | Evidence |
| --- | ---: | ---: | --- | --- |
| `add-symphony` | 4313 | 220 | keep | approved core; installation workflow |
| `ai-slop-cleaner` | 7416 | 108 | keep | explicit global cleanup workflow |
| `api-design` | 1660 | 156 | merge | overlaps OpenAPI and API documentation |
| `api-documentation` | 3466 | 226 | keep | explicit API contract work |
| `architecture-review` | 794 | 135 | keep | explicit global codebase review request |
| `auditing-access-control` | 5879 | 228 | merge | overlaps security hardening |
| `backend-patterns` | 1658 | 142 | archive | no substantive use found |
| `bash-script-generator` | 6812 | 88 | keep | focused workflow read |
| `bash-script-validator` | 7642 | 68 | keep | focused workflow read |
| `brainstorming` | 15456 | 198 | keep | approved design gate |
| `caveman` | 3916 | 392 | keep | explicit repeated requests |
| `checking-owasp-compliance` | 4341 | 202 | archive | no substantive use found |
| `checkyourself` | 6084 | 380 | archive | no substantive use found |
| `code-review-and-quality` | 3204 | 230 | merge | overlaps code-review |
| `code-review` | 6589 | 417 | keep | explicit review requests |
| `code-simplification` | 1766 | 244 | keep | explicit refactor requests |
| `codebase-design` | 6446 | 265 | keep | focused architecture workflow |
| `codebase-memory` | 5137 | 452 | keep | explicitly requested replacement MCP |
| `coding-standards` | 1694 | 178 | merge | overlaps Rails and code review |
| `commit-message` | 6002 | 349 | keep | explicit repeated requests |
| `create-adr` | 5573 | 207 | keep | explicit ADR work |
| `database-migrations` | 1735 | 213 | keep | repeated migration tasks |
| `deployment-patterns` | 1687 | 165 | keep | focused deployment workflow |
| `dockerfile-generator` | 1612 | 88 | keep | focused workflow read |
| `dockerfile-validator` | 9250 | 76 | keep | focused workflow read |
| `documentation-lookup` | 4888 | 212 | merge | duplicates Context7 routing |
| `domain-modeling` | 3331 | 150 | keep | approved repository knowledge core |
| `encrypting-and-decrypting-data` | 4284 | 186 | archive | no substantive use found |
| `error-handling` | 1679 | 167 | keep | focused workflow read |
| `find-skills` | 5446 | 303 | archive | no substantive use found; system installer remains |
| `frontend-design` | 8260 | 204 | archive | no substantive use found |
| `github-actions-generator` | 1637 | 105 | archive | no substantive use found |
| `github-ops` | 4615 | 327 | keep | retained operational capability |
| `gitlab-ci-validator` | 6461 | 73 | keep | focused workflow read |
| `gitops-workflow` | 5929 | 257 | archive | no substantive use found |
| `helm-generator` | 1599 | 87 | archive | no substantive use found |
| `idea-refine` | 2621 | 259 | merge | overlaps interview and brainstorming |
| `improve-codebase-architecture` | 5993 | 125 | archive | no substantive use found |
| `incident-runbook-templates` | 5463 | 485 | keep | focused workflow read |
| `incremental-implementation` | 2156 | 223 | keep | explicit Rails delivery workflow |
| `install-repository-knowledge` | 2982 | 249 | keep | explicit implementation and reuse |
| `interview-me` | 2699 | 249 | keep | explicit repeated requests |
| `it-operations` | 1753 | 243 | keep | focused operational workflow |
| `k8s-debug` | 1623 | 121 | archive | no substantive use found |
| `k8s-yaml-generator` | 8866 | 110 | archive | no substantive use found |
| `konsierge-git-flow` | 9598 | 344 | keep | explicit repeated delivery use |
| `konsierge-mcp-incident` | 5813 | 382 | keep | explicit incident use |
| `konsierge-mcp` | 2036 | 526 | keep | explicit repeated MCP work |
| `konsierge-project-setup` | 10360 | 527 | keep | focused Konsierge setup workflow |
| `logql-generator` | 1612 | 98 | archive | no substantive use found |
| `loki-config-generator` | 1618 | 92 | archive | no substantive use found |
| `mcp-process-cleanup` | 1878 | 144 | keep | required session cleanup boundary |
| `migrate-repository-knowledge` | 6194 | 291 | keep | explicit implementation and reuse |
| `mysql-patterns` | 1634 | 122 | archive | no substantive use found; projects use PostgreSQL |
| `nuke-on-rails` | 1928 | 418 | keep | explicitly invoked at least twice |
| `openapi-design-first` | 8219 | 228 | keep | explicit API design work |
| `orchestrating-agent-work` | 5320 | 158 | keep | explicit global workflow |
| `planning-and-task-breakdown` | 2729 | 231 | merge | overlaps orchestration |
| `postgres-patterns` | 3796 | 125 | keep | focused PostgreSQL work |
| `prerelease` | 5174 | 502 | keep | explicit repeated gem releases |
| `promql-validator` | 1603 | 87 | keep | focused workflow read |
| `rails` | 2300 | 354 | keep | primary project stack |
| `rtk` | 1115 | 240 | keep | explicit global shell workflow |
| `sast-configuration` | 5441 | 234 | archive | no substantive use found |
| `security-and-hardening` | 3812 | 250 | keep | explicit security work |
| `senior-qa` | 4461 | 371 | keep | focused QA workflow |
| `spec-driven-development` | 3168 | 235 | merge | overlaps brainstorming |
| `ssh-key-manager` | 2051 | 284 | keep | focused workflow read |
| `stride-analysis-patterns` | 2452 | 169 | archive | no substantive use found |
| `tdd-workflow` | 9775 | 171 | merge | explicitly used, but overlaps retained TDD |
| `temporal-python-testing` | 4949 | 236 | archive | no substantive use found |
| `test-driven-development` | 2855 | 254 | keep | explicit TDD use |
| `upgrade-ruby-version` | 2614 | 253 | keep | explicit Ruby upgrades |
| `using-agent-skills` | 3061 | 261 | merge | overlaps orchestration and system routing |
| `web-design-guidelines` | 1231 | 184 | archive | no substantive use found |
| `youtrack-task-runner` | 5905 | 346 | keep | explicit repeated ticket workflow |

## Legacy source decisions

- `brainstorming`, `code-review`, `codebase-design`, `domain-modeling`, `frontend-design`, `improve-codebase-architecture`, `web-design-guidelines`, and `codebase-memory` in `~/.agents/skills` are byte-identical duplicates: archive.
- `context7-mcp` is unique in legacy source: move to `~/.codex/skills`, then archive `documentation-lookup` after checking unique rules.

## Plugin decisions

| Plugin | Decision | Evidence |
| --- | --- | --- |
| `superpowers@openai-curated` | keep | multiple substantive workflow uses |
| `browser@openai-bundled` | keep | browser workflow available and used |
| `chrome@openai-bundled` | keep | focused authenticated-browser use |
| `codex-app-tools@openai-bundled` | keep | runtime dependency for app tools |
| `codex-security@openai-curated` | keep | security tooling without duplicate skill catalog |
| `template-creator@openai-primary-runtime` | remove | no substantive use found |
| `sites@openai-bundled` | remove | no substantive use found |
| `visualize@openai-bundled` | remove | no substantive use found |
| `cc-safety-net@cc-marketplace` | remove | no substantive use found |
| `codemem@codemem` | keep | user-owned MCP; explicit preservation instruction |

Disabled plugins remain out of effective activation and are not removal targets unless they still contribute skills after restart.

## Expected reduction

Before plugin contributions, consolidation and archive remove 29 custom catalog entries: 10 merge sources and 19 unused skills. Legacy cleanup removes 9 duplicate/alternate-source entries while preserving Context7 in the authoritative root. Plugin removal eliminates additional contributed descriptions. Exact effective after-metrics require a fresh Codex session.
