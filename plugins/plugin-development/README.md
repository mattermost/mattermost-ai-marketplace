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

### add-agents-mcp-server

Adds a cross-plugin MCP (Model Context Protocol) server to a Mattermost plugin so the [Mattermost Agents plugin](https://github.com/mattermost/mattermost-plugin-agents) can discover and call its tools. Uses the `pluginmcp` helper from `mattermost-plugin-agents/external/pluginmcp`.

```
/mattermost-plugin-development:add-agents-mcp-server
```

This skill will:

1. Add the `mattermost-plugin-agents` and `modelcontextprotocol/go-sdk` Go dependencies
2. Add a thread-safe MCP server holder to the `Plugin` struct
3. Scaffold `server/mcp.go` (lifecycle helpers) and `server/mcp_tools.go` (typed tool handlers)
4. Wire the server into `OnActivate` / `OnDeactivate` and route MCP requests in `ServeHTTP`
5. Provide a smoke-test template, gotchas (tool-name namespacing, user-ID propagation, registration retries, tool-budget guidance), and troubleshooting
