---
description: Phase 1 — Discovery (Problem Statement)
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/`:
1. Try exact match: `specs/$ARGUMENTS/`.
2. Fuzzy match against existing slugs if no exact match.
3. If ambiguous, list candidates and ask.
4. If not found, suggest `/spec-init` and stop.

## Preconditions

- `specs/<slug>/00-brain-dump.md` exists and is non-empty.
- `specs/<slug>/spec-state.json` exists, **or** the slug resolves to a real folder with a non-empty brain dump so it can be bootstrapped. **The state object is non-optional** (it is the run's memory + audit trail; running without one is the failure mode that left only 3/22 past specs tracked) — but it need not pre-exist, since a missing one is auto-bootstrapped below. If it is missing:
  - When the slug resolves to a real folder with a non-empty brain dump, **auto-bootstrap** the state object (`cp ${CLAUDE_PLUGIN_ROOT}/templates/spec-state-object.json` into place, then via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI `apply-delta` `meta.*` / `phase.current=0` / `phase.run_status="active"` — no timestamps, the CLI stamps them — and `log-event --event spec_created`) and surface a clear one-line notice: *"No state object found — bootstrapped a fresh `spec-state.json` so this run is tracked."* Then continue. Never proceed silently.
  - When the slug can't be resolved, **REFUSE** and tell the user to run `/spec-init <name>` first.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 1 (Discovery). Pass it:
- The slug
- Path to the brain dump
- Path to the state object
- Operating mode: **async approval** (present checklist, set gate `in_review`, do not block; advancement requires explicit approval)

The orchestrator will:
- Confirm the state object exists (auto-bootstrap with notice, or refuse) per "STATE OBJECT IS NON-OPTIONAL" — then `log-event --event phase_started` via the CLI (which stamps the timestamp).
- Delegate to `discovery-agent`
- **Verify the Phase 1 intake clarification round** runs first (per the `clarification-protocol` skill). This is the project-intake round — the richest in the system, covering complexity tier, interaction mode, mission tier, user role focus, compliance frameworks, mobile coverage, and feature-specific ambiguities. **It must also resolve the scope-lock inputs** — tier, in/out scope, surface count, comparator count (per `clarification-protocol` Trigger A scope-bearing intake). Up to 10 questions (scaled by tier), one round. User answers with `1: B, 2: A, ...` or `accept recommendations`.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI — `add-clarification` per answer (each with `chosen_via` + `user_message_ref`) into `context.clarifications[]`, `apply-delta` `gates.phase_1.intake_clarifications`, and `log-event` the matching `clarification_resolved` / `bulk_accept_recommended` entries. The CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- **Lock scope** before accepting the Problem Statement: `apply-delta` `scope_lock` (tier, scope summary, in/out scope, surface_count, comparator_count), set `locked=true` (omit `locked_at` — the CLI rejects `*_at` in deltas), then `log-event --event scope_locked`. This satisfies gate item 1.12 — the gate is not approvable until scope is locked.
- Validate output against the Phase 1 gate artifact checklist in `${CLAUDE_PLUGIN_ROOT}/templates/gate-checklists.md` (incl. 1.0 intake recorded and 1.12 scope locked).
- Save the Problem Statement to `specs/<slug>/01-problem-statement.md`. Any `[VERIFY WITH PM]` becomes a **typed** `context.open_questions[]` item via `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state add-question <slug> --id V-XXX --text "…" --owner <o> --blocker <true|false> --phase-ref P1` (the CLI self-stamps `raised_at` and defaults `status=open`), plus a `log-event --event verify_item_raised`.
- Commit the phase transition via the CLI: `apply-delta` `phase.current = 1` / `phase.status = "complete"` / `phase.history` append, then `log-event --event phase_completed`. **The CLI stamps `meta.last_updated` and every timestamp — you never write one (which is exactly why synthetic `T00:00:0N` placeholders are impossible).**
- Set the Phase 1 gate to `in_review` (since signoff is not blocking)

If the discovery-agent triggers an in-phase ambiguity pause (score ≥ 2), the orchestrator will relay the round and halt artifact production until the user answers.

## Output requirements

- All **[VERIFY WITH PM]** flags must appear at the top of `01-problem-statement.md`, never buried.
- Label the file content **[AI DRAFT]** until human review.
- Tag any externally sourced content **[EXTERNAL — UNVERIFIED]**.
- Never reference customer names.

## Report

Print to the user:
1. Path to the Problem Statement
2. Count of [VERIFY WITH PM] flags (and a one-line summary of each)
3. Suggested next step: `/research <slug>`
