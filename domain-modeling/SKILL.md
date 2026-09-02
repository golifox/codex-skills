---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a CONTEXT.md, or recording or editing an ADR.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily: only when you have something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up: capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. Do not treat `CONTEXT.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).

## Create or update an ADR

Treat an ADR as a standalone decision record. Do not implement the recorded decision, push a branch, or deploy without a separate request.

1. Read repository instructions and inspect `git status`, the current branch, and existing ADR files.
2. Preserve the repository's established ADR location and format. If none exists, use `docs/adr/` and [ADR-FORMAT.md](./ADR-FORMAT.md).
3. For a new ADR, select the next unused four-digit number and name it `NNNN-short-english-slug.md`.
4. Verify the code, configuration, and documentation on which the decision depends. Separate confirmed current behavior from the proposal.
5. Do not invent facts, requirements, alternatives, or approval. Do not include secrets or sensitive data.

### Owner approval

Approval is unnecessary when the user explicitly selected the decision, approved the presented ADR, or asked only to record an already confirmed decision.

Approval is required when the ADR selects a material option the user has not approved, or when unresolved questions affect architecture, a security boundary, a public contract, data storage, cost, or reversibility.

When approval is required:

1. Create or update the ADR with status `Предложено`.
2. Mark unresolved decisions and alternatives explicitly; do not replace them with assumptions.
3. Do not stage or commit the ADR.
4. Link the file, summarize the decisions needed, and wait for the owner.
5. After the response, reread the file from disk because the owner may have edited it. Treat the current file as authoritative, apply only approved changes, and set the status to `Принято` only after genuine approval.

### Verification and commit

Before committing an accepted ADR:

- Check its structure, Russian prose, factual grounding, and status consistency.
- Run `git diff --check` and inspect the diff for secrets or real credential values.
- Follow repository Git instructions and preserve unrelated changes.
- Stage only the ADR files created or changed for the request.

When approval is unnecessary or already obtained, create one atomic commit in the repository's style. In a Konsierge repository, use [`konsierge-git-flow`](../konsierge-git-flow/SKILL.md) for branch and delivery rules and [`konsierge-commit-conventions`](../konsierge-commit-conventions/SKILL.md) for the English commit message. Do not push without a separate request.
