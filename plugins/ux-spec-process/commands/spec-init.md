---
description: Bootstrap a new spec project (folder, state object, brain dump)
argument-hint: "<project name, or paste a full brain dump>"
---

Bootstrap a new spec project under `specs/`.

User input: `$ARGUMENTS`

## Decide what the input is

Count the words in `$ARGUMENTS`:
- **Empty:** ask the user for either a project name or a paste of the brain dump.
- **≤ 20 words:** treat as the project name. Derive a kebab-case slug (e.g., "Team Membership Policies" → `team-membership-policies`). Brain dump body will be empty (template only).
- **> 20 words:** treat the input itself as the brain dump body. Propose a kebab-case slug from the dump's first noun phrase or restated topic. Ask the user to confirm the slug before proceeding.

## Steps

0. **Scan for customer/organization names — before anything else.** Scan the raw resolved input (the
   project name if ≤ 20 words, or the full body if > 20 words) for apparent customer/organization names
   (proper nouns that aren't generic role/system/compliance terms). If any are found, list them and pause:
   ask the user to confirm each is not a customer identifier, or to redact it (e.g., replace with
   `[CUSTOMER A]`). Do not proceed until confirmed. **Use only the confirmed/redacted value for every
   subsequent step** — slug derivation, `meta.feature_name`, the state delta, and the brain-dump header —
   whether the request was project-name-only or a full body paste.
1. **Resolve slug.** Derive from the confirmed value (per "Decide what the input is" above). Confirm with
   the user before creating any files.
2. **Check collision.** If `specs/<slug>/` already exists, stop and ask whether to overwrite, append, or pick a new slug.
3. **Create folder:** `specs/<slug>/`.
4. **Initialize state object** at `specs/<slug>/spec-state.json`. First `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state bootstrap <slug>` — this is the ONE sanctioned file-creation step; never a raw Bash `cp`, which the PreToolUse guard hook denies unconditionally (no path-based allowlist can be made safe against command substitution). Then make **every** subsequent write through the same CLI; never hand-edit the file (Edit/Write are hook-denied, and bash redirection / `sed` is prohibited):
   - `apply-delta` to set: `meta.feature_name` (human-readable from input); `meta.author` and `meta.author_email` (derive from `git config user.name` / `user.email`, or ask the user if unset); `meta.complexity_tier` = "Tier 2 — Standard Spec" (default; ask if uncertain); `phase.current` = 0; `phase.status` = "initialized"; `phase.run_status` = "active". **Do NOT include any timestamp** (`created_at` / `last_updated`) — the CLI stamps `meta.last_updated` itself and REJECTS any delta carrying a `*_at` / `timestamp` field.
   - Leave `scope_lock.locked = false` — scope is locked later, at Phase 1 intake (the discovery-agent + orchestrator do this; not here).
   - `${CLAUDE_PLUGIN_ROOT}/scripts/spec-state log-event <slug> --event spec_created --phase 0 --actor human --details '{"source":"spec-init","complexity_tier":"<tier>"}'` — the CLI stamps the real ISO-8601 timestamp (synthetic `T00:00:0N` placeholders are impossible because you never write the timestamp). Do not use ad-hoc event strings like `"init"`.
5. **Create brain dump** at `specs/<slug>/00-brain-dump.md`:
   - If user provided body: write the confirmed/redacted body from Step 0 verbatim, prepended with a
     `# Brain Dump — <feature_name>` header.
   - If template only: scaffold with section headers — Context, Users affected, Compliance touchpoints, What we want to do, Open questions — for the user to fill in.
6. **Report** the slug, folder path, state path, and brain dump path. Tell the user the next step is `/discover <slug>` (or to populate the brain dump first if it's a template).

## Rules

- Do **not** invoke the spec-orchestrator yet — bootstrap is local file work only.
- Do **not** write to Confluence, Jira, or any external system.
- All output is local files. Label any generated content **[AI DRAFT]**.
- Never reference customer names in the brain dump or state object. This is enforced at write time by the
  scan-and-confirm step above — it is not a passive rule the writer is assumed to already follow.
- Intake clarification rounds are run by the phase agents themselves (starting in `/discover`), not by `/spec-init`. This command only bootstraps the folder and state object — the discovery-agent will run the project-intake clarification round as its Step 0 when `/discover` is invoked.
