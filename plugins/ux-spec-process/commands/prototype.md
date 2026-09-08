---
description: Phase 6 — build code prototype in proto-playground
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/03-prd.md` exists
- `specs/<slug>/04-solution-directions.md` exists
- `specs/<slug>/05-flow-audit.md` exists
- `specs/<slug>/spec-state.json` exists

**Resolve the prototype sandbox (`meta.prototype_root`) before invoking the agent.** The only legal
build target is a clone of https://github.com/mattermost/mattermost-proto-playground. Never write
into `mattermost/`, `mattermost-blocks-prototype/`, or any other product repo.

**Identity check (shared — every resolve/reuse path MUST pass this before use OR persistence).** A
directory is a valid build target ONLY if it is identifiably mattermost-proto-playground, not merely
any repo with `package.json` + `src/` (that would match a product repo and risk writing into it).
Confirm **both**: (a) `package.json` exists and its `name` field is `mattermost-proto-playground`;
and (b) `src/` exists. If `name` doesn't match, also accept a git identity match — `git -C <root>
remote get-url origin` resolves to `mattermost/mattermost-proto-playground`. If neither identity
signal holds, **abort** — never build against or persist an unverified path.

1. If `meta.prototype_root` is already set and that directory **passes the identity check**, use it.
   (A stored path that no longer passes — moved, swapped, or a bare product repo — is re-resolved, never trusted.)
2. Else look for an existing clone at `prototype-playground/mattermost-proto-playground/` or
   `mattermost-proto-playground/`. If found **and it passes the identity check**, confirm the path with
   the user (or accept it) and persist it to `meta.prototype_root` via
   `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state apply-delta`.
3. Else ask the user for the path to their clone. If they don't have one, pause and tell them to
   set it up from that repo:
   ```
   git clone https://github.com/mattermost/mattermost-proto-playground.git prototype-playground/mattermost-proto-playground
   ```
   Then run the identity check, persist it to `meta.prototype_root` only if it passes, and only then continue.
4. Abort if the resolved directory fails the identity check above.

If the artifact preconditions fail, abort and tell the user which prior phase to run.

## Invoke

Invoke the `spec-orchestrator` agent to execute Phase 6 (Prototype). Pass it:
- The slug
- Paths to the PRD, Solution Directions, and Flow Audit (`05-flow-audit.md`)
- Path to the state object
- **Build target: `meta.prototype_root` only** (resolved above). Pass that path through to the
  agent and every Phase 6 skill. Do not offer a playground-choice intake.
- Route convention: prototype must be accessible at `/prototypes/<slug>` per the sandbox routing.

The orchestrator will:
- **Verify the Phase 6 intake clarification round** runs first (per the `clarification-protocol` skill). Covers page pattern, theme coverage, state coverage, demo data approach, recommendation in index. Does **not** cover which playground to use.
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
