# Mattermost AI Marketplace

Staff-contributed Claude Code plugins for Mattermost engineering workflows. Browse, install, and share skills, agents, hooks, and more.

## Quick Start

```bash
# Add this marketplace
/plugin marketplace add mattermost/mattermost-ai-marketplace

# Browse available plugins
/plugin

# Install a plugin
/plugin install <plugin-name>@mattermost-ai-marketplace

# Update the marketplace catalog
/plugin marketplace update mattermost-ai-marketplace
```

## Available Plugins

| Plugin | Description | Category | Version |
|--------|-------------|----------|---------|
| [`code-simplifier`](plugins/code-simplifier/) | Simplifies and refines code for clarity, consistency, and maintainability | code-quality | 1.0.0 |
| [`conflicts`](plugins/conflicts/) | Git merge conflict resolution agent that analyzes intent behind changes | git | 1.0.0 |
| [`figma-implement-design`](plugins/figma-implement-design/) | Translate Figma designs into production-ready code with 1:1 visual fidelity | design | 1.0.0 |
| [`precommit`](plugins/precommit/) | Discover, run, and resolve all pre-commit code quality checks in a monorepo | code-quality | 1.0.0 |
| [`test-evaluator`](plugins/test-evaluator/) | Review tests for efficacy, correctness, and coverage gaps | testing | 1.0.0 |
| [`teamimplement`](plugins/teamimplement/) | Orchestrate phased implementation with dedicated research, planning, implementation, review, and QA engineers | productivity | 1.0.0 |
| [`issue-resolver`](plugins/issue-resolver/) | Autonomous issue resolution agent using sub-agents and browser-based validation | productivity | 1.0.0 |
| [`mattermost-test-data`](plugins/mattermost-test-data/) | Backfill realistic test data into a Mattermost server using MCP tools | devops | 1.0.0 |
| [`claude-md-improver`](plugins/claude-md-improver/) | Audit and improve CLAUDE.md files — scans, scores quality, and makes targeted updates | productivity | 1.0.0 |
| [`mattermost-plugin-development`](plugins/plugin-development/) | Update Mattermost plugin repos from the starter template and fix linter issues | development | 1.0.0 |

## Auto-Setup for Your Projects

Add to your project's `.claude/settings.json` so teammates are prompted to install automatically:

```json
{
  "extraKnownMarketplaces": {
    "mattermost-ai-marketplace": {
      "source": {
        "source": "github",
        "repo": "mattermost/mattermost-ai-marketplace"
      }
    }
  }
}
```

Optionally enable specific plugins by default:

```json
{
  "enabledPlugins": {
    "plugin-name@mattermost-ai-marketplace": true
  }
}
```

## Repository Structure

```
mattermost-ai-marketplace/
  .claude-plugin/
    marketplace.json          # Marketplace catalog (lists all plugins)
  plugins/
    <plugin-name>/
      .claude-plugin/
        plugin.json           # Plugin manifest
      skills/
        <skill-name>/
          SKILL.md            # Skill definition
      agents/                 # Optional: subagent definitions
      hooks/                  # Optional: lifecycle hooks
      README.md               # Plugin-level docs
  templates/
    plugin/                   # Starter template for new plugins
    skill/                    # Starter template for a single skill
  CONTRIBUTING.md
  LICENSE
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add your own plugins.

## Validating

Maintainers can validate the marketplace from the repo root:

```bash
claude plugin validate .
```
