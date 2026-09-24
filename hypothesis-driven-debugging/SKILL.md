---
name: hypothesis-driven-debugging
description: Diagnose bugs, failing tests, and unexpected behavior when the cause is uncertain. Use before speculative fixes or when an attempted fix fails; preserve investigation-only scope.
---

# Hypothesis-Driven Debugging

Follow this route: reproduce the symptom -> compare plausible causes -> run a
discriminating experiment -> fix the supported cause -> repeat the original check.
Keep it brief when the evidence already identifies the cause.

## Establish the Symptom

- Record expected versus observed behavior, relevant input, environment, revision,
  and the exact error or result. Separate user reports from direct observations.
- Obtain the smallest safe reproduction: a focused test, command, or recorded
  request with controlled dependencies. Confirm it fails for the reported reason.
- When reproduction is unavailable or unsafe, use existing traces and read-only
  evidence. State the limitation and the next observation needed; do not claim a
  reproduced or fixed bug without a corresponding check.

## Compare Hypotheses

- Read the relevant code, recent changes, and a working comparison where available.
- List plausible competing causes and an observation that would refute each.
  Do not invent alternatives when direct evidence settles a simple defect.
- Choose the smallest safe experiment that distinguishes the leading causes.
  Record the expected result before running it, then the actual result and what
  it establishes. Change one relevant condition at a time.
- Inspect inputs and outputs at the nearest observable failing boundary before
  expanding the search. A successful request or retry does not establish why
  an earlier attempt failed.
- Reject hypotheses contradicted by evidence. If a check adds no information,
  change the experiment instead of repeating it or stacking speculative fixes.

## Fix and Verify

- If implementation is authorized, correct the supported cause in the owning
  layer and preserve unrelated behavior. Add a regression check that detects the
  original defect; for Rails/Ruby behavior changes use
  [test-driven-development](../test-driven-development/SKILL.md).
- Repeat the original reproduction after the final edit, then run relevant
  neighboring checks and required project gates. If the symptom persists, return
  to the hypotheses with the new evidence.
- For investigation-only work, report the supported cause and proposed fix.
  Do not turn diagnosis into an implementation or delivery task.
- Distinguish a mitigation from a root-cause fix. A useful mitigation does not
  prove the explanation and must remain within authorized scope.

## Boundaries and Report

- Experiments inherit the task's permissions. Replaying a payment, refund,
  callback, or production job can change external state; use a local fixture,
  sandbox, or read-only evidence unless that exact live operation is authorized.
- Redact credentials and personal data in diagnostic output. Do not dump entire
  environments or unfiltered production payloads to gather evidence.
- Before a costly or externally effective experiment, prepare its target, expected
  evidence, and effects; request any permission the conversation does not supply.
- If progress depends on unavailable access or an unresolved decision, report the
  exact blocker and next check. Do not invent a cause to close the task.
- Report symptom, supported cause or remaining hypotheses, experiment results,
  changes, and final verification. Preserve rejected approaches in the task's
  existing handoff only when continued work needs them.

For Konsierge MCP or marketplace incidents, use
[konsierge-mcp-incident](../konsierge-mcp-incident/SKILL.md) for its boundary map and
provider evidence rules; apply this route within that investigation.
