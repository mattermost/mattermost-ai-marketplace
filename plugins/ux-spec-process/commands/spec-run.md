---
description: Run the full spec pipeline (Phases 1–7) with a checkpoint after each phase
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/` exists. If not, abort with: `Run /spec-init <name> first to bootstrap the project.`
- `specs/<slug>/00-brain-dump.md` exists and is non-empty. If empty, abort and tell the user to populate it before running.
- `specs/<slug>/spec-state.json` exists. **The state object is non-optional** — the pipeline does not run freeform. If it is missing but the slug + non-empty brain dump resolve, **auto-bootstrap** it (`cp ${CLAUDE_PLUGIN_ROOT}/templates/spec-state-object.json` into place, then via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI `apply-delta` `phase.run_status="active"` — no timestamps, the CLI stamps them — and `log-event --event spec_created`) and surface: *"No state object found — bootstrapped a fresh `spec-state.json` so this run is tracked."* If the slug can't be resolved, abort with the `/spec-init` message above.
- If `phase.run_status` is `paused` or `abandoned`, `apply-delta` it back to `active` and `log-event --event run_resumed` before looping.

## Pre-run summary

Read `spec-state.json`. Determine the starting phase = `phase.current + 1` (or 1 if `phase.current` is 0).

Print a pre-run summary and ask for confirmation:
```
About to run the spec pipeline for <slug>:
  Starting phase:   <N>  (<phase name>)
  Through:          Phase 7 — Spec Draft
  Checkpoint:       after every phase
  Will NOT run:     /spec-publish (Confluence writes require explicit human action)

Estimated time: 20–40 minutes depending on agent depth.
Proceed? [y/n]
```

Accept only "y", "yes", "proceed", "go". Anything else → abort cleanly.

## Phase loop

For each phase from `start` through 7, in order:

| Phase | Command to invoke |
|-------|-------------------|
| 1 | `discovery-agent` via `spec-orchestrator` (mirror `/discover` body) |
| 2 | `research-agent` via `spec-orchestrator` (mirror `/research` body) |
| 3 | `prd-agent` via `spec-orchestrator` (mirror `/prd` body) |
| 4 | `ideation-agent` via `spec-orchestrator` (mirror `/ideate` body) |
| 5 | `flow-agent` via `spec-orchestrator` (mirror `/flow` body) |
| 6 | `prototype-agent` via `spec-orchestrator` (mirror `/prototype` body) |
| 7 | `spec-writer-agent` via `spec-orchestrator` (mirror `/spec` body) |

For each phase:

1. **Skip if already complete.** If the artifact for this phase exists AND `spec-state.json` records the phase as complete, skip with a one-line notification and move on. (User can run `/spec-clean` or delete the artifact first if they want a re-run.)

1a. **Scope checkpoints (hard stops — surface and pause, do not auto-pass):**
   - **Entering Phase 3** → the orchestrator runs the **scope re-confirm** (SCOPE-LOCK §B): re-present the locked tier/scope/surface/comparator counts and wait for `y` or a described change. A change is logged as a deliberate `scope_change` (never a silent rerun); a tier flip triggers an explicit, logged re-run offer. Block Phase 3 until `scope_lock.reconfirmed_at_phase_3 == true`.
   - **Entering Phase 5 or Phase 6** → the orchestrator runs the **decide-or-fork checkpoint** (SCOPE-LOCK §C): every open `[VERIFY WITH PM]` blocker (`status=="open"`, `blocker==true`) must be **decided** (`spec decide-verify`) or **explicitly branched into a named sibling spec** (`spec branch-verify`) — a blocker cannot be deferred past this point, and a fork is never silent. Block the phase until the checkpoint is cleared and a `verify_decision_checkpoint` record is written. Both `continue` and `skip next` are disabled while blocked — only resolving the blocker or `quit` may proceed. This is the structural fix for decision-deferral forks.
   These checkpoints run **before** the phase's intake round. Surface them verbatim and use the same pause flow as intake.

2. **Run the phase.** Invoke the orchestrator with the phase directive. Commands complete without blocking on gate sign-off (async approval); never start the next phase without approval. The orchestrator appends a `phase_started` event (real ISO timestamp) on entry and `phase_completed` on a clean validation.

3. **Render HTML artifacts (advisory-failable).** Invoke the `html-spec-renderer` skill to:
   - Generate / update the per-phase HTML artifact per the pattern matrix in the `html-spec-renderer` skill (e.g., Phase 4 → `04-options.html` side-by-side comparison; Phase 5 → `phase-5-flow/<flow>.html` interactive flowcharts; Phase 6 → `prototype-tour.html`).
   - Regenerate the master `spec.html` to incorporate the new phase block.
   - Update `verify-board.html` if the phase produced new `[VERIFY WITH PM]` items.
   - On Phase 7 completion, also produce / refresh `traceability-heatmap.html`.

   This step is **advisory-failable**: if the skill errors or is unavailable, log the failure as a phase warning and continue to the checkpoint — do not block the phase loop. Surface "HTML render: ok | skipped (reason) | failed (reason)" in the checkpoint summary's Warnings line.

   Skip this step entirely for `redo` and `skip next` choices that have not yet produced a new artifact.

4. **Checkpoint after the phase.** Print:
   ```
   ─────────────────────────────────────────
   Phase <N> complete: <phase name>
     Artifact:        specs/<slug>/<file>.md
     BLUF:            <one-sentence summary of output>
     [VERIFY WITH PM]: <count>
        - <one-line summary of each flag>
     [EXTERNAL — UNVERIFIED]: <count>   (Phase 2 only)
     Warnings:        <any agent-flagged issues, or "none">
   ─────────────────────────────────────────

   What's next?
     [c] continue        → run Phase <N+1>
     [p] pause           → exit; resume later with /spec-run <slug>
     [r] redo            → delete this phase's output, re-run
     [e] edit & continue → pause; type "ready" when done editing
     [s] skip next       → skip Phase <N+1>, jump to <N+2>
     [q] quit            → exit without further changes
   ```

5. **Wait for explicit affirmative.** Accept single-letter shortcuts (`c`, `p`, `r`, `e`, `s`, `q`) or the full word. Do **not** accept "ok", "sure", or implied consent. On any unrecognized input, re-prompt.

6. **Handle the choice** (every state mutation gets a **typed audit event** from the closed vocabulary in `spec-state-object.json::$conventions.audit_event_vocabulary`, with a **real ISO-8601 timestamp** — never `{action: ...}` ad-hoc shapes or `T00:00:0N` placeholders):
   - **continue** → proceed to Phase N+1
   - **pause** → set `phase.run_status = "paused"`, append `run_abandoned` is NOT used here (the run isn't abandoned) — just exit cleanly and print the final report; user can re-run `/spec-run <slug>` to resume (which appends `run_resumed`)
   - **redo** → delete the phase's artifact file, decrement `phase.current`, append a `phase_rerun` event `{ timestamp, event:"phase_rerun", phase:N, actor:"human", details:{ reason:"user redo" } }`, re-run the same phase
   - **edit & continue** → exit the prompt; user edits the file; type "ready" or "continue" to resume from the next phase
   - **skip next** → advance the phase counter past N+1 and append `{ timestamp:<real ISO>, event:"phase_skipped", phase:N+1, actor:"human", details:{ reason:"user skip" } }`, move to N+2
   - **quit** → set `phase.run_status = "abandoned"`, fill `phase.abandoned_reason = "user quit at phase N"`, append a `run_abandoned` event, then exit; state object reflects what completed (no silent gap)

## Clarification handling (intake + ambiguity)

Every phase now runs an **intake clarification round** as its Step 0 (per the `clarification-protocol` skill). The autopilot loop honors this by:

1. **Pause for intake.** When the phase agent surfaces its intake round, display it verbatim and wait for the user's response. Accept either explicit per-question answers (`1: B, 2: A, ...`) or `accept recommendations` to take all defaults.
2. **Pause for in-phase ambiguity.** If the agent's ambiguity score reaches ≥ 2 during the phase (Trigger B in the protocol), the same pause flow applies.
3. **Record answers.** Update `context.clarifications[]` and `gates.phase_N.intake_clarifications` before resuming the phase.
4. **Escalate on round exhaustion.** If a phase exhausts 3 clarification rounds without resolving, the orchestrator reports `escalation_needed: true`. Stop the loop, surface the escalation message, and offer the checkpoint menu — typical resolution is to re-run an earlier phase rather than continue.

If during any phase the orchestrator or its delegated agent flags:
- Missing prerequisite that should have come from a prior phase
- A decision that requires a human choice (e.g., which solution direction to prototype)
- An unresolved `[VERIFY WITH PM]` that blocks further work
- An external content source that cannot be cross-verified

Then **stop the loop**, surface the issue verbatim, and offer the same checkpoint menu — but with **both `continue` and `skip next` disabled** until the issue is resolved (skipping ahead would bypass the same guard). Only `pause`, `redo`, `edit & continue`, or `quit` remain available; resolving the blocker (`decide`/`branch`) re-enables `continue`.

## Hard stops — never bypass

- **Never run `/spec-publish`.** Confluence writes require a separate, deliberate human action.
- **Never run `/spec-clean`.** Destructive commands are never auto-invoked.
- **Never modify `spec-state.json` directly.** The orchestrator owns it and writes it ONLY through the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (Edit/Write are hook-denied; bash redirection / `sed` is prohibited). Only the choices above (`redo`, `skip next`, normal phase completion) may mutate it — always via a **typed `log-event` (the CLI stamps every timestamp)**.
- **Never advance past an open `[VERIFY WITH PM]` blocker** at the Phase 5/6 decide-or-fork checkpoint. Decide it or branch it into a named sibling spec — never a silent fork (the `membership-policies` `-public`/`-flexible` twin failure mode).
- **Never run a phase without a state object.** Auto-bootstrap with a notice or refuse; no freeform runs.
- **Never reference customer names** in any artifact.
- **Never write to Confluence, Jira, GitHub, or any external system.**

## Final report

When the loop ends (Phase 7 complete, user paused, or user quit), print:

```
═══════════════════════════════════════════
  Spec Run Summary — <slug>
═══════════════════════════════════════════
  Phases completed this run:  <list>
  Phases skipped:              <list, with reasons>
  Total [VERIFY WITH PM]:      <count> across all artifacts
     - open blockers:          <count of status==open && blocker==true>
  Scope changes this run:      <count from scope_lock.changes[]>
  Total elapsed time:          <duration — computed from real audit-log timestamps; "n/a" only if events are missing, never from synthetic placeholders>
  Run status:                  <phase.run_status>
  Current phase state:         <N> (<status>)

  Suggested next step:
    <one of: review specs/<slug>/07-spec-draft.md, then /spec-publish <slug>>
                <or: resume with /spec-run <slug>>
                <or: investigate ambiguity in Phase X>
═══════════════════════════════════════════
```

## Report at top, never bury

If at any point during the run you produce intermediate output (agent thinking, file paths, etc.), the checkpoint summary still appears at the bottom of each phase block in the exact format above — never buried in a paragraph, never abbreviated.
