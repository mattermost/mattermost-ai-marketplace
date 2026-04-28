# Phase 8: Release

**Goal**: Update the Jira ticket, prep release metadata, plan backports, and draft release notes.

Steps 8.1–8.4 require a Jira ticket and are skipped if none was identified. Step 8.5 (Release Planning) always runs. If `acli` is unavailable, all Jira/Confluence calls fall back to Atlassian MCP, then manual prompts if both are missing ([rules.md §5.3](rules.md#53-cli-tool-fallback)).

## Step 8.1: Transition Ticket Status
Use `acli jira workitem` to update the ticket:
- **Status**: Move to `Submitted` (or the project's equivalent PR-submitted state)
- If transition fails (e.g., invalid workflow state), report and skip — don't block

## Step 8.2: Update Ticket Fields
Set these fields if available and applicable:

| Field | Value |
|-------|-------|
| Fix Version | Current development target (detect from branch name or ask user) |
| PR Link | The PR URL from Phase 7 |
| Labels | Add `has-pr` or equivalent if project uses it |

## Step 8.3: Backfill Ticket Description & QA Test Steps (from Phase 1)

Resolved tickets often have thin or stale descriptions and no QA test steps — this is the moment to fix that, while Phase 1 context is still loaded in `<artifact_dir>/spec.md`. This step has two parts; both run, both are independent.

**Source of truth for backfill** (per [rules.md §1.4](rules.md#14-artifacts-are-source-of-truth)): read from disk, not conversation.
- `<artifact_dir>/spec.md` — acceptance criteria, scope, user value, motivation
- `<artifact_dir>/plan.md` — `## Test Plan` section
- `<artifact_dir>/findings/phase4/` — exploratory testing checklist + edge cases discovered

### Field-First Principle

**Always write to the real Jira field.** A comment is the absolute fallback, only used when the real field cannot be set, and only after explicit user confirmation. This applies to both description and QA test steps — order of preference, top to bottom:

1. **Real field** (`description`, custom fields like `Test Steps` / `QA Steps` / `Acceptance Criteria`) — preferred, always.
2. **Append to existing field content** — when overwriting would destroy useful prior content; preserves the original author's framing and adds clearly-marked auto-generated content below.
3. **Comment** — fallback only. Used when (a) the project lacks a suitable field, (b) the field is read-only / locked / requires permissions you don't have, (c) `acli` returns an unexpected schema error after retry. **Always confirm with the user before falling back to a comment**, showing them which field probe failed.

Probe the ticket's available fields once per Phase 8 run using `acli jira workitem view <ID> --json` (parse all fields and custom fields) or `acli jira workitem fields --project <PROJECT>` if available. Cache the field map in `state.json.phases["8-release"].field_map` so subsequent steps don't re-probe.

### 8.3a: Description Audit & Backfill (description field)

Fetch the current description value from the ticket. Apply the meaningfulness check:

| Signal | Action |
|--------|--------|
| Description is empty, single line, or `< ~3 sentences` | **Backfill** — describe motivation, scope, and user-visible behaviour from `spec.md` |
| Description is just a title repeat or "see PR" / "as discussed in standup" | **Backfill** — same as above |
| Description references an external doc that no longer exists or is private to the original author | **Backfill** — inline the relevant content from `spec.md` |
| Description is a placeholder template (`**Steps to reproduce:**\n**Expected:**\n**Actual:**` with empty fields) | **Backfill** — fill the template fields from `spec.md` repro steps + acceptance criteria |
| Description is meaningful and current | **Skip** — leave it alone, do not "improve" prose for the sake of it |

**How to write**:
- Use `acli jira workitem edit <ID> --description '<new value>'` (or the equivalent JSON-payload form for multi-line bodies). Update the **description field directly** — do NOT post as a comment.
- **Append**, do not overwrite: read the current description, append the auto-generated block below, write the combined result back. This preserves the original author's words; future readers may need the original framing.
- If `acli` rejects the edit (permission denied, locked field, workflow restriction): **prompt the user** — "Cannot edit description on `<ID>` (reason: `<error>`). Fall back to posting as a comment? (y/n)". Only post a comment on explicit `y`. If the user declines, record `skipped-locked` and move on.

Auto-generated block format (appended to existing description):

```text
---
**Description (backfilled from /longshot Phase 1 spec):**

<motivation: 1–2 sentences on why this work was done>

<scope: what changed, in user-visible terms>

<acceptance criteria, as a bulleted list copied from spec.md>

<related artifacts: PR link from state.json, plan.md path if accessible>
```

The `(backfilled from /longshot Phase 1 spec)` line is the only marker — no AI-attribution per [rules.md §1.3](rules.md#13-no-ai-attribution-in-commits-or-prs). If the ticket is a security ticket, apply [rules.md §3.1](rules.md#31-language-rules-applies-to-all-artifacts) language rules to the backfilled text.

**Confirm with the user before writing** if any backfilled content might be sensitive (security context, customer names, internal-only specifics) OR if the auto-generated block exceeds ~30 lines (signal that scope was misdetected and the user should review).

### 8.3b: QA Test Steps (custom field, then field-append, then comment)

Probe the ticket's field map (cached from above) for a structured test-step field. Common Mattermost/Jira names, in order of preference:
- `Test Steps`
- `QA Test Steps`
- `Acceptance Criteria`
- `Steps to Test`
- Any project-defined custom field whose name matches `/test|qa|acceptance/i`

Apply the meaningfulness check against whatever field (or comment thread, as last resort) currently holds the QA steps:

| Signal | Action |
|--------|--------|
| No structured field present AND no prior QA comment | **Write** — generate from sources below |
| Structured field exists but is empty | **Write** — into the field |
| Structured field is meaningful and covers acceptance criteria | **Skip** — record `skipped-existing` |
| Structured field exists but missing edge cases the work introduced | **Append** — only the new edge cases, into the same field |
| No structured field, but a meaningful QA comment already exists | **Append a supplemental comment** — only new edge cases, referencing the original |
| No structured field AND no usable comment | **Confirm fallback** with user, then post as comment |

**Decision flow**:
1. If a structured field exists → **write/append into it** via `acli jira workitem edit <ID> --field "<Field Name>"='<value>'` (or JSON form). Done.
2. If no structured field exists → prompt the user: "Ticket `<ID>` has no `Test Steps` / `QA Test Steps` / `Acceptance Criteria` field. Post QA steps as a comment instead? (y/n)". Only post a comment on explicit `y`.
3. If `acli` rejects the field write → same prompt as 8.3a's fallback path.

Generate QA test steps from:
- Acceptance criteria (from `<artifact_dir>/spec.md`)
- Exploratory testing checklist (from `<artifact_dir>/findings/phase4/`)
- Key user flows and edge cases identified during Phase 2/4

Content format (used in both field-write and comment-fallback paths; the surrounding wrapper changes, the body doesn't):
```text
QA Test Steps (auto-generated from /longshot):

Setup:
1. Check out branch: <branch-name>
2. Deploy locally / use test server

Verification:
1. [ ] <acceptance criterion 1> — expected: <behavior>
2. [ ] <acceptance criterion 2> — expected: <behavior>
...

Edge Cases:
1. [ ] <edge case from gap analysis>
2. [ ] <edge case from exploratory testing>

Regression:
1. [ ] Verify existing <related feature> still works
2. [ ] No console errors on affected pages
```

### Recording in state.json

Both backfills, if performed, are tracked under `state.json.phases["8-release"]` so the Longshot Summary surfaces them and the chosen path is auditable:

```json
"backfill": {
  "description": {
    "result": "appended-to-field" | "skipped-meaningful" | "skipped-no-spec" | "skipped-locked" | "fallback-comment",
    "field_used": "description" | null,
    "comment_id": "<id>" | null,
    "timestamp": "<RFC3339 UTC>"
  },
  "qa_steps": {
    "result": "written-to-field" | "appended-to-field" | "skipped-existing" | "skipped-no-spec" | "fallback-comment",
    "field_used": "Test Steps" | "QA Test Steps" | null,
    "comment_id": "<id>" | null,
    "timestamp": "<RFC3339 UTC>"
  }
}
```

If `<artifact_dir>/spec.md` is missing (e.g., `--skip-to release` from a stale run), set both `result` values to `skipped-no-spec` and warn the user — the source-of-truth requirement in §1.4 forbids reconstructing from conversation.

## Step 8.4: Link PR to Ticket
If not already linked via branch name convention, add the PR as a linked item on the ticket.

## Step 8.5: Release Planning

Always runs. Depth scales based on scope and whether this is a security issue.

**For all tickets** (standard release planning):

1. **Determine fix version**: If not already set in state.json `release.fix_version`, identify the target release:
   - **With ticket** (`state.json.repo` has a Jira ID): check the ticket's Fix Version via `acli jira workitem view`; query Jira project versions (`acli jira workitem search --jql "project = MM AND fixVersion = '<version>'" --fields fixVersion`) for Unreleased/Released status; update `state.json.release.fix_version` and set the field on the ticket.
   - **Without ticket**: skip Jira reads/writes entirely. Detect from branch name (e.g., `release-10.5` → `10.5.0`) or ask the user; write to `state.json.release.fix_version` only.
   - Either path: cross-reference with the [Mattermost Server Releases page](https://docs.mattermost.com/product-overview/mattermost-server-releases.html#latest-releases) to verify currency and release date.

2. **Backport eligibility**: Evaluate whether this fix should be cherry-picked to any active release or ESR branches:
   - Query Jira for active release versions and their statuses — look for versions marked as Unreleased to identify branches still accepting fixes
   - Reference the [Mattermost Server Releases page](https://docs.mattermost.com/product-overview/mattermost-server-releases.html#latest-releases) for support windows and ESR status
   - Is this a bug fix (not a new feature)?
   - Does it affect functionality available in older releases?
   - If yes to both: identify which maintained branches need the backport by cross-referencing Jira's active versions with the releases page's support windows
   - Record in `state.json.release.backport_targets`
   - Ask the user to confirm the backport list before adding it to the Jira ticket

3. **Document in Jira**: If backports are confirmed, add a comment to the ticket listing target branches and their status.

4. **Release notes & changelog** (non-security issues):
   - If the project maintains a `CHANGELOG.md` or release notes file: draft a concise entry — feature name, one-line description, PR link
   - If there are user-facing changes: draft a customer-facing release note in plain language (one short paragraph, no jargon)
   - If there are documentation updates needed (new config options, changed API surface, migration steps): verify docs were updated in Phase 7.1, or open a follow-up ticket if deferred
   - Ask user to confirm or edit the release note draft before closing the ticket

**Additional steps when `is_security_issue: true`**:

4. **CVE field prep**:
   - Extract CVE ID from the Jira ticket (check description, custom fields, and comments via `acli jira workitem view`)
   - If a CVE ID is present: update `state.json.security.cve` and set the CVE field on the Jira ticket
   - If no CVE yet: note that Security team will assign one; leave a comment on the ticket referencing the PR

5. **CVSS / severity confirmation**:
   - Verify the severity field matches what's documented in the ticket (Security team owns this)
   - If missing or unclear: leave a comment on the ticket asking Security team to confirm before release

6. **Backport coordination** (security-specific):
   - Security fixes typically need backports to ALL actively maintained ESR/release branches — not just the latest
   - Identify affected versions from the ticket's "Affected Versions" field or description
   - For each affected version that has an active branch: add to `state.json.release.backport_targets`
   - Coordinate with Security team on timing — backport PRs may need to land simultaneously (coordinated release)
   - Do NOT open backport PRs until Security team gives the go-ahead (embargo timing)

7. **Security team notification**: Remind the user to update the Security team in the appropriate Mattermost channel that the PR is submitted, fix version is set, and backport targets are identified.

Update state.json per [rules.md §1.5](rules.md#15-statejson-update-ritual). Additionally set top-level `status = "complete"` to close the run.

---
