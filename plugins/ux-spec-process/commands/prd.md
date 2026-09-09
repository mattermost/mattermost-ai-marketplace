---
description: Phase 3 — PRD + threat model + pre-flight review
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/01-problem-statement.md` exists
- `specs/<slug>/02-research-brief.md` exists
- `specs/<slug>/spec-state.json` exists

If any precondition fails, abort and tell the user which prior phase to run.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 3 (PRD). Pass it:
- The slug
- Paths to the Problem Statement and Research Brief
- Path to the state object

The orchestrator will:
- **Verify the Phase 3 intake clarification round** runs first (per the `clarification-protocol` skill). Covers scope cut (MVF/GA), threat model depth, mobile coverage, analytics expectations, success metrics emphasis, SKU/licensing, approval cadence, dependency surfacing, [VERIFY WITH PM] tolerance.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (`add-clarification` per answer into `context.clarifications[]` + `apply-delta` `gates.phase_3.intake_clarifications`) — the CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- Delegate to `prd-agent`, which:
  - Generates the PRD body
  - Runs a **threat model** on the proposed surface (uses `threat-modeler` skill) — enumerate spillage paths, trust boundaries, misconfiguration vectors, UI-layer attack surface
  - Runs a **pre-flight review** — internal consistency check, missing-requirement scan
- Validate output against the Phase 3 gate artifact checklist.
- Save to `specs/<slug>/03-prd.md`.
- Commit the transition via the CLI: `apply-delta` `phase.current = 3` and `log-event` the audit entry (the CLI stamps `meta.last_updated` and all timestamps).

If the prd-agent triggers an in-phase ambiguity pause (score ≥ 2), the orchestrator will relay the round and halt artifact production until the user answers.

## Output requirements

- All **[VERIFY WITH PM]** flags at the top of the file.
- Threat model section is prominent (not buried) — DoD reviewers look for it.
- Label content **[AI DRAFT]**.

## Report

1. Path to the PRD
2. [VERIFY WITH PM] flag count + one-line summaries
3. Threat model highlights (3 most critical surfaces, one line each)
4. Pre-flight review verdict (clean / issues found)
5. Suggested next step: `/ideate <slug>`
