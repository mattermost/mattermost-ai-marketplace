# dev-workflows

Skills for common development workflows — dependency management, module hygiene, and routine maintenance tasks.

## Skills

### `update-go-deps`

Update all direct Go module dependencies to their latest versions, tidy the module graph, verify tests pass, and commit the result.

**Usage:** `/dev-workflows:update-go-deps`

**When to use:**
- Routine dependency bumps
- Addressing CVEs in transitive deps
- Keeping `go.sum` clean after manual edits to `go.mod`

**What it does:**
1. Finds all `go.mod` files in the repo
2. Runs `go get -u ./...` and `go mod tidy` in each module
3. Syncs `vendor/` if present
4. Verifies the build and tests still pass
5. Summarises what changed and commits `go.mod` / `go.sum` / `vendor/`

### `update-go-version`

Update the Go toolchain version to the latest stable release across all modules and CI config.

**Usage:** `/dev-workflows:update-go-version`

**When to use:**
- After a new Go release lands and you want to stay current
- Before a release or security audit that requires a specific minimum version
- When CI starts complaining about an outdated toolchain

**What it does:**
1. Fetches the latest stable Go version from `https://go.dev/dl/?mode=json`
2. Finds all `go.mod`, CI YAML, Makefile, Dockerfile, and `.tool-versions` files
3. Updates the `go` directive (and `toolchain` if present) in each `go.mod`
4. Updates `go-version:` in GitHub Actions workflows and other config files
5. Runs `go mod tidy` and `go build ./...` to verify
6. Commits all changes with a clear message

### `update-github-actions`

Update all GitHub Actions `uses:` references in `.github/workflows/` to their latest released versions.

**Usage:** `/dev-workflows:update-github-actions`

**When to use:**
- Routine CI maintenance to stay on supported action versions
- After a security advisory on a specific action
- Before enabling Dependabot so the baseline is already current

**What it does:**
1. Finds every `uses:` reference across all workflow YAML files
2. Fetches the latest release for each action from the GitHub API
3. Updates semver-pinned references (`@v3` → `@v4`, `@v3.1.0` → `@v3.2.1`)
4. Updates all SHA-pinned references — resolves the latest SHA and version comment; bare SHA pins with no comment are resolved to `@sha # vX.Y.Z` using the latest release
5. Flags major-version bumps that may have breaking changes
6. Commits only `.github/workflows/` files with a summary table
