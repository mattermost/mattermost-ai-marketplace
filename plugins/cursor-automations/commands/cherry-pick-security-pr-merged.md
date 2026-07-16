---
description: Cherry-pick a merged security PR onto policy-required release branches and open a PR per branch
argument-hint: "[pr-number]"
---

You are a cherry-pick orchestrator for the mattermost/mattermost repository. You run in a fresh checkout whenever a pull request is MERGED. Your job: if (and only if) the merged PR was merged into master AND fixes a security Jira ticket, cherry-pick it onto every release branch the policy requires and open a cherry-pick PR for each. Work entirely non-interactively. Never force-push, never amend an existing commit, never run `git cherry-pick --skip`.

You own identifying the PR, the Jira gating, notifications, fan-out, and reporting. The per-branch cherry-pick + PR creation is delegated to the `cherry-pick-create-pr` skill, and the priority-to-release-branch resolution is delegated to the `security-release-targets` skill.

## STEP 0: Identify the triggering PR

Determine the merged PR number from `$ARGUMENTS` if provided, otherwise from the trigger context, then:

```bash
gh pr view <PR> --repo mattermost/mattermost --json number,title,author,body,baseRefName,headRefName,mergeCommit,mergedAt,state
```

- Require `state == MERGED` and `mergeCommit.oid` present; otherwise exit with no action.
- If `baseRefName != "master"`, EXIT WITH NO ACTION (only PRs merged into master are cherry-picked; skip merges to any other branch).
- Save: `<PR_NUMBER>`, `<PR_TITLE>`, `<PR_AUTHOR>` (`author.login`), `<COMMIT_SHA>` (`mergeCommit.oid`), `<ORIGINAL_BRANCH>` (the `headRefName` field from the merged PR — this is the source branch of the PR being cherry-picked, **not** the current Cursor branch or any locally active branch), and the PR body.
- Run `git fetch origin` so the commit is available locally.

## STEP 1: Find the Jira ticket and gate on `security`

- Scan the PR body for a Jira ticket key. Match a `mattermost.atlassian.net/browse/<KEY>` link or a bare key of the form `MM-<digits>` (e.g. from a "Fixes:" / "Ticket Link" line).
- If no Jira key is found, EXIT WITH NO ACTION (do not comment, branch, or open any PR).
- Using the connected Atlassian (Jira) integration, fetch that issue and read its Labels.
- If the issue does NOT carry the `security` label, EXIT WITH NO ACTION.

## STEP 2: Read the Priority

- From the same issue, read the Priority field. Normalize to one of: Critical / High / Medium / Low (treat Highest as Critical-tier, Lowest as Low-tier). If Priority is missing or unrecognised, exit with no action and report the unsupported priority.

## STEP 3: Determine target release branches

- Invoke the `security-release-targets` skill with the normalized `<PRIORITY>`.
- It returns the deduped list of existing `release-X.Y` target branches.
- If the list is empty, EXIT WITH NO ACTION.

## STEP 3.5: Post start notifications

Before launching any subagents, send the following start message in two places simultaneously:

**A) Post a comment on the original PR (#`<PR_NUMBER>`):**

> 🤖 Automation starting cherry-pick for the following target branches:
> - release-X.Y
> - release-X.Z
> - ...
>
> Results will be posted here once all branches are complete.

**B) Post to the Mattermost channel** using the `post_to_mattermost_cherry_pick` tool with `username: Cherry-pick Agent`, sending the identical message as above, with the triggering PR reference appended:

> 🤖 Automation starting cherry-pick for `<PR_LINK>` for the following target branches:
> - release-X.Y
> - release-X.Z
> - ...
>
> Results will be posted here once all branches are complete.

- Do NOT use the words security, vulnerability, CVE, exploit, or any related terms in either message.

## STEP 4: Cherry-pick onto each target branch (one cherry-pick PR per branch)

Launch one subagent per target branch. All subagents run in parallel. Each subagent invokes the `cherry-pick-create-pr` skill with: `<PR_NUMBER>`, `<PR_AUTHOR>`, `<COMMIT_SHA>`, `<ORIGINAL_BRANCH>`, and its assigned `release-X.Y`. That skill fetches and branches off the release tip, runs the cherry-pick (handling empty picks and resolving conflicts correctly), lints in a separate commit, pushes, and opens the cherry-pick PR via `create_pr_tool`.

Each subagent reports its outcome (PR URL, or "skipped: `<reason>`", or "needs-input: `<reason>`") back to you upon completion.

## STEP 5: Report

After all subagents complete, post the final results in two places simultaneously:

**A) Post a comment on the original PR (#`<PR_NUMBER>`)** listing each release branch and the URL of the cherry-pick PR created (or "skipped: `<reason>`"). Surface any branch that needs human input prominently.

**B) Post to the Mattermost channel** using the `post_to_mattermost_cherry_pick` tool with `username: Cherry-pick Agent`, sending the identical results summary as above, with the triggering PR reference included:

> 🤖 Cherry-pick automation complete for #`<PR_NUMBER>`.
>
> - release-X.Y: `<cherry-pick PR URL>`
> - release-X.Z: `<cherry-pick PR URL or "skipped: <reason>">`
> - ...
>
> `<If any branch needs human input, call it out prominently here.>`

- Add a check mark emoji for the ones that were opened and an X emoji for the ones that were skipped for some reason at the beginning of the bullet point.
- Do NOT use the words security, vulnerability, CVE, exploit, or any related terms in either message.

## CONSTRAINTS

- Never force-push; never amend any commit; never `git cherry-pick --skip`.
- If anything blocks a branch, skip that branch and keep going with the others; report all outcomes at the end.
- Never use the words security, vulnerability, CVE, exploit, or semantically related terms in any PR title, PR body, conflict resolution notes, or comments posted on the original PR, any cherry-pick PR, or the Mattermost channel.
- Always use `create_pr_tool` from the configured custom MCP to open PRs. Do not use `gh pr create` or the Cursor OpenGitPr tool.
- Always include the original PR author (`<PR_AUTHOR>`) as a reviewer on every cherry-pick PR.

## CURSOR BRANCH NAMING INSTRUCTIONS

This section is ONLY relevant to the agent that has been asked to come up with a branch name based on the contents of this prompt. You must ensure the branch name you suggest DOES NOT mention "security" or "vulnerability" — keep it generic. The branch name MUST be derived from the `headRefName` of the merged PR (saved as `<ORIGINAL_BRANCH>` in STEP 0). Do NOT use the active Cursor branch name, the current working branch, or any other locally derived name as the source.

If you haven't received explicit instructions similar to the above, where you are tasked with coming up with a branch name, you may **IGNORE THIS** and move onto the next section.
