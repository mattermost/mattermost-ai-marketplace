# cursorctl

Drive Cursor cloud and local agents from Claude Code with the `cursorctl` CLI (Cursor SDK Bridge). Use it to spawn an agent against a GitHub repo, detach and poll later, send follow-ups, and collect run results, conversations, or artifacts.

This plugin is a Claude Code adaptation of the [`cursorctl` skill](https://github.com/nickmisasi/cursor-utils/tree/main/skills/cursorctl) from [nickmisasi/cursor-utils](https://github.com/nickmisasi/cursor-utils).

## Skills

| Skill | Description |
|-------|-------------|
| `cursorctl` | Spawn, send, detach, follow up, inspect, and collect Cursor agents via `cursorctl` |

## Usage

```
/cursorctl:cursorctl
```

Claude also loads the skill when a task calls for Cursor cloud agents (`bc-…` IDs), `--detach` fire-and-forget, `run get`/`wait`/`watch`, or `cursorctl auth`.

## Prerequisites

1. Install `cursorctl` from [GitHub Releases](https://github.com/nickmisasi/cursor-utils/releases) (linux/darwin amd64/arm64) or `go install github.com/nickmisasi/cursor-utils/cursorctl@latest`. A common local path is `~/.local/bin/cursorctl`.
2. Store a Cursor user API key from https://cursor.com/dashboard/api:

   ```bash
   cursorctl auth add work --stdin --default
   ```

   Do not `export CURSOR_API_KEY` in shell rc files; Cursor's `agent` CLI treats that variable as higher-priority than stored login.

3. Confirm the binary:

   ```bash
   command -v cursorctl
   cursorctl version
   ```

The first bridge-backed command downloads the pinned SDK Bridge, verifies SHA-256, and caches it under `~/.cache/cursorctl/sdk-bridge/`. Pre-fetch with `cursorctl bridge install`.

## Author

Nick Misasi
