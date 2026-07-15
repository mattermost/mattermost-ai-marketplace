# Contributing to the Mattermost AI Marketplace

Thanks for sharing your Claude Code plugins with the team! This guide walks you through adding a new plugin.

## Quick Path

1. Copy the template: `cp -r templates/plugin plugins/my-plugin`
2. Edit the plugin manifest and add your skills/agents/hooks
3. Test locally: `/plugin marketplace add ./` then `/plugin install my-plugin@mattermost-ai-marketplace`
4. Validate: `claude plugin validate .`
5. Open a PR

## Plugin Structure

Every plugin lives under `plugins/<plugin-name>/` and must have:

```
plugins/my-plugin/
  .claude-plugin/
    plugin.json             # Required: plugin manifest
  skills/
    my-skill/
      SKILL.md              # At least one skill recommended
  README.md                 # What your plugin does and how to use it
```

Optional directories:

- `commands/` -- Explicitly-invoked slash commands (`<command-name>.md`), namespaced `/plugin-name:command-name`. Prefer a command over a skill for side-effecting, orchestrated flows; a command can delegate to the plugin's own skills.
- `agents/` -- Subagent markdown files (e.g., `security-reviewer.md`)
- `hooks/` -- Lifecycle hooks (`hooks.json`)
- `scripts/` -- Helper scripts referenced by skills or hooks

## Naming Conventions

- **Plugin names**: kebab-case, descriptive, max 64 chars (e.g., `code-review`, `go-conventions`)
- **Skill names**: kebab-case, match the directory name (e.g., `skills/review/SKILL.md`)
- Skills are namespaced by plugin: a `review` skill in `code-review` plugin becomes `/code-review:review`

## Plugin Manifest (plugin.json)

```json
{
  "name": "my-plugin",
  "description": "Brief description of what this plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  },
  "keywords": ["relevant", "tags"]
}
```

## Writing Good Skills

- Keep `SKILL.md` focused and under 500 lines
- Use `disable-model-invocation: true` for skills with side effects (deploy, commit, send messages)
- Use `allowed-tools` to restrict tools when appropriate (e.g., read-only skills)
- Move detailed reference material to separate files that Claude loads on demand
- Use `${CLAUDE_PLUGIN_ROOT}` in hooks/scripts to reference plugin files (plugins are cached on install)

## Registering Your Plugin

After creating your plugin, add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-plugin",
  "source": "my-plugin",
  "description": "Brief description",
  "version": "1.0.0",
  "category": "your-category",
  "tags": ["tag1", "tag2"],
  "author": {
    "name": "Your Name"
  }
}
```

The `pluginRoot` in marketplace metadata is set to `./plugins`, so source paths are relative to that directory.

### Categories

Use one of these categories (or propose a new one in your PR):

| Category | Description |
|----------|-------------|
| `code-quality` | Linting, formatting, code review |
| `conventions` | Language/framework coding standards |
| `testing` | Test generation, test fixing, coverage |
| `devops` | Deployment, CI/CD, infrastructure |
| `git` | Git workflows, commit helpers, PR automation |
| `docs` | Documentation generation and maintenance |
| `security` | Security scanning and review |
| `productivity` | General developer productivity |

## Testing Your Plugin

1. From the marketplace root, add it locally:
   ```
   /plugin marketplace add ./
   /plugin install my-plugin@mattermost-ai-marketplace
   ```

2. Test each skill:
   ```
   /my-plugin:my-skill
   ```

3. Validate the marketplace:
   ```
   claude plugin validate .
   ```

## Versioning

Follow semver:
- **PATCH** (1.0.x): Bug fixes, wording tweaks
- **MINOR** (1.x.0): New skills or agents added
- **MAJOR** (x.0.0): Breaking changes (renamed skills, changed behavior)

## PR Checklist

- [ ] Plugin is in `plugins/<kebab-case-name>/`
- [ ] `.claude-plugin/plugin.json` exists with required fields
- [ ] At least one skill with a `SKILL.md`
- [ ] Plugin-level `README.md` describing usage
- [ ] Entry added to `.claude-plugin/marketplace.json`
- [ ] `claude plugin validate .` passes
- [ ] Tested locally with `/plugin install`
