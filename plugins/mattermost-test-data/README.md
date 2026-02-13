# mattermost-test-data

Backfill realistic test data into a Mattermost server using MCP tools. Creates users, teams, channels, and natural multi-user conversations for demo or testing environments.

## Skills

| Skill | Description |
|-------|-------------|
| `mattermost-test-data` | Populate a Mattermost instance with realistic test data and interact via MCP tools |

## Usage

```
/mattermost-test-data:mattermost-test-data
```

### Prerequisites

Requires a connected Mattermost MCP server with write access (create users, teams, channels, posts).

### What It Does

Follows a structured workflow to seed a Mattermost server:

1. **Gather requirements** — asks about theme, scale, conversation topics, and tone
2. **Create team** — sets up the workspace
3. **Create users** — realistic profiles with distinct personas and communication styles
4. **Create channels** — general, random, and topic-specific channels with purpose/header
5. **Seed conversations** — multi-user threaded discussions using `create_post_as_user` for authentic message attribution

### Conversation Quality

- Persona-consistent voices (leads coordinate, seniors advise, juniors ask questions)
- Natural thread patterns (problem-solving, coordination, knowledge-sharing, casual)
- Realistic artifacts (code blocks, tool references, deployment commands)
- Imperfections (typos, self-corrections, "nvm found it" messages)

### MCP Tool Reference

Also serves as a reference for reading, searching, and interacting with Mattermost data via the available MCP tools.

## Author

Nick Misasi
