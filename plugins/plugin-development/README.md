# mattermost-plugin-development

Claude Code plugins for developing Mattermost plugins.

## Skills

### update-from-starter-template

Syncs a Mattermost plugin repository with common files from [mattermost-plugin-starter-template](https://github.com/mattermost/mattermost-plugin-starter-template) and fixes all linter issues.

```
/mattermost-plugin-development:update-from-starter-template
```

This skill will:

1. Prepare the repository by creating a new branch
2. Update common build and config files from the starter template while preserving plugin-specific customizations
3. Fix linter issues using `gofumpt` and manual fixes
4. Verify tests pass and create a commit with PR
