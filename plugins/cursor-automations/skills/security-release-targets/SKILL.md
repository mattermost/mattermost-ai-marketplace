---
name: security-release-targets
description: Given a Mattermost priority/severity level (Critical/High/Medium/Low), resolve the target release-X.Y branches to cherry-pick onto by parsing the Mattermost release policy (ESR/active/upcoming) and keeping only branches that exist on origin. Use when you need the list of release branches a fix must be backported to for a given severity.
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

- Fetch the page source of: https://docs.mattermost.com/product-overview/release-policy.html
- Locate the `<pre class="mermaid"> ... gantt ...` block in the "Releases" section.
- Parse each release row `vX.Y[ & ...] :<status>, <start>, <end>`:
  - rows tagged `:crit` are ESR (Extended Support) versions.
  - rows tagged `:active` are active versions.
  - rows tagged `:done` are end-of-life; ignore them.
- Let `ESR` = all `:crit` versions; `ACTIVE` = all `:active` versions; `UPCOMING` = the highest-numbered ACTIVE version (the next release).

## Step 2: Map priority to candidate versions

- Critical / High / Medium  ->  `ACTIVE ∪ ESR`
- Low                       ->  `{UPCOMING} ∪ ESR`

## Step 3: Map to branches and filter to what exists

- Map each candidate version `vX.Y` to the branch `release-X.Y` (drop the leading `v`, keep major.minor only, e.g. `v11.7 -> release-11.7`).
- Keep only branches that already exist on origin:

  ```bash
  git ls-remote --heads origin release-X.Y
  ```

  (This enforces "upcoming version only if its branch has already been created"; ESR and shipped active branches will exist, an uncut upcoming branch will be skipped.)
- Dedupe.

## Output

Return the deduped list of existing `release-X.Y` target branches. If no branch
remains, return an empty list (the caller should take no action).
