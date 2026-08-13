---
name: plugin-security-release-targets
description: Given a Mattermost priority/severity level and a plugin repository, resolve the target plugin release-X.Y branches by cross-referencing the platform release policy with the plugin versions declared in each platform Makefile. Returns only branches that exist on the plugin's origin.
allowed-tools: Read, Bash(git ls-remote:*), Bash(gh api:*), WebFetch
---

# Resolve target plugin release branches for a severity

You take a priority/severity level and a plugin identifier, then return the set of
plugin `release-X.Y` branches that a fix at that level must be cherry-picked onto.
The resolution works by: (1) delegating to `/cursor-automations:security-release-targets`
to get the set of active platform `release-X.Y` branches, then (2) looking up the
plugin version shipped in each platform release's Makefile, and finally (3) mapping
those plugin versions to plugin release branches that exist on the plugin's remote.

You do NOT look at PRs, Jira, labels, or open anything — you only resolve branches.
Ticket handling, gating, and cherry-pick execution live in the caller.

## Inputs

- `<PRIORITY>`: one of `Critical` | `High` | `Medium` | `Low`. Optional — if omitted, defaults to `Critical` (which resolves to all `ACTIVE ∪ ESR` platform versions, giving the broadest coverage).
  - Treat `Highest` as Critical-tier and `Lowest` as Low-tier.
  - If the value is unrecognised, return an empty result and report the unsupported priority.
- `<PLUGIN_REPO>`: the `owner/repo` of the plugin (e.g. `mattermost/mattermost-plugin-jira`).
- `<MAKEFILE_NAME>`: the artifact name as it appears in the platform Makefile (e.g. `mattermost-plugin-jira`). Used to grep for the bundled version.

## Step 1: Resolve platform release branches via `security-release-targets`

Invoke the `/cursor-automations:security-release-targets` skill with `<PRIORITY>` (or `Critical` if priority was omitted). That skill:

1. Parses the Mattermost release policy (gantt chart at https://docs.mattermost.com/about/release-policy.html)
2. Maps the priority to candidate platform versions (`ACTIVE ∪ ESR` for Critical/High/Medium; `{UPCOMING} ∪ ESR` for Low)
3. Filters to branches that exist on origin

Take its output — a deduped list of platform `release-X.Y` branches — as `PLATFORM_BRANCHES`.

If `PLATFORM_BRANCHES` is empty, return an empty list immediately.

## Step 2: Look up the plugin version in each platform release Makefile

For each platform branch `release-X.Y` in `PLATFORM_BRANCHES`:

1. Fetch `https://raw.githubusercontent.com/mattermost/mattermost/refs/heads/release-X.Y/server/Makefile`.
2. Grep for `<MAKEFILE_NAME>`. Exclude any lines containing `fips`. Extract the full artifact name up to and including the semver (e.g. `mattermost-plugin-jira-v4.7.0`).
3. Parse the semver: `vMAJOR.MINOR.PATCH`. Keep only `MAJOR.MINOR` for branch resolution.

If the Makefile does not exist for a platform version (branch not yet cut) or the plugin is not found in it, skip that platform version.

## Step 3: Map to plugin release branches and filter to what exists

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
