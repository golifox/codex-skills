---
name: add-symphony
description: "Add a local filesystem-backed Symphony queue to a Codex project, including role-based model and reasoning selection. Use when a user asks to install, bootstrap, or configure Symphony/Codex task execution in a repository."
---

# Add Symphony

Add a local, sequential Codex task runner. It is for repository work only: no external tracker and no automatic deployment. Each task runs in an isolated local Git worktree and must produce a clean task commit before handoff.

## Discover before changing

Read the target repository's `AGENTS.md`, deployment conventions, runtime versions, and current Git state. Check whether `ops/symphony`, `WORKFLOW.md`, or `.symphony` already exist. Preserve an existing implementation unless the user asked to migrate it.

Confirm the task source, working directory, and runtime before creating files. Use the repository's pinned Node runtime if one exists; otherwise require Node 22 or later. Keep `.symphony/` runtime data ignored by Git and keep versioned configuration under `ops/symphony/`.

## Install

Use the layout and schemas in [layout reference](references/layout.md).

1. Add a filesystem queue runner under `ops/symphony/`, its tests, `README.md`, and a versioned `roles.json`.
2. Add `WORKFLOW.md` with `task_worktree` mode, one concurrent agent, a filesystem queue, a Codex command ending in stdin marker `-`, and `roles_path` pointing at the role map. Resolve the repository's integration base instead of assuming `origin/dev` when it differs.
3. Add `.symphony/` to `.gitignore`; do not commit task runtime data, logs, leases, tokens, or provider credentials.
4. Make every queued task use an optional `role`. Omitted role must safely fall back to `default_role`; an unknown role must fail before a task starts. Do not put model or reasoning overrides inside task files.
5. Make the runner create or reuse a local branch named after the task identifier below `.symphony/worktrees/`. A successful run must create at least one commit, leave a clean worktree, and keep the baseline commit as an ancestor. Persist `branch` and `commit_sha` in the handoff record. Never push task branches.
6. Run runner unit tests, including the commit gate, and validate every task JSON plus role reference. Run a single dry pass only when it cannot consume a real task; never use a production task as a smoke test.

The runner must inject `-m <model>` and `-c model_reasoning_effort=<effort>` from the role map before its stdin prompt marker. Log the chosen role/model/effort in `run_started`, but never log task secrets, tokens, headers, or prompt contents.

## Existing shared-checkout migration

Do not activate `task_worktree` while a task lease is active. Existing dirty changes do not appear in new worktrees: inventory and preserve them before migration, and do not mark old handoffs as committed. Update runner, tests, workflow, and documentation together. Restart an installed service only after explicit authorization and only when no lease exists.

## Default role policy

Install this mapping unless the user specifies another policy:

- `scout`: `gpt-5.6-luna`, `low` — inventory, characterization, docs, fixtures.
- `builder`: `gpt-5.6-terra`, `medium` — normal bounded implementation slices.
- `specialist`: `gpt-5.6-sol`, `high` — auth, realtime, security, migration, concurrency.
- `reviewer`: `gpt-5.6-sol`, `xhigh` — reviews, release readiness, difficult diagnosis.
- `verifier`: `gpt-5.6-terra`, `medium` — CI, E2E, staging evidence.

Use `max` only when the user explicitly requests a quality-first exceptional task. The global Codex default remains a fallback for executions outside Symphony.

## Service lifecycle

Generate a project-specific systemd unit only when systemd is available. Its `ExecStart` must use absolute paths, the pinned Node binary, the target repository, and `--workflow <absolute path>/WORKFLOW.md`. Never install, enable, restart, or stop a service without the user's explicit authorization. If a runner is active, do not restart it until its lease is gone.

## Delivery

Report versioned files, role mapping, validation commands/results, whether a service was merely generated or actually enabled, and the next safe command. Keep project changes separate from host-level systemd changes.
