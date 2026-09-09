---
description: Show current phase, gate status, and artifacts for a spec project
argument-hint: "[project name or slug — empty to list all]"
---

Resolve `$ARGUMENTS` to a project slug under `specs/`:
1. If empty: list all subdirectories of `specs/` and ask the user which one.
2. Try exact match: `specs/$ARGUMENTS/`.
3. If no exact match: fuzzy match against existing slugs (normalize hyphens, spaces, case; use substring/keyword match). One match → use it. Multiple → list candidates and ask. Zero → suggest `/spec-init`.

Once resolved, report **concisely**:

1. **Slug** and human-readable feature name (from `meta.feature_name`)
2. **Current phase** and status (from `phase.current`, `phase.status`)
3. **Tier** (from `meta.complexity_tier`)
4. **Artifacts present** — list files matching `[0-9][0-9]-*.md` in the project folder with one-line descriptions
5. **Gates** — for each phase 1–7, show one line: `Phase N (<name>): <status>` (pending / in_review / approved / bypassed)
6. **[VERIFY WITH PM] flag count** — grep the artifact files and report total open items
7. **Last update** from `meta.last_updated`
8. **Suggested next action** — based on current phase and what artifacts exist (e.g., "Run `/research <slug>`")

Read-only command. Do not modify state, write files, or invoke agents.
