---
name: plugin-security-release-targets
description: Given a Mattermost priority/severity level and a plugin repository, resolve the target plugin release-X.Y branches by cross-referencing the platform release policy with the plugin versions declared in each platform Makefile. Returns only branches that exist on the plugin's origin.
allowed-tools: Read, Bash(git ls-remote:*), Bash(gh api:*), WebFetch
---

# Resolve target plugin release branches for a severity

You take a priority/severity level and a plugin identifier, then return the set of
plugin `release-X.Y` branches that a fix at that level must be cherry-picked onto.
The resolution works by mapping platform release versions (from Mattermost release
policy) to the plugin version each platform release ships with (from the server
Makefile), and then mapping those plugin versions to plugin release branches.

You do NOT look at PRs, Jira, labels, or open anything — you only resolve branches.
Ticket handling, gating, and cherry-pick execution live in the caller.

## Inputs

- `<PRIORITY>`: one of `Critical` | `High` | `Medium` | `Low`.
  - Treat `Highest` as Critical-tier and `Lowest` as Low-tier.
  - If the value is missing or unrecognised, return an empty result and report the unsupported priority.
- `<PLUGIN_REPO>`: the `owner/repo` of the plugin (e.g. `mattermost/mattermost-plugin-jira`).
- `<MAKEFILE_NAME>`: the artifact name as it appears in the platform Makefile (e.g. `mattermost-plugin-jira`). Used to grep for the bundled version.

## Step 1: Parse the Mattermost release policy

- Fetch the page source of: https://docs.mattermost.com/about/release-policy.html
- Locate the `<pre class="mermaid"> ... gantt ...` block in the "Releases" section.
- Parse each release row `vX.Y[ & ...] :<status>, <start>, <end>`:
  - rows tagged `:crit` are ESR (Extended Support) versions.
  - rows tagged `:active` are active versions.
  - rows tagged `:done` are end-of-life; ignore them.
- Let `ESR` = all `:crit` versions; `ACTIVE` = all `:active` versions; `UPCOMING` = the highest-numbered ACTIVE version (the next release).

## Step 2: Map priority to candidate platform versions

- Critical / High / Medium  ->  `ACTIVE ∪ ESR`
- Low                       ->  `{UPCOMING} ∪ ESR`

## Step 3: Look up the plugin version in each platform release Makefile

For each candidate platform version `X.Y`:

1. Fetch `https://raw.githubusercontent.com/mattermost/mattermost/refs/heads/release-X.Y/server/Makefile`.
2. Grep for `<MAKEFILE_NAME>`. Exclude any lines containing `fips`. Extract the full artifact name up to and including the semver (e.g. `mattermost-plugin-jira-v4.7.0`).
3. Parse the semver: `vMAJOR.MINOR.PATCH`. Keep only `MAJOR.MINOR` for branch resolution.

If the Makefile does not exist for a platform version (branch not yet cut) or the plugin is not found in it, skip that platform version.

## Step 4: Map to plugin release branches and filter to what exists

- Map each resolved plugin version `vX.Y` (major.minor) to the branch name `release-X.Y` on the plugin repository.
- Deduplicate: multiple platform releases may ship the same plugin version.
- Keep only branches that actually exist on the plugin's remote:

  ```bash
  git ls-remote --heads https://github.com/<PLUGIN_REPO>.git release-X.Y
  ```

  Alternatively, if you are already in a checkout of the plugin:

  ```bash
  git ls-remote --heads origin release-X.Y
  ```

## Output

Return the deduped list of existing plugin `release-X.Y` target branches, in ascending order. If no branch remains, return an empty list (the caller should take no action).
