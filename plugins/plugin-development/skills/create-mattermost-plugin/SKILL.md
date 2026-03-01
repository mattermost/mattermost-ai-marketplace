---
name: create-mattermost-plugin
description: Create a new Mattermost plugin from the starter template in the current directory. Use when creating a new plugin from scratch, scaffolding a Mattermost plugin, or bootstrapping a plugin project.
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Create Mattermost Plugin

Scaffold a new Mattermost plugin by cloning the [starter template](https://github.com/mattermost/mattermost-plugin-starter-template) into the current directory and customizing it.

The **plugin name** is the current folder name (e.g. if pwd is `/home/user/mattermost-plugin-foo`, the plugin name is `mattermost-plugin-foo`).
The **Go module path** is `github.com/mattermost/<plugin-name>`.

## Step 1: Pre-flight

Check if pwd has files beyond dotfiles. If non-empty, warn the user with `AskUserQuestion` and let them choose to proceed or abort.

## Step 2: Clone template into pwd

```bash
TMPDIR=$(mktemp -d)
git clone --depth 1 https://github.com/mattermost/mattermost-plugin-starter-template "$TMPDIR"
rm -rf "$TMPDIR/.git"
cp -a "$TMPDIR"/. ./
rm -rf "$TMPDIR"
```

## Step 3: Customize (follow README "Getting Started" steps)

Derive values:

- `PLUGIN_NAME` = basename of pwd (e.g. `mattermost-plugin-foo`)
- `MODULE_PATH` = `github.com/mattermost/$PLUGIN_NAME`
- `PLUGIN_ID` = `com.mattermost.$PLUGIN_NAME` (dots replaced for the id portion after `com.mattermost.`)

1. **Edit `plugin.json`**: set `id`, `name`, `description` (use the plugin name as a sensible default for name/description, the user can refine later). Update `homepage_url` and `support_url` to point to `https://$MODULE_PATH` and `https://$MODULE_PATH/issues`.

2. **Replace the old module path everywhere**: Use `Grep` to find all files containing `github.com/mattermost/mattermost-plugin-starter-template`, then `Edit` each with `replace_all` to substitute the new `MODULE_PATH`.

## Step 4: Git init & first commit

1. Run `git init` if `.git` doesn't exist
2. `git add -A && git commit -m "Initial plugin scaffold from mattermost-plugin-starter-template"`

## Step 5: Summary

Print what was created and remind the user to run `make` to build.
