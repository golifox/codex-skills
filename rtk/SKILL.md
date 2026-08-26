---
name: rtk
description: Run terminal commands through RTK, a token-efficient CLI proxy that condenses noisy command output. Use whenever executing shell commands, inspecting logs, building, testing, or running Git commands in environments where `rtk` is installed.
---

# RTK

Prefix terminal commands with `rtk` to retain important output while reducing repeated or noisy lines.

## Use

- Run `rtk <command>` for ordinary commands.
- Run `rtk env NAME=value <command>` when setting environment variables.
- Run `rtk proxy <command>` only when complete, unfiltered output is required for diagnosis.
- Run `rtk --version` and `rtk gain` to verify the installation and inspect savings.

## Keep execution safe

- Preserve the command's normal exit status and review errors before continuing.
- Do not use RTK to bypass approval, sandbox, authentication, or permission controls.
- Use a literal command rather than complex shell quoting when RTK parsing becomes ambiguous.

## Examples

```bash
rtk git status --short
rtk bun test
rtk env PORT=3010 bun run dist/main.js
rtk proxy docker compose logs codex-web
```
