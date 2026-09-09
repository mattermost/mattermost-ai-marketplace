---
description: Phase 4 — solution directions + scored evaluation matrix
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/03-prd.md` exists
- `specs/<slug>/spec-state.json` exists

If preconditions fail, abort and tell the user to run `/prd` first.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 4 (Ideation). Pass it:
- The slug
- Path to the PRD (the primary input)
- Path to the state object

The orchestrator will:
- **Verify the Phase 4 intake clarification round** runs first (per the `clarification-protocol` skill). Covers approach diversity vector, number of approaches, constraint emphasis, evaluation weighting, risk surfacing depth, recommendation commitment, mobile criterion.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (`add-clarification` per answer into `context.clarifications[]` + `apply-delta` `gates.phase_4.intake_clarifications`) — the CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- Delegate to `ideation-agent`, which generates **3–5 conceptually distinct** solution directions.
- Each direction must be scored on the evaluation matrix:
  - Mission effectiveness
  - Security posture
  - Cognitive load
  - Accessibility (Section 508 / WCAG 2.1 AA)
  - Build cost
- Use the `solution-scorer` skill for matrix construction.
- Produce a **BLUF recommendation** with rationale.
- List the top 3 risks for the recommended direction with proposed mitigations.
- Save to `specs/<slug>/04-solution-directions.md`.
- Commit the transition via the CLI: `apply-delta` `phase.current = 4` and `log-event` the audit entry (the CLI stamps `meta.last_updated` and all timestamps).

If the ideation-agent triggers an in-phase ambiguity pause (e.g., two approaches tie on a load-bearing matrix criterion), the orchestrator will relay the round and halt artifact production until the user answers.

## Output requirements

- Directions must be *conceptually distinct* — not variations of the same idea.
- Scoring rationale per cell, not just numbers.
- Label content **[AI DRAFT]**.

## Report

1. Path to the Solution Directions doc
2. Names of the 3–5 directions (one line each)
3. BLUF recommendation
4. Top 3 risks for the recommendation
5. Suggested next step: `/flow <slug>` or `/prototype <slug>`
