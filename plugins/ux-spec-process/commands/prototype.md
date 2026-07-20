---
description: Phase 6 — build code prototype in proto-playground
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/03-prd.md` exists
- `specs/<slug>/04-solution-directions.md` exists
- `specs/<slug>/spec-state.json` exists
- **At least one of the four prototype targets** exists at the workspace root:
  - `prototype-playground/mattermost-proto-playground/`
  - build target: read `meta.prototype_root` from spec-state (currently `prototype-playground/mattermost-proto-playground/`)
  - `mattermost-blocks-prototype/`
  - `mattermost/`

If preconditions fail, abort and tell the user which prior phase to run, or which prototype target is missing.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 6 (Prototype). Pass it:
- The slug
- Paths to the PRD, Solution Directions, and Flow Audit (if it exists)
- Path to the state object
- **Build target: determined by Phase 6 intake clarification.** The prototype-agent's Step 0 intake round will present four options:
  - `prototype-playground/mattermost-proto-playground` — sandboxed proto-playground copy
  - canonical sandbox = `meta.prototype_root` (`prototype-playground/mattermost-proto-playground/`)
  - `mattermost-blocks-prototype` — legacy blocks prototype
  - `mattermost` — production product repo (strict scoping: isolated branch, `[AI DRAFT — PROTOTYPE]` labels)

  The user's answer is recorded in `context.clarifications[]` and `artifacts.prototype.prototype_base_url`. The agent does not scaffold anything until this choice is made.
- Route convention: prototype must be accessible at `/prototypes/<slug>` per the chosen target's routing (for `mattermost`, follow the product's existing routing conventions instead)

The orchestrator will:
- **Verify the Phase 6 intake clarification round** runs first (per the `clarification-protocol` skill). Covers number of options, page pattern, theme coverage, state coverage, demo data approach, recommendation in index, target playground.
- Commit intake answers via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI (`add-clarification` per answer into `context.clarifications[]` + `apply-delta` `gates.phase_6.intake_clarifications`) — the CLI is the only sanctioned writer; never edit `spec-state.json` directly.
- Delegate to `prototype-agent`, which:
  - Generates **one design option prototype per carried-forward direction** (per phase-6 multi-option pattern; count = `gates.phase_4.carried_forward[]` length)
  - Composes from the component library in the sandbox playground (enumerated at runtime) — does **not** generate components from scratch
  - Uses the existing design tokens and theming system
  - Adds routes under `/prototypes/<slug>` following the existing `pages/` and `router/` conventions
  - Generates required UI states for each option (empty, loading, error, populated)
  - Produces an option comparison matrix at `specs/<slug>/06-prototype-options.md`
- Validate the build (TypeScript compile, no broken imports) before reporting back.
- Commit the transition via the CLI: `apply-delta` `phase.current = 6` and `log-event` the audit entry (the CLI stamps `meta.last_updated` and all timestamps).

## Build hygiene

- If a long-running dev server is needed, run it as a background task — do not block the chat.
- Do not run lint auto-fixers that touch files outside the prototype scope.
- If the build fails, report the error and do not update the state object beyond logging the failure.

## Output requirements

- Each option must be clickable and visually distinct.
- Option comparison matrix scores each option against the Phase 4 evaluation criteria.
- Label all generated files with `[AI DRAFT]` comments at the top.

## Report

1. List of routes added (e.g., `/prototypes/<slug>/option-a`, `/option-b`, etc.)
2. Build status (pass / fail)
3. Path to the option comparison matrix
4. Command to start the dev server (do not auto-start unless asked)
5. Suggested next step: `/spec <slug>` once an option is selected
