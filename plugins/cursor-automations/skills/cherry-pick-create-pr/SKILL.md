---
name: cherry-pick-create-pr
description: Cherry-pick a single merged commit onto one release-X.Y branch, correctly resolving conflicts, running lint in a separate commit, pushing, and opening a cherry-pick PR via the create_pr_tool MCP following the PR template. Self-contained (carries its own conflict-resolution logic). Use inside a per-branch subagent when backporting a merged PR to a release branch. Has side effects (push + open PR).
disable-model-invocation: true
---

# Cherry-pick a commit onto a release branch and open a PR

You cherry-pick one merged commit onto a single release branch and open one
cherry-pick PR for it. You run entirely non-interactively. Never force-push,
never amend an existing commit, never run `git cherry-pick --skip`.

## Commit attribution — ABSOLUTE REQUIREMENT

Every follow-up commit created by this agent (lint/type fix-up commits, and any
other commit you author) **must** end with the following trailer on its own
line, separated from the rest of the message by a blank line:

```text
Co-authored-by: mattermost-code <matty-code@mattermost.com>
```

This does NOT apply to the cherry-pick commit itself — that commit preserves the
original author's message and authorship and must not be amended.

This is non-negotiable for the commits you author: it is what attributes the
work correctly on GitHub and is required by Mattermost's tooling. Do not omit
it, do not reword it, do not change the email, and do not put it on the same
line as another trailer.

## Inputs

You receive:

- `<REPO_NAME>`: the `owner/repo` to cherry-pick in and open the PR against. Optional — if missing, use `mattermost/mattermost`. Also selects which lint suite runs in step 4.
- `<PR_NUMBER>`: the original merged PR number.
- `<PR_AUTHOR>`: the original PR author's `login`.
- `<COMMIT_SHA>`: the merge/commit SHA to cherry-pick.
- `<ORIGINAL_BRANCH>`: the `headRefName` of the merged PR (the source branch of the PR being cherry-picked) — never the active/local branch name.
- `release-X.Y`: the single target release branch for this run.
- `<REVIEWERS>`: the list of GitHub logins to request review from. Optional — if missing, default to [`<PR_AUTHOR>`]. Always deduplicate, and always keep `<PR_AUTHOR>` in the final list even if the caller omitted them.
- `<LABELS>`: the list of labels to apply to the cherry-pick PR. Optional — if missing, apply no labels. Never invent labels the caller did not pass.

The cherry-pick branch name for this target is:

```text
automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y
```

**Important:** `<ORIGINAL_BRANCH>` must always be the `headRefName` from the merged PR — never the name of the active Cursor branch or any other locally derived name.

## 1. Determine the cherry-pick form

Repositories differ in how they merge: a squash merge produces a single-parent commit, a standard merge produces a two-parent commit. Decide the command once, from the commit's parents:

```bash
git cat-file -p <COMMIT_SHA> | head -20
```

- one parent  -> `CMD = git cherry-pick <COMMIT_SHA>`
- two parents -> `CMD = git cherry-pick -m 1 <COMMIT_SHA>`

Never assume the form. Cherry-picking a two-parent commit without `-m 1` fails outright.

## 2. Fetch and branch off the release tip

```bash
git fetch origin release-X.Y
git checkout -B automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y origin/release-X.Y
```

## 3. Cherry-pick and resolve conflicts correctly (a single, properly-resolved cherry-pick commit)

Run `CMD` (determined in step 1).

**Empty cherry-pick (change already on branch):** The target branch may already contain the incoming change, producing an empty cherry-pick. Detect this when any of the following is true:
- Git reports that the cherry-pick is empty (e.g. "The previous cherry-pick is now empty").
- After a clean apply or conflict resolution, `git diff origin/release-X.Y` shows no changes.

When detected, abort — do NOT run `git cherry-pick --skip` or `git cherry-pick --continue`:

```bash
git cherry-pick --abort
```

Skip this branch and report `skipped: change already on release-X.Y`. Do not push or open a PR.

- **Clean apply (non-empty):** the resulting commit is the cherry-pick as-is. Confirm `git diff origin/release-X.Y` is non-empty, then proceed to lint.
- **On conflict:** do NOT blindly accept either side. Never run `git checkout --theirs` / `git checkout --ours` (or any equivalent whole-file "take one side" resolution) — doing so can silently drop code or tests that exist on the release branch and lose data. Instead, resolve each conflict by understanding the incoming change and integrating it correctly:
  1. Inspect the intent of the incoming change with `git show <COMMIT_SHA>` (and the surrounding original PR context) so you understand exactly what the cherry-picked commit is trying to do.
  2. For each conflicted path (`git diff --name-only --diff-filter=U`), open the file and read every conflict hunk to understand BOTH the incoming (cherry-picked) change and the existing release-branch content.
  3. Manually edit each conflicted region so the incoming change is correctly applied to `release-X.Y`, re-applying any branch-specific logic that the incoming change would otherwise overwrite. Preserve all release-branch code and tests that are unrelated to the incoming change — never delete or weaken them to make the merge "go away".
  4. Keep a concise per-file note of exactly what you reconciled (for the PR body). Do NOT mention security, vulnerability, CVE, exploit, or any related terms in these notes; describe only the structural or logical change made to reconcile the code.

  Once EVERY conflict is resolved and the working tree reflects a correct integration, re-check for an empty cherry-pick (`git diff origin/release-X.Y`). If empty, abort per the empty-cherry-pick steps above. Otherwise:

  ```bash
  git add -A
  git cherry-pick --continue --no-edit
  ```

  This yields one correctly-resolved cherry-pick commit — there is no separate "take-theirs" dump commit and no follow-up "resolve conflicts" commit; the resolution lives inside the cherry-pick itself. Leave this commit's message and authorship as-is — do not amend it or add a trailer to it.

**Conflict resolution constraint:** When resolving conflicts, do NOT remove or edit any code that is not directly related to the incoming change. Do not delete tests or other code present in the release branch that are not part of the original commit being cherry-picked.

**Escalate instead of guessing:** Do NOT auto-resolve conflicts in config files, DB migrations, or anything marked "DO NOT AUTO-MERGE". If a conflict is in one of these, or you cannot confidently determine the correct integration, run `git cherry-pick --abort`, skip this branch, and report it for human review.

## 4. Lint before opening the PR

Which checks to run depends on `<REPO_NAME>`.

**If `<REPO_NAME>` is `mattermost/mattermost`:** determine changed areas (`git diff --name-only` against `origin/release-X.Y`) and run the matching checks, applying auto-fixes:
- `server/`  -> (in `server/`) `make check-style`; run relevant generation checks (`make mocks`, `make store-layers`, `make i18n-extract` etc.) if those files changed and stage regenerated output.
- `webapp/`  -> (in `webapp/`) `npm run check` and `npm run check-types`; for i18n, run `npm run i18n-extract` in `webapp/channels` and only ever edit `en.json`.
- `e2e-tests/*` -> the matching `npm run check` / `make check-shell`.

**For any other repository (including all plugin repositories):** the directory layout and per-area targets above do not apply. Run only:

```bash
make check-style
```

If the repository has no `check-style` target, note that no lint suite was available and continue to the push step — do not guess at other targets.

Fix ALL lint and type errors — whether auto-fixable or requiring manual code edits. Analyze each error, apply the correct fix directly in the source, and re-run the check to confirm it passes before proceeding. Commit all lint and type fixes SEPARATELY from the cherry-pick:

```bash
git commit -am "$(printf 'Apply lint fixes\n\nCo-authored-by: mattermost-code <matty-code@mattermost.com>')"
```

Repeat the lint/fix/commit cycle until all checks pass cleanly.

## 5. Push

If you created any follow-up commits (e.g. lint/type fixes), verify each one you authored carries the required attribution trailer before pushing. The cherry-pick commit itself is exempt and keeps the original message.

```bash
# For a follow-up commit you authored (e.g. the lint-fix tip commit):
git log -1 --format=%B | grep -F 'Co-authored-by: mattermost-code <matty-code@mattermost.com>'
```

Then push:

```bash
git push -u origin automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y
```

## 6. Open the cherry-pick PR

### 6.1. Preflight — never open a PR that cannot be valid

Run these checks first. If any fails, do NOT open a PR; return `needs-input: <reason>` and stop.

1. The head branch exists on origin (it must already be pushed):

   ```bash
   git ls-remote --heads origin automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y
   ```

2. The head branch actually carries the change — never open an empty PR:

   ```bash
   git diff origin/release-X.Y...automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y
   ```

3. The base branch exists on origin:

   ```bash
   git ls-remote --heads origin release-X.Y
   ```

4. No open PR already targets this head — never open a duplicate:

   ```bash
   gh pr list --repo <REPO_NAME> --head automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y --state open --json url
   ```

   If one already exists, return that existing URL as the outcome and do NOT create a second PR.

### 6.2. Assemble the PR fields and open it

Use the `create_pr_tool` from the configured custom MCP (do NOT use `gh pr create` or the Cursor OpenGitPr tool). Pass the following parameters:
- `repo`: [`<REPO_NAME>`, mattermost/mattermost] (`<REPO_NAME>` is an optional value, if it's missing use mattermost/mattermost )
- `base`: release-X.Y
- `head`: automated-cherry-pick-of-<ORIGINAL_BRANCH>-release-X.Y
- `title`: Automated cherry pick of #`<PR_NUMBER>`
- `reviewers`: `<REVIEWERS>` as received, with `<PR_AUTHOR>` added if the caller omitted them, deduplicated. If `<REVIEWERS>` was not passed, use [`<PR_AUTHOR>`].
- `labels`: `<LABELS>` as received, verbatim. If `<LABELS>` was not passed, omit labels entirely.
- `body` (follow `.github/PULL_REQUEST_TEMPLATE.md`):

  ````markdown
  #### Summary
  Cherry pick of #<PR_NUMBER> on release-X.Y.

  #### Conflict Resolution Changes
  - <concise bullet per structural/logical change made while resolving conflicts — omit security, vulnerability, CVE, exploit, or any related terms; remove this section entirely on a clean cherry-pick>
  - <If no conflicts were resolved, state that as the only bullet point>

  #### Release Note
  ```release-note
  NONE
  ```
  ````

## Output

Report the outcome back to the caller: the created PR URL, or `skipped: <reason>`,
or `needs-input: <reason>` for a branch that needs human review.

## Constraints

- Never force-push; never amend any commit; never `git cherry-pick --skip`.
- Always determine the cherry-pick form from the commit's parent count. Never assume a squash merge — use `-m 1` for a two-parent commit.
- Never open a PR for an empty diff, for a branch that is not pushed, or for a head that already has an open PR.
- Every follow-up commit you author (e.g. lint/type fixes) MUST end with the trailer `Co-authored-by: mattermost-code <matty-code@mattermost.com>` on its own line, separated from the rest of the message by a blank line. This does NOT apply to the cherry-pick commit, which keeps the original author's message and is never amended. Do not omit it, reword it, change the email, or place it on the same line as another trailer.
- On an empty cherry-pick (change already on the release branch), run `git cherry-pick --abort` and skip the branch — never use `--skip` or `--continue` for empty picks.
- Resolve conflicts inside the cherry-pick itself (via `git cherry-pick --continue`) by correctly integrating the incoming change. Never resolve a conflict by blindly accepting one side (`git checkout --theirs` / `--ours` or equivalent), as this can lose data present on the release branch. Lint and type fixes go in a separate follow-up commit.
- When resolving conflicts, do not remove or edit code that is not directly related to the incoming change. Do not delete tests in the release branch that are not part of the original commit.
- Do not auto-resolve conflicts in config files, DB migrations, or anything marked "DO NOT AUTO-MERGE" — abort the cherry-pick and report those for human review.
- Never use the words security, vulnerability, CVE, exploit, or semantically related terms in the PR title, PR body, or conflict resolution notes.
- Always use `create_pr_tool` from the configured custom MCP to open the PR. Do not use `gh pr create` or the Cursor OpenGitPr tool.
- Always include the original PR author (`<PR_AUTHOR>`) as a reviewer, whether or not the caller listed them in `<REVIEWERS>`.
- Apply only the labels passed in `<LABELS>`. Never add labels the caller did not pass, and never assume repository-specific labels exist.
- Run the full per-area lint suite only for `mattermost/mattermost`. For any other repository, `make check-style` is the only lint command.
