# cursor-automations

Internal Cursor automation commands for Mattermost engineering workflows.

> **Internal use only.** The commands in this plugin are designed to be invoked by Cursor Automations (webhook/trigger-driven) and depend on a runtime that provides custom MCP tools. They are **not** intended for individual/manual use.

## Commands

| Command | Description |
|---------|-------------|
| `cherry-pick-security-pr-merged` | Orchestrates the full cherry-pick flow: identify the merged PR, gate on a `security`-labeled Jira ticket, resolve target release branches, then cherry-pick and open a PR per branch |
| `server-flaky-test` | Diagnose and fix one flaky Go unit test in the Mattermost server: land a tests-only fix PR against `master`, or open a Jira ticket plus a skip PR when the root cause cannot be determined with high confidence |

## Skills

| Skill | Description |
|-------|-------------|
| `security-release-targets` | Given a priority/severity level, resolves the target `release-X.Y` branches by parsing the Mattermost release policy and filtering to branches that exist on origin. Read-only, no Jira/PR handling — reusable on its own. |
| `cherry-pick-create-pr` | Cherry-picks one commit onto one release branch: correct conflict resolution, lint in a separate commit, push, and open the PR via `create_pr_tool`. Self-contained; side-effecting. |

## Required integrations

- **Custom automation MCP** providing tools such as `create_pr_tool`, `post_to_mattermost_cherry_pick`, `post_to_mattermost_flaky_result`, `add_pr_comment`, `add_labels_to_PRs`, `request_reviewer`, and `request_group_reviewer`.
- **Atlassian / Jira** integration for security-label / priority gating and flaky-test ticket creation.
- **GitHub** (`gh`) for reading PRs and, for the flaky-test command, opening PRs.

## Author

Maria Nunez
