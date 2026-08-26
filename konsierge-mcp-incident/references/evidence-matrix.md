# MCP and Marketplace Evidence Matrix

Use only the sections relevant to the incident. Record exact timestamps and environment for every artifact.

| Boundary | Strong evidence | Common false conclusion | Useful checks |
| --- | --- | --- | --- |
| Conversation | Raw user/assistant messages and ordered history | Assistant text proves a tool ran | Match messages to tool-call IDs and runtime trace |
| Model decision | Tool call name, exact arguments, model request/tool catalog | Producer received what user meant | Compare literal user text, supplied context, and arguments |
| Trusted context | Persisted allowlisted context after each tool result | Full provider result is safely remembered | Inspect only IDs, selections, and bounded schema-valid values |
| Consumer catalog | Effective tool schema, metadata, digest version, access policy | Producer registration makes tool immediately visible | Compare consumer digest/sync state per actor and environment |
| Executor | Schema validation, dispatch target, response/error mapping | Valid tool call reached intended producer | Correlate executor and producer request IDs |
| Producer | Tool definition and real query/service/mapper path | Current code ran in the incident | Resolve deployed SHA at incident time |
| Database | Read-only rows under runtime-equivalent filters | Matching raw row was eligible | Apply active, blocked, tenant, kind, tariff, and visibility scopes |
| Provider | Raw HTTP request/response at the manager boundary | HTTP 200 completed the workflow | Verify parsing, persistence, checkpoints, and later reads |
| Deployment | Exact pipeline and deployment job for exact SHA | Green pipeline means live production | Verify environment job, running SHA, and public behavior |

## Minimum Trace Record

Capture when available:

```text
environment:
surface / actor / access_policy:
conversation_id:
request_id / trace_id:
timestamp range:
user message:
catalog or digest version:
selected tool:
exact arguments:
producer request/log:
tool structured result or error:
trusted context persisted:
assistant response:
consumer SHA:
producer SHA:
pipeline / deployment job:
```

## Discriminating Controls

- Same literal query with and without `service_kind`.
- Exact external ID or IATA versus full name, generic term, partial term, and typo.
- Active eligible record versus inactive, blocked, wrong-kind, and duplicate records.
- Direct producer call versus consumer-mediated call with the same arguments.
- Fresh digest/catalog versus stale consumer state.
- Same exact SHA locally, on staging, and on production.
- Legacy result without selection numbers versus numbered result; valid and invalid numeric selection.

Run only controls that separate plausible hypotheses. Avoid broad production queries or data mutations.
