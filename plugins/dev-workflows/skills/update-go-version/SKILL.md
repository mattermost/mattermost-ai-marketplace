---
name: update-go-version
description: "Update the Go version in go.mod and related config files (CI workflows, Dockerfiles, Makefiles) to the latest stable release. Fetches the current version from go.dev, updates all relevant files, runs go mod tidy, and commits. Use when the user asks to update Go, upgrade the Go version, bump go.mod, migrate to a newer Go release, or keep Go toolchain current."
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# Update Go Version

Update all Go module files and CI configuration to the latest stable Go release.

## Instructions

### Phase 0: Discover the latest stable Go version

Fetch the latest stable version from the official Go downloads API:

```bash
curl -s 'https://go.dev/dl/?mode=json' | jq -r '[.[] | select(.stable == true)][0].version' | sed 's/^go//'
```

This returns the full patch version (e.g. `1.24.1`). Derive the minor-only form (e.g. `1.24`) by stripping the patch segment — use the minor form in `go.mod` and the full version everywhere else.

### Phase 1: Identify files to update

Find all Go modules and config files that reference a Go version:

```bash
find . -name go.mod -not -path '*/vendor/*'
find . -name '*.yml' -path '*/.github/workflows/*'
grep -rl 'GO_VERSION\|golang:' Makefile Dockerfile docker-compose.yml .tool-versions 2>/dev/null
```

Files that typically contain the Go version:
- `go.mod` — `go X.Y` directive and optional `toolchain goX.Y.Z`
- `.github/workflows/*.yml` — `go-version:` fields (quoted or unquoted)
- `Makefile` — `GO_VERSION ?= X.Y.Z` or similar variables
- `Dockerfile` / `docker-compose.yml` — `FROM golang:X.Y.Z`
- `.tool-versions` (asdf) — `golang X.Y.Z`

### Phase 2: Check current versions

For each `go.mod`, read the current `go` directive. If it is already at the latest version, log that fact for this module and continue to the next module (nothing to do for this one).

### Phase 3: Update files

For each file identified above, update the Go version string using precise replacements:

- **`go.mod`**: Update the `go` directive (e.g. `go 1.23` → `go 1.24`) and `toolchain` if present (e.g. `toolchain go1.23.5` → `toolchain go1.24.1`).
- **CI YAML**: Match both quoted and unquoted `go-version:` values:
  ```bash
  grep -n 'go-version:' .github/workflows/*.yml
  ```
- **Makefiles**: Update version variables only — do not touch logic.
- **Dockerfiles**: Update the `golang:` image tag.

### Phase 4: Tidy and verify

For each updated `go.mod`:

1. `cd` into the module directory.
2. Run `go mod tidy` to update `go.sum` for the new toolchain.
3. If a `vendor/` directory exists, run `go mod vendor`.
4. Run `go build ./...` to confirm nothing broke.
5. Run `go test ./...` — note any failures and whether they are pre-existing.

### Phase 5: Commit

1. Stage `go.mod`, `go.sum`, `vendor/` (if present), and any updated config files.
2. Commit with a message like:

```text
chore(go): update Go version to X.Y.Z
```

3. Print a summary of every file changed and the old → new version in each.

## Notes

- Always fetch the live version from `https://go.dev/dl/?mode=json` — do not hard-code a version.
- Use the **minor** version (`1.24`) in `go.mod` and the **full patch** version (`1.24.1`) everywhere else, unless the existing file already uses a different precision.
- Do not update `go.mod` to a version lower than the current one.
- If the repo pins Go via `toolchain` directive, update both `go` and `toolchain`.
