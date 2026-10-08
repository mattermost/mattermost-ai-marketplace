---
name: Playground Bootstrap
description: Pre-flight for /prfaq-prototype. Makes sure the active target playground exists inside the workspace. If it's missing and the target profile names a repo, prompts the user to clone a fresh copy (plus any companion repos it needs) and install dependencies; if it exists, verifies it's the expected sandbox repo, never a production repo. Never clones, installs, pulls, or resets without the user's yes.
version: 1.0.0
author: Mattermost Design Team
tags: [prototype, playground, bootstrap, git, clone, sandbox, target-profile, fast-path]
---

# Playground Bootstrap

## Purpose

Stage 2 builds into a sandbox playground at the target profile's `workspace_relative_root`. On a fresh
project that folder doesn't exist yet. This skill closes that gap: it offers to clone the playground (and
its companion repos) into the workspace, installs dependencies, and verifies an existing checkout is the
right repo — so the pipeline can run end to end from an empty folder.

## When to Use

- Pre-flight of every `/prfaq-prototype:prototype` run, after target-profile resolution and before
  Stage 1. Run by the command (top-level assistant), which can prompt the user.
- Re-run before Stage 2 if the playground was removed or moved mid-run.

## Input

```json
{
  "target_profile": "The resolved target profile (incl. project override and --target).",
  "workspace_root": "Absolute path of the project workspace (containment root)."
}
```

Profile fields used: `workspace_relative_root`, `repo_url`, `default_branch`, `companion_repos[]`
(`{ name, repo_url, default_branch, workspace_relative_path, why }`), `commands.install`,
`node_version_file`.

## Step 1 — Containment (security, always first)

Canonicalize `workspace_relative_root` and every `companion_repos[].workspace_relative_path` against
`workspace_root`. Each must stay **inside** the workspace. Reject absolute paths, `..` that escapes, and
symlinks that resolve outside. Abort with the specific path on failure. Re-check right before cloning.

## Step 2 — Playground present?

### 2a. Present → verify it

- It must be a git checkout. Read `git -C <root> remote get-url origin` and normalize both it and the
  profile's `repo_url` (`git@github.com:o/r.git` ≡ `https://github.com/o/r(.git)`).
- **Mismatch** → stop: "`<root>` is a checkout of `<actual>`, not the playground `<expected>`." Never
  build into it. (This is the guard that keeps the pipeline out of the production `mattermost` repo.)
- No `repo_url` in the profile → skip the remote check, but still refuse a remote that is
  `mattermost/mattermost` or `mattermost/mattermost-webapp`.
- If `node_modules/` is missing, offer to run the install command (Step 4).
- **Never** `pull`, `reset`, `checkout`, or `clean` an existing playground — it may hold the user's
  unpushed prototypes. If it looks stale, you may mention `git -C <root> pull --ff-only` as a suggestion.
- Then check companions (Step 3).

### 2b. Missing, profile has no `repo_url` → abort

Tell the user to clone or point at their playground: copy the bundled
`config/prototype-targets.json` into the project as `prototype-targets.json` and set
`workspace_relative_root`.

### 2c. Missing, profile has a `repo_url` → ask

Use the host's interactive question picker. Say exactly what will happen:

> "There's no prototype playground in this project yet. I can clone **<repo_url>** into
> `<workspace_relative_root>`<, plus **<companion>** into `<path>` (<why>)>, then run `<install>`.
> This downloads the repos and their npm packages."

Options:

1. **Clone a fresh copy (Recommended)** — clone + install as described.
2. **Use a playground I already have** — explain: copy the bundled config into the project as
   `prototype-targets.json` and set `workspace_relative_root` to a folder inside this project, then
   re-run. (The playground must live inside the workspace.)
3. **Stop.**

Only option 1 proceeds. Never clone without this explicit yes.

## Step 3 — Companion repos

For each `companion_repos[]` entry whose path is missing, include it in the Step 2c prompt (or, when the
playground already exists, ask the same question for just the companion). Present companions are verified
the same way as the playground (remote matches `repo_url`), but never modified.

## Step 4 — Clone and install (after the yes)

1. Re-run Step 1 containment.
2. `git clone --branch <default_branch> <repo_url> <workspace_relative_root>`; same for each missing
   companion at its path. Use the user's existing git credentials; if a clone fails on auth, tell them to
   run `gh auth login` (or fix SSH) themselves — never ask for a token in chat.
3. If the profile names a `node_version_file` (e.g. `.nvmrc`), compare it with `node --version`; on a
   major-version mismatch, warn (don't switch versions for the user) and continue.
4. Run the install command in `<workspace_relative_root>`. On failure, show the tail of the error and
   stop — don't retry with `--force` or `--legacy-peer-deps` unless the user asks.
5. Verify: the conventions docs and `manifest_file` from the profile exist. If the profile references a
   file that doesn't exist in the fresh clone, report it as `PROFILE_DRIFT` (the builder will trust the
   live files).

## Output

```json
{
  "status": "ready | cloned | aborted",
  "root": "prototype-playground/proto-playground",
  "remote": "https://github.com/mattermost/mattermost-proto-playground",
  "companions": [ { "name": "compass-design", "path": "prototype-playground/compass-design", "status": "cloned | present" } ],
  "installed": true,
  "warnings": [ "node 22 vs .nvmrc 24", "PROFILE_DRIFT: <path>" ]
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `PATH_ESCAPE` | Root or companion path leaves the workspace | Abort; name the path. |
| `REMOTE_MISMATCH` | Existing folder is a different repo | Abort; never build into it. |
| `NO_REPO_URL` | Playground missing and profile has no `repo_url` | Abort with the copy-config instructions. |
| `CLONE_FAILED` | Network/auth error | Report; suggest `gh auth login` / SSH fix; stop. |
| `INSTALL_FAILED` | npm install error | Report the error tail; stop. |
| `USER_DECLINED` | User chose option 2 or 3 | Stop cleanly with the matching instructions. |

## Related Skills

- **prfaq-source-resolver** — the other pre-flight step (gets the PRFAQ into `PRFAQs/`).
- **sandbox-scaffolder** — assumes this skill has run; reports `ROOT_MISSING` if it hasn't.
