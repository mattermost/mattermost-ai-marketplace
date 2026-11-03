---
name: review-pr
description: Two-phase security review (paranoid + critical) of a Mattermost PR, in an isolated worktree, with test-driven verification of each Medium+ finding
argument-hint: <PR number>
disable-model-invocation: true
---
# Security review for PR $ARGUMENTS

Execute a full two-phase security review of the Mattermost PR with the given ID. The argument is the PR number.

## Concurrency rule (read first)

The checkout your session starts in is on the default branch, and the subagents you launch share one `.git`, one working tree and one `HEAD`. **Never run `gh pr checkout`, `git checkout`, `git switch`, `git pull` or any other command that moves `HEAD` in the main working tree** — something else may be reading files from it right now, and you would corrupt that work (and it would corrupt yours).

This review must run entirely inside a **dedicated git worktree** created in Step 1. Every path handed to a subagent must be an absolute path inside that worktree.

## Step 1 — Fetch PR context and create an isolated worktree

First, resolve the target repository from the current working directory. Never hardcode a repo name:

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "Reviewing PR $ARGUMENTS in $REPO"
```

Then retrieve the PR metadata using that resolved repo:

```bash
gh pr view $ARGUMENTS --json number,title,body,baseRefName,headRefName,commits,files,state,mergeCommit --repo "$REPO"
```

If this fails, the PR number likely doesn't exist in this repository — stop and report that to the user. Do NOT fall back to a different repository. Extract:

- PR number
- Title
- Body (the "PR context")
- List of changed files
- `state` (OPEN or MERGED)
- `mergeCommit.oid` (the merge commit SHA, present when state is MERGED)

Now create the isolated worktree. `WT` is a directory under `/tmp` named after the review, so it never collides with another tree. Always use `--detach`: git refuses two worktrees on the same branch, and a detached HEAD pins the exact tree you want to review.

```bash
WT="/tmp/pr$ARGUMENTS-review"
git fetch origin
```

- If `state` is **MERGED**, pin the merge commit directly. This gives the exact post-merge tree with no unrelated local changes:

  ```bash
  git worktree add --detach "$WT" <mergeCommit.oid>
  ```

- If `state` is **OPEN**, fetch the PR head into a per-PR ref and pin it:

  ```bash
  git fetch origin "pull/$ARGUMENTS/head:refs/pr-review/$ARGUMENTS"
  git worktree add --detach "$WT" "refs/pr-review/$ARGUMENTS"
  ```

Verify the worktree before proceeding:

```bash
git -C "$WT" log -1 --oneline
git -C "$WT" status --short
```

If `git worktree add` fails because the path already exists (a previous aborted run), remove it with `git worktree remove --force "$WT"` and retry. Do not fall back to reviewing in the main working tree — abort and report to the user instead.

From here on, **`$WT` is the review root**. Use `git -C "$WT" ...` for every git command and absolute `$WT/...` paths for every file read.

## Step 1.5 — Linked context (you, not a subagent)

Scan the PR body for links (Confluence/Google Docs specs, Jira tickets, design docs). Decide which ones are worth reading and read them following these rules:

@../../prompts/pr-linked-context.md

Use the Atlassian MCP for Jira/Confluence links and the Google Docs connector for Google Docs links. Produce the LINKED CONTEXT section in the format defined there. It is passed to both reviewers in Steps 2 and 3.

## Step 2 — Paranoid reviewer (isolated subagent)

Invoke the `pr-paranoid-reviewer` subagent. Pass it:
- The PR number
- The absolute worktree path `$WT`, with an explicit instruction that **all file reads and all git commands must target that path** (`git -C "$WT"`, absolute `$WT/...` paths for `cat`/`grep`/Read). It must never read files from the main clone, whose `HEAD` may move mid-review, and must never move `HEAD` anywhere.
- The PR title and full body as the PR context
- The base branch (`baseRefName` from Step 1), to use as `<base_branch>` in its diff commands
- The LINKED CONTEXT section from Step 1.5, verbatim
- The COMPLETE list of changed files from the `gh pr view --json files` output in Step 1, verbatim. Instruct the subagent that this is the authoritative coverage scope: every backend (non-test) Go file in this list must be read in full and assigned a status.

The subagent will independently run `gh pr diff`. Pass it the resolved `$REPO` value explicitly, and instruct it to use `--repo "$REPO"` (never a hardcoded repository name). `gh` commands do not depend on the working tree, so they are safe from any directory.

When the subagent returns, validate its coverage inventory before continuing: confirm the number of files in its coverage table equals the number of files reported by `gh pr view --json files`, and that every backend non-test Go file has a `reviewed-*` status (never "skipped"). If any backend file is missing or unreviewed, send the subagent back (via SendMessage) to complete coverage before proceeding to Step 3. Do not advance with incomplete coverage.

Also sanity-check the paths it cites: if any finding references a path outside `$WT`, the subagent read the wrong tree — send it back to redo those files against `$WT`.

## Step 3 — Critical reviewer (isolated subagent)

Once the paranoid reviewer subagent has finished, invoke the `pr-critical-reviewer` subagent. Pass it:
- The PR number
- The absolute worktree path `$WT`, with the same instruction as in Step 2: read only from `$WT`, never move `HEAD`.
- The complete list of findings produced by the paranoid reviewer subagent (verbatim, with all finding IDs)
- The PR title and body, and the LINKED CONTEXT section from Step 1.5, verbatim

The critical reviewer subagent must NOT receive any context about the paranoid reviewer's reasoning, exploration steps, or intermediate thoughts — only the final list of findings. This isolation is intentional and mandatory.

## Step 4 — Test-driven verification (isolated subagent, one per finding)

Every finding rated MEDIUM or higher that the critical reviewer kept as a TRUE POSITIVE (severity as adjusted by the critical reviewer) must be verified by test before it is reported. This step is mandatory and cannot be skipped. A valid red test that fails for the vulnerable reason is the proof; do not re-trace the code yourself on top of it.

Run it sequentially, one finding at a time, all in `$WT` (they share one tree, and the subagent restores it after each finding). For each one, invoke the `pr-finding-verifier-tdd` subagent. Pass it:
- The finding's ID, title, file/lines and description, and the critical reviewer's verdict, severity, attack chain and attacker privilege, verbatim, as FINDING and CRITIC_ANALYSIS
- The absolute worktree path `$WT` as WT
- The PR number, title and the list of changed files from Step 1

It returns a JSON object. Act on its `verification` value:

- **CONFIRMED_BY_TEST:** first check the test yourself against its `realism_audit` and `red_test.output`: the attacker is the lowest-privilege role that can reach the path, the entry point is a real one that exercises the guards, the input is the finding's, and the failure is the vulnerable behavior (not a setup or compile error). If any of these fails, send the subagent back (SendMessage) to fix the test and rerun it. Once it holds, the finding is a confirmed true positive: report it with no confidence note.
- **NOT_REPRODUCED:** run the same check on the test. If it is valid and still passes, the finding is a false positive: silently discard it, together with its PR comment. If the test is defective, send the subagent back once to fix it; never discard a finding on a test you have not checked.
- **INCONCLUSIVE:** retry once via SendMessage, telling the subagent what blocked it. If it is still inconclusive, report the finding with a `> ⚠️ Confidence note:` stating that the test could not settle it and why.
- **TEST_NOT_FEASIBLE:** the finding was verified from the code by the subagent (`code_verification`). If `confidence` is `high`, report it as a true positive. If `not_high`, report it as a potential true positive with a `> ⚠️ Confidence note:` that carries its `doubt` text, in plain and simple language. Do not re-trace the code yourself.
  - If `needs_dynamic.required` is true, do NOT run anything on a live instance and do not start any server: dynamic verification is not done in this review. Report it as a potential true positive with the confidence note, and include in the note what would have to be checked, as which role, and that the instance would have to be running this PR's code.

Do not proceed to Step 5 until every MEDIUM+ finding has been through this step.

## Step 5 — Present results

Present only the verified MEDIUM+ findings. Do not include LOW findings, false positives, findings discarded in Step 4, or the critical reviewer's one-line `DISCARDED` entries: none of them are reviewed, so writing them out is wasted output. Do not add any wrapper text or summary beyond what the critical reviewer produced for the MEDIUM+ findings, the confidence notes from Step 4, and, under each MEDIUM+ finding confirmed by test, a compact evidence block:

- Red test: file, test name, runner command, and the relevant failing assertion
- Green test: file, test name, and that it passes
- Attacker role used in the test

The evidence block is for internal use only. The PR comment for GitHub stays exactly as the critical reviewer wrote it and never mentions tests.

## Step 6 — Leave the worktree in place

Do not remove the worktree or the per-PR ref: the same session may be asked later to fix a finding, and it needs the tests left in the tree. Never commit, stage or push anything.
