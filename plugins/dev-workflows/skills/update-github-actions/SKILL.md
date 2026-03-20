---
name: update-github-actions
description: Update all GitHub Actions workflow dependencies (uses: owner/action@vX) to their latest released versions. Fetches current releases from GitHub, updates all workflow YAML files to use SHA pinning with version comments, and commits.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, mcp__github-server__list_commits
---

# Update GitHub Actions Dependencies

Scan all `.github/workflows/*.yml` files, find every `uses:` reference, resolve the latest release for each action, and update in place. **All actions are migrated to SHA pinning with a version comment** (e.g. `@abc123 # v4.1.0`) for supply-chain security.

## Instructions

### Phase 0: Prepare

1. Confirm the working tree is clean: `git status`. If there are uncommitted changes, stop and ask the user how to proceed.
2. Create a new branch: `git switch -c update-github-actions`.

### Phase 1: Collect all action references

Find all workflow files:

```bash
find .github/workflows -name '*.yml' -o -name '*.yaml'
```

Extract every `uses:` line. Each reference has one of these forms:
- `uses: owner/repo@vX.Y.Z` — pinned to a semver tag
- `uses: owner/repo@vX` — pinned to a major-version tag
- `uses: owner/repo@<sha> # vX.Y.Z` — already SHA-pinned with version comment
- `uses: owner/repo@<sha>` — SHA-pinned with no comment (treat as unknown version)
- `uses: ./.github/actions/local` — local action (skip)

Deduplicate the list. For each unique `owner/repo` reference, record the current version string.

### Phase 2: Resolve latest versions

For each `owner/repo`, fetch the latest release from GitHub:

```text
https://api.github.com/repos/{owner}/{repo}/releases/latest
```

If the action does not publish GitHub Releases, fall back to the latest tag:

```text
https://api.github.com/repos/{owner}/{repo}/tags
```

Record the latest version tag (e.g. `v4.1.0`).

### Phase 3: Resolve commit SHAs

For every action (regardless of how it is currently pinned), fetch the commit SHA for the latest release tag:

```text
https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{latest-tag}
```

If the tag is an annotated tag (type `tag`), follow the `object.url` to get the underlying commit SHA. If it is a lightweight tag (type `commit`), use the SHA directly.

The target format for every action reference is:
```text
uses: owner/repo@<full-commit-sha> # vX.Y.Z
```

### Phase 4: Determine changes

For each reference, compare the current state to the target SHA-pinned form:
- Currently `@vX.Y.Z` → migrate to `@<sha> # vX'.Y'.Z'`
- Currently `@vX` → migrate to `@<sha> # vX'.Y'.Z'`
- Currently `@<sha> # vX.Y.Z` → update SHA and version tag to latest
- Currently `@<sha>` with no comment → update to `@<sha> # vX'.Y'.Z'` using the resolved latest release

Report any major-version bumps separately — these may have breaking changes.

### Phase 5: Update workflow files

For each workflow file, replace every action reference with its SHA-pinned form using exact string replacement.

Examples:
```yaml
# before (semver tag)
uses: actions/checkout@v3
# after
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.1.0
```

```yaml
# before (major-version tag)
uses: actions/setup-go@v4
# after
uses: actions/setup-go@d35c59abb061a4a6fb18e82ac0862c26744d6ab5 # v5.5.0
```

```yaml
# before (SHA-pinned, stale)
uses: actions/download-artifact@9782bd6a9848b53b110e712e20e42d89988822b7 # v3.0.1
# after
uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4.1.0
```

### Phase 6: Summarise and commit

1. Print a table of all changes:
   | Action | Old version | New version | Major bump? |
   |--------|-------------|-------------|-------------|

2. If any major-version bumps are present, note that the action's changelog should be reviewed for breaking changes and provide the GitHub releases URL.

3. Stage only `.github/workflows/` files.

4. Commit:

```text
chore(ci): update GitHub Actions to latest versions

<paste summary table>
```

5. Ask the user if they want to push or open a PR.

## Notes

- Every action is migrated to `@<sha> # vTag` format — this is the target state regardless of how the action was previously pinned.
- If an action's latest release is a pre-release (`-beta`, `-rc`), skip it and use the latest stable release instead.
- Some actions (e.g. `github/codeql-action`) release very frequently — confirm the version looks sane before committing.
