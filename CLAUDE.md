# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace — a catalog of staff-contributed plugins (skills, agents, hooks) that Mattermost engineers install into their own projects. There is no application code, build system, or test suite. The repo is purely declarative: JSON manifests + Markdown skill definitions.

## Validation

```bash
claude plugin validate .
```

This is the only "build/test" command. Run it after any structural change.

## Architecture

```
.claude-plugin/marketplace.json    # Central catalog — lists every plugin
plugins/<name>/                    # One directory per plugin
  .claude-plugin/plugin.json       # Plugin manifest (name, version, author, keywords)
  skills/<skill-name>/SKILL.md     # Skill prompt with YAML frontmatter (model-invoked capability)
  commands/<command-name>.md       # Optional: slash command prompt (explicitly invoked)
  README.md                        # Plugin-level docs
templates/                         # Starter templates for new plugins/skills
```

**marketplace.json** has `"pluginRoot": "./plugins"`, so each plugin's `"source"` field is just its directory name (e.g., `"source": "code-simplifier"` resolves to `./plugins/code-simplifier`).

## Adding a New Plugin

Every change follows the same pattern — there is no variation:

1. Create `plugins/<name>/.claude-plugin/plugin.json`
2. Create `plugins/<name>/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`)
3. Create `plugins/<name>/README.md`
4. Append an entry to `.claude-plugin/marketplace.json` `plugins` array
5. Append a row to the "Available Plugins" table in `README.md`

Use `templates/plugin/` as a starting point. Plugin and skill names use kebab-case.

## Conventions

- **SKILL.md frontmatter**: Must include `name` and `description`. Use `disable-model-invocation: true` for skills with side effects. Use `allowed-tools` to restrict tool access for read-only skills.
- **plugin.json fields**: `name`, `description`, `version` (semver), `author.name`, `keywords` (array).
- **marketplace.json entry fields**: `name`, `source`, `description`, `version`, `category`, `tags`, `author.name`.
- **Categories**: `code-quality`, `conventions`, `testing`, `devops`, `git`, `docs`, `security`, `productivity`.
- **Skill invocation pattern**: `/plugin-name:skill-name` (skills are namespaced by plugin).
- **Commands**: optional `commands/<command-name>.md` files are explicitly-invoked slash commands, namespaced `/plugin-name:command-name`. Prefer a command over a skill for side-effecting, orchestrated procedures; a command can delegate to the plugin's own skills. `plugins/mattermost-cherry-pick/` ships both a command and skills.
- **Keep SKILL.md under 500 lines** — move reference material to separate files loaded on demand.
- **`${CLAUDE_PLUGIN_ROOT}`** — use this env var in hooks/scripts to reference files within the plugin (plugins are copied to a cache on install).
