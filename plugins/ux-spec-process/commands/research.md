---
description: Phase 2 — Research Brief (standards + competitive intel)
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/01-problem-statement.md` exists (run `/discover` first if not — abort with that suggestion).
- `specs/<slug>/spec-state.json` exists.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 2 (Research). Pass it:
- The slug
- Path to the Problem Statement
- Path to the state object

The orchestrator will:
- **Verify the Phase 2 intake clarification round** runs first (per the `clarification-protocol` skill). Covers compliance framework priority, competitive scope, standards depth, competitor count, pattern emphasis, ATO-criticality, research gap tolerance.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (`add-clarification` per answer into `context.clarifications[]` + `apply-delta` `gates.phase_2.intake_clarifications`) — the CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- Delegate to `research-agent`, which runs two sub-agents in parallel:
  - **Standards sub-agent:** maps relevant NIST 800-53, NIST 800-207, NIST 800-162, DoD ZT Reference Architecture, Section 508, IL4/5/6 controls. Each control must have a `[SOURCE]` citation and a documented UX implication.
  - **Competitive intel sub-agent:** analyzes at least 3 platforms. Tags all findings **[EXTERNAL — UNVERIFIED]** until cross-referenced from 2+ sources.
- Validate output against the Phase 2 gate artifact checklist.
- Save the Research Brief to `specs/<slug>/02-research-brief.md`.
- Commit the transition via the CLI: `apply-delta` `phase.current = 2` and `log-event` the audit entry (the CLI stamps `meta.last_updated` and all timestamps).

If the research-agent triggers an in-phase ambiguity pause (score ≥ 2), the orchestrator will relay the round and halt artifact production until the user answers.

## Output requirements

- Label content **[AI DRAFT]**.
- All external findings tagged **[EXTERNAL — UNVERIFIED]** until verified.
- Flag any research gaps explicitly under a "Research Gaps" section.

## Report

1. Path to the Research Brief
2. Count of standards mapped
3. Count of competitive platforms analyzed
4. Open research gaps (one-line each)
5. Suggested next step: `/prd <slug>`
