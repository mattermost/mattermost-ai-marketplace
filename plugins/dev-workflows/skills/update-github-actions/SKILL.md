---
name: update-github-actions
description: Update all GitHub Actions workflow dependencies (uses: owner/action@vX) to their latest released versions. Fetches current releases from GitHub, updates all workflow YAML files, and commits.
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch, mcp__github-server__list_commits
---

# Update GitHub Actions Dependencies

Scan all `.github/workflows/*.yml` files, find every `uses:` reference, resolve the latest release for each action, and update in place.

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
- `uses: owner/repo@<sha>` — pinned to a commit SHA (skip these — do not change SHA pins without user confirmation)
- `uses: ./.github/actions/local` — local action (skip)

Deduplicate the list. For each unique `owner/repo` reference, record the current version string.

### Phase 2: Resolve latest versions

For each `owner/repo`, fetch the latest release from GitHub:

```
https://api.github.com/repos/{owner}/{repo}/releases/latest
```

If the action does not publish GitHub Releases, fall back to the latest tag:

```
https://api.github.com/repos/{owner}/{repo}/tags
```

Record the latest version tag (e.g. `v4.1.0`). Also note the major version alias (e.g. `v4`) — some repos maintain floating major-version tags.

### Phase 3: Determine update strategy

For each reference, decide how to update based on what the workflow currently uses:
- Currently `@vX.Y.Z` → update to latest `@vX'.Y'.Z'` (full semver)
- Currently `@vX` → update to latest major version `@vX'` only if a newer major exists; otherwise leave as-is
- Currently `@<sha>` with no comment → skip unless the user explicitly asked to unpin
- Currently `@<sha> # vX.Y.Z` → **update**: resolve the latest release SHA and version tag, replace both the SHA and the comment (e.g. `@abc123 # v3.0.1` → `@def456 # v4.1.0`)

Report any major-version bumps separately — these may have breaking changes.

### Phase 4: Resolve commit SHAs for SHA-pinned actions

For any action pinned as `@<sha> # vX.Y.Z`, fetch the commit SHA for the latest release tag:

```
https://api.github.com/repos/{owner}/{repo}/git/ref/tags/{latest-tag}
```

If the tag is an annotated tag (type `tag`), follow the `object.url` to get the underlying commit SHA. If it is a lightweight tag (type `commit`), use the SHA directly.

### Phase 5: Update workflow files

For each workflow file, replace outdated version strings using exact string replacement. Update every occurrence of each action reference.

Semver-pinned example:
```yaml
# before
uses: actions/checkout@v3
# after
uses: actions/checkout@v4
```

SHA-pinned with comment example:
```yaml
# before
uses: actions/download-artifact@9782bd6a9848b53b110e712e20e42d89988822b7 # v3.0.1
# after
uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4.1.0
```

### Phase 5: Summarise and commit

1. Print a table of all changes:
   | Action | Old version | New version | Major bump? |
   |--------|-------------|-------------|-------------|

2. If any major-version bumps are present, note that the action's changelog should be reviewed for breaking changes and provide the GitHub releases URL.

3. Stage only `.github/workflows/` files.

4. Commit:

```
chore(ci): update GitHub Actions to latest versions

<paste summary table>
```

5. Ask the user if they want to push or open a PR.

## Notes

- SHA-pinned actions with a version comment (`@<sha> # vX.Y.Z`) are updated — both the SHA and the comment are replaced with the latest release.
- SHA-pinned actions with no comment are left unchanged — these are intentional pins with no declared version to track.
- If an action's latest release is a pre-release (`-beta`, `-rc`), skip it and use the latest stable release instead.
- Some actions (e.g. `github/codeql-action`) release very frequently — confirm the version looks sane before committing.
