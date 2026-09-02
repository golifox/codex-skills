---
name: orchestrating-agent-work
description: Use when coordinating multi-step implementation work with parallel streams, role-based subagents, review checkpoints, or durable continuation across sessions.
---

# Orchestrating Agent Work

The primary agent owns goals, dependencies, decisions, integration, and delivery evidence. Delegate bounded detail while keeping authority and shared-state mutations centralized.

## Routing

- Use `superpowers:dispatching-parallel-agents` to partition genuinely independent domains.
- Use `superpowers:subagent-driven-development` for plan execution with isolated worktrees, ledgers, reviews, fix rounds, and final verification.
- Route discovery to `codebase_explorer`, cross-cutting design to `architect`, implementation to `implementer` or a domain specialist, independent review to `code_reviewer`, and acceptance checks to `verifier`. Use security or migration specialists when those boundaries are material.
- Give coding agents an explicit worktree, branch, file ownership, acceptance criteria, verification commands, report path, and warning that concurrent user/agent changes must be preserved.
- Give every delegated task a minimal skill allowlist in its brief. Use a context budget, not a hard ban:
  - discovery/review: one task-specific skill at most, plus project instructions;
  - routine implementation: the domain skill and one workflow skill (for example, `rails` + `test-driven-development`);
  - release/security/migration work: add only its risk-specific skill (`prerelease`, security, or migration), not unrelated ones.
  The brief carries exact files, invariants, and artifact paths instead of transcript history. An agent may load one extra skill only when it names the concrete missing capability or risk; it reports that escalation in its handoff. This is a prompt-level boundary: the runtime catalog remains visible.
- Before parallel dispatch, compare file and interface ownership, branch, worktree, and dirty state. Serialize streams whose write scopes overlap.
- Do not parallelize tightly coupled or trivial work.

## Control and integration

- Delegate exploration, implementation, diff review, and verification. Keep the primary context focused on goals, dependencies, rulings, SHA and ledger state, integration order, and delivery proof.
- Before the final handoff of a write task, run an AI-slop cleanup review. Remove unnecessary comments, speculative abstractions, redundant defensive code, duplication without a domain concept, awkward generated naming, and violations of the repository's established layers or idioms. Preserve business behavior and public contracts.
- For non-trivial slices, assign cleanup review to an independent reviewer and return confirmed findings to the original implementer. Run the agreed verification again after cleanup.
- Review and verify every slice before integration. Only the primary agent mutates shared branches, merges, pushes, or deploys, and only within explicit user authority.
- Reuse the original implementer for ordinary fix rounds. Independent reviewers report findings; they do not silently repair them.
- Never treat a commit, push, pipeline, deployment, and runtime state as equivalent evidence.

## Durable coordination

- Route each task as `{role, difficulty, skills}` instead of hardcoding model IDs.
- Choose model and reasoning from uncertainty and blast radius, then record the result in the handoff: low-cost discovery/static inspection uses the lightest capable route; routine implementation and focused verification use a standard route; architecture, security, migrations, concurrency, and final reviews use the strongest appropriate route. Escalate only after a concrete signal (conflicting contract evidence, two failed root-cause passes, or a security/irreversible boundary), not merely because a task is unfinished. Respect role-enforced model settings; use explicit model/reasoning only where the runtime permits it.
- For concurrent plans, persist a compact registry containing work ID, plan path, worktree, branch, status, current task, agent/session identity, and last verified SHA. Keep detailed progress in each plan's own ledger.
- Pass structured handoffs (`conventions`, `successes`, `failures`, `gotchas`, `commands`) or artifact paths, not accumulated transcript history.
- Do not advance or redispatch work while its agent is pending or running. Resume from persisted state and verified artifacts.
- Before a final handoff, a write-task worker must run the agreed verification, create one atomic signed commit for the completed slice, and report its exact SHA. Read-only tasks and explicitly blocked or intermediate handoffs do not create commits.
- Workers must not merge or push the shared target branch.
- Classify delegation failures before retrying: invalid routing, missing skill or context, ownership conflict, unavailable tool, capability mismatch, or implementation blocker. Retry with the smallest corrected input.
- Route a child failure to its owning task rather than failing unrelated streams.
- Automatic continuation never authorizes repeating an external side effect. Require persisted idempotency or reconciliation evidence first.

Project and nested `AGENTS.md` instructions remain authoritative for repository-specific workflow and architecture.
