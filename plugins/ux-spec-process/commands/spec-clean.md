---
description: Reset a spec project to brain-dump-only (destructive, prompts confirmation)
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy match → ask).

## Destructive — confirmation required

1. **List what will be deleted.** Show the user every file under `specs/<slug>/` that will be removed. This includes:
   - All numbered artifacts: `01-*.md`, `02-*.md`, `03-*.md`, `04-*.md`, `05-*.md`, `06-*.md`, `07-*.md`
   - Any agent-generated subdirectories (e.g., `prototypes/`, `wireframes/`, `figma/`)
2. **Show what will be kept / reset:**
   - `00-brain-dump.md` — kept untouched.
   - `spec-state.json` — **reset in place by the CLI, not deleted** (see step 5); preserves `meta` fields and returns the run to phase 0.
3. **Wait for explicit confirmation.** Require the user to type "yes" or "confirm" — do not accept "ok", "sure", or implied consent. If they decline, abort and report nothing was deleted.
4. **Preflight the reset before deleting anything.** Confirm `specs/<slug>/spec-state.json` exists and parses as valid JSON — `reset` requires and overwrites it. If it is missing or malformed, abort now and delete nothing, so the directory stays consistent with state.
5. **Reset the state object FIRST — before deleting any artifact.** Doing the mediated state reset before the destructive file deletion is what makes cleanup failure-safe: a later artifact-deletion failure can then never leave the spec with *pre-cleanup* state next to partially-deleted artifacts (the flagged mismatch). `spec-state.json` is never `rm`/`cp`'d directly — reinitialize it via the CLI only (Edit/Write are hook-denied, and the PreToolUse guard hook denies any Bash command that references `specs/*/spec-state.json`, with no exceptions — a regex over shell text cannot safely allowlist one particular command):
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state reset <slug>` — this single call captures the prior `meta` fields (feature_name, created_at, author, author_email, complexity_tier), overwrites the file from the template, restores those fields, and sets `phase.current` = 0 / `phase.status` = "reset", all atomically. It requires the file to already exist (bootstrap is for new slugs only). The CLI stamps `meta.last_updated` itself.
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state log-event <slug> --event spec_created --phase 0 --actor human --details '{"source":"spec-clean"}'` (the CLI stamps the timestamp). There is no "reset"/"clean" event in the closed vocabulary — a reset re-creates the state object, so `spec_created` is the correct typed event; never use an ad-hoc string like `"clean"`.
6. **Then delete the listed artifact files (best-effort).** Remove the numbered artifacts and agent-generated subdirectories from step 1 (never `00-brain-dump.md`, never `spec-state.json` — it was reset in step 5, not deleted). If any deletion fails, do **not** abort silently: report exactly which files could not be removed. Because state is already reset, re-running `/spec-clean <slug>` safely re-attempts the residual deletions — the directory is never left in the pre-cleanup/partial-delete mismatch.
7. **Confirm** the reset and tell the user the next step is `/discover <slug>`.

## Rules

- Never touch the proto-playground at `meta.prototype_root` — that's a sibling clone of mattermost-proto-playground, not part of the spec project.
- Never delete `00-brain-dump.md`.
- Never write to Confluence, Jira, or any external system.
- If `--force` appears in `$ARGUMENTS`, ignore it. This command always prompts.
