---
description: Phase 5 — generate flow definitions per carried-forward direction, then audit + feedback synthesis
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/04-solution-directions.md` exists
- `specs/<slug>/spec-state.json` exists

If preconditions fail, abort and tell the user to run `/ideate` first.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 5 (Flows). Pass it:
- The slug
- Path to the Solution Directions doc
- Path to the state object

The orchestrator will:
- Read `gates.phase_4.carried_forward[]` (the surviving direction IDs from Gate 4 approval) and pass it to `flow-agent`.
- **Verify the Phase 5 intake clarification round** runs first (per the `clarification-protocol` skill). Covers flow fidelity, mobile flows in scope, error-path depth, navigation audit scope, security audit depth, feedback channels, MUST-FIX threshold.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (`add-clarification` per answer into `context.clarifications[]` + `apply-delta` `gates.phase_5.intake_clarifications`) — the CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- Delegate to `flow-agent`, which:
  - For each carried-forward direction with no designer-provided flows, invokes `flow-generator` to draft a screen-level flow-definition set, labeled `[AI DRAFT]`
  - Audits each direction's flows for completeness using the `flow-auditor` skill — findings kept per-direction, never merged
  - Identifies missing paths, security bypass risks, navigation inconsistencies
  - Synthesizes any stakeholder feedback present in the project folder (use `feedback-synthesizer` skill if feedback files exist)
- Save to `specs/<slug>/05-flow-audit.md`.
- Commit the transition via the CLI: `apply-delta` `phase.current = 5` and `log-event` the audit entry (the CLI stamps `meta.last_updated` and all timestamps).

If the flow-agent triggers an in-phase ambiguity pause (PRD story-to-flow gap or contradicting stakeholder feedback), the orchestrator will relay the round and halt artifact production until the user answers.

## Output requirements

- Flow gaps categorized by severity (P1 / P2 / P3, per conventions.md §1)
- Security bypass risks called out explicitly with mitigation suggestions
- Label content **[AI DRAFT]**

## Report

1. Path to the Flow Audit
2. Count of gaps by severity
3. Top 3 security or navigation risks
4. Suggested next step: `/prototype <slug>`
