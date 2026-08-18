---
description: Reset a spec project to brain-dump-only (destructive, prompts confirmation)
argument-hint: "<project name or slug>"
---

Resolve `$ARGUMENTS` to a project slug under `specs/` (exact match → fuzzy match → ask).

## Destructive — confirmation required

1. **List what will be deleted.** Show the user every file under `specs/<slug>/` that will be removed. This includes:
   - All numbered artifacts: `01-*.md`, `02-*.md`, `03-*.md`, `04-*.md`, `05-*.md`, `06-*.md`, `07-*.md`
   - `spec-state.json`
   - Any agent-generated subdirectories (e.g., `prototypes/`, `wireframes/`, `figma/`)
2. **Show what will be kept:**
   - `00-brain-dump.md`
3. **Wait for explicit confirmation.** Require the user to type "yes" or "confirm" — do not accept "ok", "sure", or implied consent. If they decline, abort and report nothing was deleted.
4. **Once confirmed, delete the listed files.** `spec-state.json` is excluded from the plain-delete list above — reinitialize it via the mediated write path only; never hand-edit or `rm`/`cp` it directly (Edit/Write are hook-denied, and the PreToolUse guard hook denies any Bash command that references `specs/*/spec-state.json`, with no exceptions — a regex over shell text cannot safely allowlist one particular command):
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state reset <slug>` — this single call captures the prior `meta` fields (feature_name, created_at, author, author_email, complexity_tier), overwrites the file from the template, restores those fields, and sets `phase.current` = 0 / `phase.status` = "reset", all atomically. It requires the file to already exist (bootstrap is for new slugs only). The CLI stamps `meta.last_updated` itself.
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state log-event <slug> --event spec_created --phase 0 --actor human --details '{"source":"spec-clean"}'` (the CLI stamps the timestamp). There is no "reset"/"clean" event in the closed vocabulary — a reset re-creates the state object, so `spec_created` is the correct typed event; never use an ad-hoc string like `"clean"`.
5. **Confirm** the reset and tell the user the next step is `/discover <slug>`.

## Rules

- Never touch the proto-playground (`meta.prototype_root`, `prototype-playground/mattermost-proto-playground/`) — that's a sibling tool, not part of the spec project.
- Never delete `00-brain-dump.md`.
- Never write to Confluence, Jira, or any external system.
- If `--force` appears in `$ARGUMENTS`, ignore it. This command always prompts.
