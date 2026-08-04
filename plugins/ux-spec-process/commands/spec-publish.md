---
description: Phase 8 — publish spec to Confluence as DRAFT (requires explicit confirmation)
argument-hint: "<project> [space=<key>] [parent=\"<page title>\"]"
---

Parse `$ARGUMENTS`. Expected formats:
- `<slug>` — resolve the Confluence target interactively (see Target resolution)
- `<slug> space=<space> parent="<parent page title>"` — specify the target explicitly

Resolve the slug under `specs/` (exact match → fuzzy → ask).

## Preconditions

- `specs/<slug>/07-spec-draft.md` exists (run `/spec` first if not — abort).
- `specs/<slug>/spec-state.json` exists.

## Target resolution

If the user supplied `space=` and `parent=` arguments, use those.

Otherwise, **ask the user** for the target — do not guess or default to a hardcoded value:
- Confluence space key or name
- Parent page title

If `meta.confluence_last_parent` (space + parent title) is already set on the spec state from a prior publish, offer it as the default and confirm before reusing it.

## Hard-stop confirmation protocol

Before any Confluence write:

1. **State exactly what will be written and where.** Print a confirmation block:
   ```
   I am about to publish to Confluence as a DRAFT (not published):
     Space:        <space>
     Parent page:  <parent title>
     Page title:   [AI DRAFT] <feature_name> — UX Spec
     Source file:  specs/<slug>/07-spec-draft.md
     Word count:   <count>
   This will create a NEW draft page. It will NOT publish.
   Confirm with "yes" or "go ahead" to proceed.
   ```

2. **Wait for explicit affirmative.** Accept only "yes", "confirm", "go ahead", "publish draft". Do not accept "ok", "sure", or any implied consent. If the user declines, abort and report nothing was written.

3. **On confirmation:** Use the Atlassian MCP `createConfluencePage` tool to create the page as a **draft** (not published). Page title must begin with `[AI DRAFT]`. Body is the markdown content of `07-spec-draft.md` converted to Confluence storage format.

4. **Second confirmation for publishing.** Never publish (move from draft to live) without a separate, explicit instruction from the user. This command only creates drafts.

5. **On success:** commit via the `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI only — never hand-edit `spec-state.json` (Edit/Write are hook-denied; bash redirection / `sed` is prohibited):
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state apply-delta <slug>` to set `phase.current = 8`, `meta.confluence_draft_url = <page URL>` (the newly created draft — never reused as a parent target), and `meta.confluence_last_parent = {"space":"<space>","parent_title":"<parent title>"}` (the resolved target actually used, reusable as the next run's default). **Do not pass any timestamp** — the CLI stamps `meta.last_updated`.
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state log-event <slug> --event confluence_draft_created --phase 8 --actor human --details '{"page_url":"<url>"}'` (closed-vocabulary event; the CLI stamps the timestamp).

## Report

1. Confluence draft URL
2. State object updated
3. Reminder: page is a draft. To publish, the user must explicitly instruct it.

## Rules

- Never publish directly — drafts only.
- Never reference customer names in the page title or body.
- Page title must always be prefixed `[AI DRAFT]` until a human removes it post-review.
