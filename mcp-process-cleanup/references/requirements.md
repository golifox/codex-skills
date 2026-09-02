# Captured Requirements

| Requirement ID | Description | Source | Implementation |
|---|---|---|---|
| REQ-001 | Stop only MCP processes registered by the launching session | User | Per-session registry and active-session check |
| REQ-002 | Preserve other Codex, ChatGPT, IDE, and platform MCP processes | User | No pattern-wide signals; unregistered PIDs are ineligible |
| REQ-003 | Protect against PID reuse and tampered metadata | Safety requirement | UID, start identity, and command SHA-256 revalidation |
| REQ-004 | Prefer graceful shutdown | User | `TERM`, bounded five-second wait, exact-PID `KILL` fallback |
| REQ-005 | Make orphan cleanup conservative | User | Owner PID identity proof and dry-run default |
| REQ-006 | Leave an audit trail | User | Stable action/result lines on standard output |
| REQ-007 | Avoid unsafe metadata execution | Safety requirement | Parse allowlisted keys; never source registry files |

The registry is stored under `${CODEX_HOME:-$HOME/.codex}/runtime/mcp-processes`
with directory mode `0700` and record mode `0600`. Tests override the root with
`MCP_CLEANUP_STATE_ROOT` and use harmless processes whose command contains the
explicit marker `mcp-cleanup-test`.

