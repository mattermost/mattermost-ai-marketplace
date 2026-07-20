---
description: Phase 7 — generate UX spec draft (local only, never writes to Confluence)
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/01-problem-statement.md` exists
- `specs/<slug>/02-research-brief.md` exists
- `specs/<slug>/03-prd.md` exists
- `specs/<slug>/04-solution-directions.md` exists
- `specs/<slug>/06-prototype-options.md` exists (the selected option should be noted; if not, ask the user which option was chosen)
- `specs/<slug>/spec-state.json` exists

If preconditions fail, abort and tell the user which prior phase to run.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 7 (Spec Writing). Pass it:
- The slug
- Paths to all prior artifacts (01–06)
- Path to the state object
- Template: `${CLAUDE_PLUGIN_ROOT}/templates/ux-spec-template.md` — use as a **menu, not a checklist**

The orchestrator will:
- **Verify the Phase 7 intake clarification round** runs first (per the `clarification-protocol` skill). Covers spec length target, optional template sections (terminology, accessibility, analytics, compliance appendix, deprecated explorations, future considerations), Confluence parent page, [VERIFY WITH PM] tolerance in draft.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (`add-clarification` per answer into `context.clarifications[]` + `apply-delta` `gates.phase_7.intake_clarifications`) — the CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- Delegate to `spec-writer-agent`, which:
  - Generates the spec draft, selecting template sections relevant to the feature (skip sections that would be empty filler)
  - Runs internal validation passes:
    - `edge-case-hunter` skill — adversarial review for missing states, contradictions, mobile gaps, security holes
    - `traceability-checker` skill — verify every PRD requirement maps to a spec section
    - `ux-copy-reviewer` skill — catch AI-slop language patterns in any UI copy
- Save to `specs/<slug>/07-spec-draft.md`.
- Commit the transition via the CLI: `apply-delta` `phase.current = 7` and `log-event` the audit entry (the CLI stamps `meta.last_updated` and all timestamps).

## Hard rule

**Do NOT write to Confluence under any circumstance.** This command produces a local draft only. Confluence publishing requires the separate `/spec-publish` command and explicit human authorization.

## Output requirements

- Label content **[AI DRAFT]**.
- Edge case hunter findings appended in a "Validation Notes" section.
- Traceability matrix included or linked.

## Report

1. Path to the spec draft
2. Validation pass results (edge case findings count, traceability gaps count, copy issues count)
3. [VERIFY WITH PM] flag count
4. Suggested next step: review the draft, then `/spec-publish <slug>` to push as a Confluence draft
