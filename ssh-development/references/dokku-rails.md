# Dokku Rails command patterns

Replace `HOST`, `APP`, and `SERVICE` only after resolving them read-only. Prefix commands with the environment's required terminal wrapper when one exists.

## Connection and deployment identity

```bash
ssh -G HOST | rg '^(hostname|user|port|identityfile|proxyjump) '
ssh -o BatchMode=yes -o ConnectTimeout=12 HOST \
  'id -un; hostname; dokku apps:list'
ssh -o BatchMode=yes -o ConnectTimeout=12 HOST \
  'dokku ps:report APP; dokku git:report APP'
```

Do not infer `APP` from a Git remote until `dokku apps:list` confirms it.

## Interactive Rails console

```bash
rtk proxy ssh -tt -o BatchMode=yes -o ConnectTimeout=12 HOST \
  'dokku enter APP web -- env PROMETHEUS_EXPORTER_PORT=19397 bundle exec rails console'
```

Choose an unused high port for the one-off process. If startup reports `EADDRINUSE`, exit, check for a session-owned stale console, choose another port, and retry. Do not change application config.

Start with:

```ruby
puts 'CONSOLE_OK'
Rails.env
Model.column_names
Model.reflect_on_all_associations.map(&:name)
```

Then emit a small structured result:

```ruby
record = Model.find_by(id: 123)
pp(record&.attributes&.slice('id', 'status', 'created_at', 'updated_at'))
```

Do not print whole records: inspected output can include PII, tokens, encrypted fields, or raw provider payloads. IRB may open a pager for long output; press `q`, then `exit`.

## Rails runner

First try a marker through the app's normal Dokku runner. Treat it only as a transport probe:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=12 HOST \
  "dokku run APP bundle exec rails runner \"puts 'RUNNER_OK'\""
```

If `RUNNER_OK` is absent, stop. Do not interpret exit zero, Rails boot logs, or metrics-server shutdown as query output. `dokku run ... rails runner -` and `dokku enter ... rails runner -` may discard stdin depending on Dokku/runtime versions.

For multiline Ruby, prefer the interactive console. When root Docker access is available, resolve one running web container with the label-filter command under Cleanup, copy its exact ID, and use Docker stdin. Herokuish images require `/exec` to restore the application PATH:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=12 HOST \
  'docker exec -i CONTAINER_ID /exec env PROMETHEUS_EXPORTER_PORT=19398 bundle exec rails runner -' <<'RUBY'
puts 'RUNNER_OK'
# Read-only query follows only after the marker works.
RUBY
```

This preserves stdin across SSH and Docker without embedding Ruby into shell source. If `/exec` is absent or Docker access is unavailable, use the interactive console. Dokku wrappers may reconstruct commands through `eval`, so repeatedly adding quotes or Base64 loaders can still fail silently.

## Read-only PostgreSQL

Prefer Active Record reads in console. Use direct PostgreSQL only when SQL or query-plan evidence is required and the correct linked service is known.

```bash
rtk proxy ssh -tt HOST 'dokku postgres:connect SERVICE'
```

Immediately make the session fail closed:

```sql
\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '5s';
SELECT id, status, created_at FROM records WHERE id = 123;
ROLLBACK;
\q
```

Never print `DATABASE_URL`, use `dokku config:show`, or paste credentials into the command. `BEGIN READ ONLY` blocks writes in that transaction; it does not turn the database user into a permanent read-only role.

## Job evidence

For Solid Queue, inspect the application record first, then select queue rows by exact job class and serialized identifier. Report `created_at`, `scheduled_at`, `finished_at`, execution state, and a short first error line. A sequence of finished jobs with no failed execution may be expected deferral rather than a broken worker.

Read the job implementation and its retry/defer limit. Then evaluate the workflow's ordering/eligibility policy against the persisted blockers. Never enqueue or retry a job during diagnosis.

## Cleanup

Exit console and psql explicitly. If the transport died, find only the session-owned process without inspecting environment variables:

```bash
ssh HOST \
  'docker ps --filter label=com.dokku.app-name=APP --filter label=com.dokku.process-type=web --format "{{.ID}} {{.Status}}"'
ssh HOST 'docker top CONTAINER_ID -eo pid,args'
```

Terminate only a PID proven to belong to the current session. Re-run `docker top` and confirm the normal web server remains.

## Common failures

| Symptom | Meaning | Response |
| --- | --- | --- |
| Dokku app does not exist | Git remote/app name differs from current host | Run `dokku apps:list`; do not guess |
| Exit 0, marker absent | stdin or quoting was lost | Change transport; do not trust output |
| `EADDRINUSE` during boot | one-off exporter port collided | Exit/clean owned process or choose another port |
| Missing model method | local assumption does not match deployed schema | Inspect columns/reflections read-only |
| Console says `production` on stage | Rails runtime mode differs from infrastructure identity | Verify host/app/SHA |
| Long output opens pager | IRB pager captured the terminal | Press `q`, reduce selected fields |
| Finished jobs, state still pending | job may have deferred by policy | Inspect retry limit and older blockers |
| Full inspect prints env | secret boundary was crossed | Stop using inspect; filter container metadata |
