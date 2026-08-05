#!/usr/bin/env python3
"""PreToolUse guard for specs/*/spec-state.json.

Blocks any tool call that would write to a spec-state.json file directly,
regardless of which tool is used (Edit, Write, or Bash). There are exactly
two sanctioned writers:
  1. The bundled spec-state CLI (${CLAUDE_PLUGIN_ROOT}/scripts/spec-state),
     which never takes a raw spec-state.json path as an argument.
  2. The one-time bootstrap `cp` of the template into a fresh spec folder
     (documented in spec-orchestrator.md / spec-init.md / spec-clean.md as
     "the one sanctioned file-creation step").

Reads the PreToolUse JSON payload from stdin and decides allow/deny in code,
rather than relying on the hook `if` filter (only honoured in Claude Code
v2.1.85+) or a tool-specific matcher (which would miss Bash entirely).

Bash commands are split on shell chaining metacharacters (&&, ||, ;, |,
newline) before matching, so a legitimate-looking prefix can't smuggle a
chained write past the guard.
"""
import json
import re
import sys

STATE_FILE_RE = re.compile(r"specs/[^/\s]+/spec-state\.json")
CHAIN_SPLIT_RE = re.compile(r"&&|\|\||[;|\n]")
BOOTSTRAP_CP_RE = re.compile(
    r"^\s*cp\s+.*templates/spec-state-object\.json\s+.*specs/[^/\s]+/spec-state\.json\s*$"
)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path", "") or ""
        if STATE_FILE_RE.search(file_path):
            verb = "edits" if tool_name == "Edit" else "writes"
            deny(
                "spec-state.json is orchestrator-managed; direct %s are blocked. "
                "Use the bundled spec-state CLI "
                "(${CLAUDE_PLUGIN_ROOT}/scripts/spec-state)." % verb
            )

    elif tool_name == "Bash":
        command = tool_input.get("command", "") or ""
        for sub_command in CHAIN_SPLIT_RE.split(command):
            if not STATE_FILE_RE.search(sub_command):
                continue
            if BOOTSTRAP_CP_RE.match(sub_command):
                continue
            deny(
                "spec-state.json is orchestrator-managed; direct shell writes are "
                "blocked. Use the bundled spec-state CLI "
                "(${CLAUDE_PLUGIN_ROOT}/scripts/spec-state), or the documented "
                "template `cp` for first-time bootstrap only."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
