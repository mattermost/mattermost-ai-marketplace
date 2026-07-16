# Mattermost AI Marketplace

A collection of Claude Code plugins for Mattermost development.

## Installation

Add the marketplace:

```
/plugin marketplace add mattermost/mattermost-ai-marketplace
```

Then install individual plugins:

```
/plugin install mattermost-ai-marketplace@mattermost-plugin-development
```

## Plugins

| Plugin                          | Description                                          | Skills / Commands              |
| ------------------------------- | ---------------------------------------------------- | ------------------------------ |
| `mattermost-plugin-development` | Tools for developing Mattermost plugins              | `update-from-starter-template` |
| `mattermost-flaky-tests`        | Diagnose and fix flaky Go unit tests in the server   | `server-flaky-test`            |

### mattermost-plugin-development

Provides skills for developing and maintaining Mattermost plugins.

**Skills:**

- **update-from-starter-template** — Syncs a Mattermost plugin repository with common files from [mattermost-plugin-starter-template](https://github.com/mattermost/mattermost-plugin-starter-template) and fixes all linter issues.

  ```
  /update-from-starter-template
  ```

### mattermost-flaky-tests

Provides commands for diagnosing and fixing flaky tests in the Mattermost server.

**Commands:**

- **server-flaky-test** — Takes one flaky Go unit test from the `mattermost/mattermost` server tree and either lands a tests-only fix PR against `master` or, when the root cause can't be determined with high confidence, opens a Jira ticket plus a skip PR.

  ```
  /server-flaky-test
  ```

## Contributing

To add a new plugin to the marketplace:

1. Create a directory under `plugins/` (e.g. `plugins/your-plugin/`)
2. Add a `.claude-plugin/plugin.json` manifest inside it
3. Add skills under `plugins/your-plugin/skills/`
4. Register the plugin in `.claude-plugin/marketplace.json` by adding an entry to the `plugins` array
