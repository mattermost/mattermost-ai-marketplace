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

| Plugin                          | Description                             | Skills                         |
| ------------------------------- | --------------------------------------- | ------------------------------ |
| `mattermost-plugin-development` | Tools for developing Mattermost plugins | `update-from-starter-template` |

### mattermost-plugin-development

Provides skills for developing and maintaining Mattermost plugins.

**Skills:**

- **update-from-starter-template** — Syncs a Mattermost plugin repository with common files from [mattermost-plugin-starter-template](https://github.com/mattermost/mattermost-plugin-starter-template) and fixes all linter issues.

  ```
  /update-from-starter-template
  ```

## Contributing

To add a new plugin to the marketplace:

1. Create a directory under `plugins/` (e.g. `plugins/your-plugin/`)
2. Add a `.claude-plugin/plugin.json` manifest inside it
3. Add skills under `plugins/your-plugin/skills/`
4. Register the plugin in `.claude-plugin/marketplace.json` by adding an entry to the `plugins` array
