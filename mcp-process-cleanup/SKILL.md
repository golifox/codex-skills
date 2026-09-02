---
name: mcp-process-cleanup
description: Register and safely stop MCP processes launched by the current Codex session without touching platform-managed or neighboring-session processes.
---

# MCP Process Cleanup

Use this skill when a task launches its own long-lived MCP helper or when a
registered helper must be reaped after the owning session exits.

## Invariants

- Never use broad `pkill`, `killall`, command-pattern killing, or process-group killing.
- Never stop inherited or platform-managed MCP processes. Only processes registered by this skill are eligible.
- Before signalling a PID, verify its UID, process start identity, command fingerprint, and session ownership.
- Treat missing, malformed, tampered, or reused PID records as stale metadata: remove no live process.
- Default orphan inspection to dry-run. Mutating cleanup requires explicit `--execute`.

## Workflow

Use the wrapper when starting an MCP helper:

```bash
~/.codex/skills/mcp-process-cleanup/scripts/mcp-process-cleanup run \
  --session "${CODEX_SESSION_ID:-${OMX_SESSION_ID:-}}" -- command --mcp
```

At task handoff, inspect and then clean the current session:

```bash
~/.codex/skills/mcp-process-cleanup/scripts/mcp-process-cleanup list
~/.codex/skills/mcp-process-cleanup/scripts/mcp-process-cleanup cleanup-session --dry-run
~/.codex/skills/mcp-process-cleanup/scripts/mcp-process-cleanup cleanup-session --execute
```

Inspect orphaned registered processes separately:

```bash
~/.codex/skills/mcp-process-cleanup/scripts/mcp-process-cleanup cleanup-orphans --dry-run
```

Only use `cleanup-orphans --execute` when the task explicitly includes process
cleanup. The script sends `TERM`, waits at most five seconds, then sends `KILL`
to the same revalidated PID if required.

Read [requirements.md](references/requirements.md) when changing the script or
reviewing its safety model.

