# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Mattermost AI Marketplace**, a collection of Claude Code plugins for Mattermost development. It is distributed via the Claude Code plugin marketplace under `mattermost/mattermost-ai-marketplace`.

## Repository Structure

- `.claude-plugin/marketplace.json` — Marketplace manifest (lists all plugins, versions, metadata)
- `plugins/` — Each subdirectory is a plugin
  - `plugins/<name>/.claude-plugin/plugin.json` — Plugin manifest
  - `plugins/<name>/skills/<skill-name>/SKILL.md` — Skill definitions

## How Plugins Work

Plugins are defined by a `plugin.json` manifest and one or more skills. Skills are Markdown files with YAML frontmatter that declares the skill name, description, whether it's user-invocable, and which tools it's allowed to use. The Markdown body contains instructions that Claude follows when the skill is invoked.

## Adding a New Plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` with the plugin manifest
2. Add skills under `plugins/<name>/skills/<skill-name>/SKILL.md`
3. Register the plugin in `.claude-plugin/marketplace.json` by adding an entry to the `plugins` array
4. Update `README.md` to list the new plugin and its skills

## Releasing a New Version

When releasing, update the `version` field in:
- `.claude-plugin/marketplace.json` (both `metadata.version` and each plugin's `version`)
- Individual plugin manifests if their content changed
