---
name: brainstorming
description: Clarify ambiguous feature requests and compare consequential design choices before implementation. Use for new subsystems, uncertain requirements, or materially different approaches; clear, authorized changes can proceed directly.
---

# Brainstorming

Turn the requested outcome into a concrete design with scope, constraints, and
observable acceptance criteria. Scale the process to uncertainty and risk.

## Authorization and Decisions

- Reuse authorization and decisions already given in the conversation. A clear
  action request authorizes implementation and proportionate verification within
  its stated scope; do not require a second approval of the same work.
- Resolve routine, reversible implementation choices from project evidence.
- Ask when missing information materially changes the result, a consequential
  choice remains unresolved, or an action exceeds existing authorization.
  Prepare the concrete proposal and recommendation before asking.
- Wait for required answers before dependent work. Continue independent,
  authorized work meanwhile. Silence is not approval.
- Preserve explicit research-only, design-only, and external-action boundaries.
  A design decision does not itself authorize a push, deployment, or live mutation.

## Choose the Smallest Useful Process

| Situation | Process |
| --- | --- |
| Clear, bounded change in an existing flow | Read the relevant code, briefly state the approach, implement and verify under existing authorization. No mandatory spec or approval round. |
| Feasibility question or uncertain technical assumption | State the question and run a bounded, authorized experiment. Report observations and limitations; label experimental code as throwaway. |
| New subsystem, unclear behavior, or consequential interface choice | Gather evidence, clarify unresolved decisions, compare viable approaches, and record the resulting design and acceptance criteria. |

Reassess when new evidence changes scope or risk. Pause only the work affected by
an unresolved decision or missing authority. Complexity alone does not revoke
prior approval or require a new interview.

## Clarify and Compare

1. Read relevant project instructions, code, contracts, and prior decisions.
   Find facts in the project before asking the user to supply them.
2. Identify the missing outcomes, constraints, failure behavior, and acceptance
   criteria. Use [interview-me](../interview-me/SKILL.md) when intent needs deeper
   clarification.
3. Group independent questions into a short round, usually two or three. Include
   a recommended answer and reason for each. Ask dependent questions after their
   prerequisites are answered; one question is appropriate when it blocks the rest.
4. Compare alternatives only where a real choice exists. Show concrete behavior,
   trade-offs, and a recommendation. For substantial interface choices, use
   [codebase-design](../codebase-design/SKILL.md).
5. Resolve material decisions with the user unless the conversation already
   resolves them. Do not reopen settled questions for a workflow checkbox.

## Record and Continue

- A bounded task can keep its approach and acceptance criteria in the conversation.
- For work spanning sessions or components, write a self-contained design in the
  repository's established location: outcome, scope, constraints, relevant
  interfaces, failure behavior, verification, and remaining decisions. Mark
  proposals and confirmed decisions distinctly.
- Check the design for missing requirements, contradictions, and unverifiable
  claims. Reuse existing specifications instead of creating competing copies.
- When a material decision still needs approval, link the concrete design and
  ask only about that decision. When implementation is already authorized and
  decisions are resolved, continue without another review gate.
- Use [incremental-implementation](../incremental-implementation/SKILL.md) for
  Rails/Ruby changes spanning several layers. Use
  [orchestrating-agent-work](../orchestrating-agent-work/SKILL.md) when the work
  needs coordination or durable continuation. Apply the relevant domain skill
  and focused verification for smaller tasks.
- Commit and deliver only within the user's authorized Git scope.

## Visual Companion

Use visuals when they clarify a concrete design choice. If the user opts into the
browser companion, read [visual-companion.md](visual-companion.md) before starting
its server. Keep conceptual questions in text; the companion is optional.

## Verification

- The outcome, scope, and acceptance criteria are concrete.
- Project facts and unresolved decisions are distinguishable.
- Questions respect dependencies and reuse prior answers.
- The next action fits existing authorization; any pause names the actual
  unresolved decision or missing permission.
