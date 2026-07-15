# mattermost-cherry-pick

Cherry-picks a merged security PR from `mattermost/mattermost` master onto every release branch the Mattermost release policy requires, opening one cherry-pick PR per branch. Designed to be driven by a Cursor Automation that fires when a PR is merged, but the command and skills can also be run by hand.

## Command

| Command | Description |
|---------|-------------|
| `cherry-pick-security-pr-merged` | Orchestrates the full flow: identify the merged PR, gate on a `security`-labeled Jira ticket, resolve target release branches, then cherry-pick and open a PR per branch |

## Skills

| Skill | Description |
|-------|-------------|
| `security-release-targets` | Given a priority/severity level, resolves the target `release-X.Y` branches by parsing the Mattermost release policy and filtering to branches that exist on origin. Read-only, no Jira/PR handling — reusable on its own. |
| `cherry-pick-create-pr` | Cherry-picks one commit onto one release branch: correct conflict resolution, lint in a separate commit, push, and open the PR via `create_pr_tool`. Self-contained; side-effecting. |

## Usage

```text
/mattermost-cherry-pick:cherry-pick-security-pr-merged 36316
```

The PR number is optional — when omitted, the command reads the merged PR from the trigger context (as it does when invoked from the Cursor Automation). The command takes no action unless the PR was merged into `master` and fixes a `security`-labeled Jira ticket.

### Workflow

1. **Identify the PR** and require it was merged into `master`.
2. **Gate on Jira** — find the ticket key in the PR body, confirm the `security` label, and read the Priority.
3. **Resolve targets** — hand the priority to `security-release-targets`, which returns the existing `release-X.Y` branches per policy (Critical/High/Medium → active ∪ ESR; Low → upcoming ∪ ESR).
4. **Notify** — post a start message on the PR and to the Mattermost channel.
5. **Fan out** — one subagent per branch, each invoking `cherry-pick-create-pr` to branch, pick, resolve conflicts, lint, push, and open the PR.
6. **Report** — aggregate results back on the PR and in the Mattermost channel.

## Required integrations

- **Custom cherry-pick MCP** providing `create_pr_tool` (opens the PRs) and `post_to_mattermost_cherry_pick` (channel notifications).
- **Atlassian / Jira** integration for the security-label and priority gate.
- **GitHub** (`gh`) for reading the merged PR.

This plugin has no dependency on other marketplace plugins — the cherry-pick skill carries its own conflict-resolution logic.

## Author

Maria Nunez
