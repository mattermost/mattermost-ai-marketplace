---
name: security-release-targets
description: Given a Mattermost priority/severity level (Critical/High/Medium/Low), resolve the target release-X.Y branches to cherry-pick onto by parsing the Mattermost release policy (ESR/active/upcoming) and keeping only branches that exist on mattermost/mattermost. Use when you need the list of release branches a fix must be backported to for a given severity.
allowed-tools: Read, Bash(git ls-remote:*), WebFetch
---

# Resolve target release branches for a severity

You take a single priority/severity level and return the set of `release-X.Y`
branches that a fix at that level must be cherry-picked onto, per the Mattermost
release policy. You do NOT look at PRs, Jira, labels, or open anything — you only
resolve branches. Ticket handling and gating live in the caller.

## Input

- `<PRIORITY>`: one of `Critical` | `High` | `Medium` | `Low`.
  - Treat `Highest` as Critical-tier and `Lowest` as Low-tier.
  - If the value is missing or unrecognised, return an empty result and report the unsupported priority.

## Step 1: Parse the release policy

Fetch and parse the policy once here; later steps consume the sets produced below rather than re-reading the page.

- Fetch the page source of: https://docs.mattermost.com/product-overview/release-policy.html
- Locate the `<pre class="mermaid"> ... gantt ...` block in the "Releases" section.
- Unescape HTML entities such as `&amp;` before parsing.
- Parse each release row `vX.Y[ & ...] :<status>, <start>, <end>`:
  - Locate the status marker `:(crit|active|done),` and treat everything before that marker as the row label.
  - Do not assume the row label is only `vX.Y`. Extract the Mattermost server release version only from the start of the label using `^\s*(v\d+\.\d+)\b`. Ignore additional label text such as `& Desktop App v6.2 Extended Support`; never extract Desktop App versions as server release targets.
  - Rows tagged `:crit` are ESR (Extended Support) versions, even when their label contains extra descriptive text. There should always be at least one ESR row.
  - Rows tagged `:active` are active versions.
  - Rows tagged `:done` are end-of-life; ignore them.
- Let `ESR` = all `:crit` versions; `ACTIVE` = all `:active` versions; `UPCOMING` = the highest-numbered ACTIVE version (the next release).

## Step 2: Map priority to candidate versions

- Critical / High / Medium  ->  `ACTIVE ∪ ESR`
- Low                       ->  `{UPCOMING} ∪ ESR`

## Step 3: Determine target release branches

Use the candidate version set from Step 2 — do not re-fetch or re-parse the release policy.

- Map each candidate version `vX.Y` to the branch `release-X.Y` (drop the leading `v`, keep major.minor only, e.g. `v11.7 -> release-11.7`).
- Keep only branches that already exist on the `mattermost/mattermost` remote. Always use the explicit URL — never bare `origin`, which may point to a different repository when this skill is invoked from a plugin checkout:

  ```bash
  git ls-remote --heads https://github.com/mattermost/mattermost.git release-X.Y
  ```

  (This enforces "upcoming version only if its branch has already been created"; ESR and shipped active branches will exist, an uncut upcoming branch will be skipped.)
- Dedupe.

## Output

Return the deduped list of existing `release-X.Y` target branches. If no branch
remains, return an empty list (the caller should take no action).
