---
name: ssh-development
description: Use when investigating or operating a remote Rails application over SSH, especially on Dokku, with rails runner, Rails console, logs, job queues, or read-only PostgreSQL access.
---

# SSH Development

## Core rule

Establish the remote topology first, then collect the smallest read-only evidence that answers the question. An SSH command returning zero is not proof: require an explicit marker and expected records.

Treat diagnosis as read-only unless the user separately authorizes a mutation. Do not retry jobs, invoke state transitions, save records, change Dokku config, restart processes, or run SQL writes while investigating.

## Resolve the four names

Confirm these independently before running application code:

1. SSH alias and resolved host: `ssh -G <alias>`.
2. Server identity: `id -un` and `hostname`.
3. Dokku app: `dokku apps:list`; a Git remote path may be stale or differently named.
4. Process type: `dokku ps:report <app>`; Rails commands normally enter `web`.

Use configured SSH aliases instead of copying hostnames, users, ports, or key paths into commands.

## Investigation order

1. Verify host, app, deployment SHA, and running processes.
2. Read local model/service/job code before assuming remote associations or columns.
3. Inspect the primary record and its persisted workflow rows.
4. Inspect step attempts, leases, failure codes, and queue records.
5. Compare persisted state with the policy that decides whether execution may proceed.
6. State the proven blocker and stop before recovery actions.

For cancellation, payment, or other externally effective workflows, a completed job only proves that the job returned. It does not prove the provider effect succeeded.

## Rails console

Prefer an interactive console for multi-step exploration because it avoids nested SSH/Dokku/Ruby quoting. Use `rtk proxy ssh -tt` so the local output wrapper preserves the PTY. Set a unique temporary metrics port if application boot starts an exporter.

The prompt may say `production` on a staging app because staging commonly uses `RAILS_ENV=production`. Trust the verified SSH host, Dokku app, and deployment SHA for environment identity.

Inside console, begin with a marker, inspect `column_names` or reflections when uncertain, and use only reads such as `find_by`, `where`, `pluck`, `count`, `group`, and `exists?`. Select explicit non-sensitive fields. Exit explicitly and verify no console process remains.

## Runner and shell quoting

Use runner for short, deterministic probes. Test transport first with `puts 'RUNNER_OK'`. Some Dokku commands silently discard stdin from `rails runner -`; exit zero plus bootstrap logs is a failed probe when the marker is absent.

Do not keep adding escaping layers after quoting breaks. Switch to interactive console, or use the verified Docker stdin fallback from the reference when host access permits it. Never interpolate secrets or untrusted values into shell/Ruby source.

Read [Dokku Rails command patterns](references/dokku-rails.md) before running a remote console, runner, direct SQL session, or queue investigation.

## Secret-safe evidence

Never run or print broad environment/config inspection such as `env`, `dokku config:show`, or full Docker/Dokku inspect. These can expose database URLs, API keys, and encryption secrets even when a wrapper masks most values.

Use Docker label filters when a container ID is needed. Output only app name, process type, container ID, status, and the exact application fields required for the incident. Avoid PII and raw payloads.

## Stop conditions

Stop and report when evidence reaches a recovery boundary: unknown provider outcome, payment ambiguity, expired lease after dispatch, support-required state, or a blocked older operation. Read-only investigation does not authorize replay, deletion, status edits, reservation release, or direct provider calls.

Before finishing, close every console/psql session created by the investigation and verify cleanup without restarting the app.
