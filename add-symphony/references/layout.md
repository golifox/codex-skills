# Symphony layout and validation

## Versioned repository files

```text
WORKFLOW.md
ops/symphony/
  README.md
  runner.mjs
  roles.json
  test/runner.test.mjs
  systemd/<project>-symphony.service
```

Runtime-only files belong below `.symphony/` and must be ignored:

```text
.symphony/tasks/*.json
.symphony/logs/runner.jsonl
.symphony/leases/*.json
```

Tasks can be versioned only when the repository deliberately treats them as a backlog. Otherwise the whole `.symphony/` directory stays runtime-only.

## Workflow configuration

The JSON front matter must specify a local filesystem tracker, active states,
one `shared_checkout` agent, and a Codex command with stdin marker. Example:

```json
{
  "tracker": {
    "kind": "filesystem",
    "provider": { "queue_path": ".symphony/tasks" },
    "active_states": ["Ready", "RetryQueued"],
    "terminal_states": ["Handoff", "Blocked", "Cancelled"],
    "required_labels": ["codex"]
  },
  "workspace": {
    "root": ".",
    "mode": "task_worktree",
    "base_ref": "origin/dev",
    "worktree_root": ".symphony/worktrees"
  },
  "agent": { "max_concurrent_agents": 1, "max_retry_backoff_ms": 300000 },
  "codex": {
    "command": "codex exec --approve-for-me --color never -",
    "roles_path": "ops/symphony/roles.json",
    "turn_timeout_ms": 3600000,
    "stall_timeout_ms": 300000
  }
}
```

## Role map schema

```json
{
  "default_role": "builder",
  "roles": {
    "scout": { "model": "gpt-5.6-luna", "model_reasoning_effort": "low" },
    "builder": { "model": "gpt-5.6-terra", "model_reasoning_effort": "medium" },
    "specialist": { "model": "gpt-5.6-sol", "model_reasoning_effort": "high" },
    "reviewer": { "model": "gpt-5.6-sol", "model_reasoning_effort": "xhigh" },
    "verifier": { "model": "gpt-5.6-terra", "model_reasoning_effort": "medium" }
  }
}
```

Allowed efforts: `none`, `low`, `medium`, `high`, `xhigh`, `max`. Validate model
names as safe command-line atoms. Reject an unknown role rather than silently
falling back.

## Task shape

```json
{
  "id": "local-feature-name",
  "identifier": "KON-0000-feature-name",
  "title": "Short imperative title",
  "description": "Bounded outcome, acceptance checks, and scope exclusions.",
  "priority": 10,
  "sequence": 10,
  "queued_at": "2026-08-21T00:00:00.000Z",
  "state": "Ready",
  "role": "builder",
  "labels": ["codex", "frontend"]
}
```

`role` is optional; omission uses `default_role`. `Blocked` tasks must explain
the exact approval or external condition needed to become `Ready`.

For `task_worktree`, `identifier` must also be a safe local branch name such as
`KON-0000-feature-name`. Runner creates or reuses that branch, records its
baseline SHA, and accepts `Handoff` only when HEAD advanced, baseline remains an
ancestor, and `git status --porcelain` is empty. The task record then receives
`branch` and `commit_sha`. Merge and push remain separate delivery work.

## Minimum verification

```sh
node --test ops/symphony/test/*.test.mjs
jq -e '(.default_role | type == "string") and (.roles | type == "object")' ops/symphony/roles.json
jq -s 'all(.[]; (.role // "builder") as $role | ["scout", "builder", "specialist", "reviewer", "verifier"] | index($role) != null)' .symphony/tasks/*.json
```

Adapt commands to the repository runtime. Do not run the production worker to
test installation. A live service may be restarted only with explicit approval,
after confirming no active shared-checkout lease exists.
