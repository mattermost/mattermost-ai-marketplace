#!/usr/bin/env python3
"""PreToolUse guard for specs/*/spec-state.json.

Blocks any tool call that would write to a spec-state.json file directly,
regardless of which tool is used (Edit, Write, or Bash). There is exactly
one sanctioned writer: the bundled spec-state CLI
(${CLAUDE_PLUGIN_ROOT}/scripts/spec-state), including its `bootstrap`
subcommand for first-time file creation. The CLI takes only a validated
kebab-case slug — it never accepts a raw spec-state.json path as an
argument — so a legitimate Bash invocation of it never needs to mention
the literal path at all.

Two things a naive version of this guard gets wrong (fixed here):
  1. Edit/Write: matching the raw `file_path` string against a pattern is
     defeated by a non-canonical path that still resolves to the protected
     file (e.g. `specs/demo/../demo/spec-state.json`). We resolve the path
     against the tool call's `cwd` and normalize it before matching.
  2. Bash: a regex over raw shell text cannot safely allowlist "this cp
     command is the sanctioned bootstrap" — command substitution
     (`$(...)`), backticks, and chaining can smuggle an arbitrary write
     past any such pattern. There is no safe allowlist for this, so Bash
     is denied unconditionally whenever the command references the
     protected path pattern anywhere in its text. The bootstrap CLI
     subcommand above is the only sanctioned creation path precisely
     because it removes the need for Bash to ever reference the raw path.

Reads the PreToolUse JSON payload from stdin and decides allow/deny in code,
rather than relying on the hook `if` filter (only honoured in Claude Code
v2.1.85+) or a tool-specific matcher (which would miss Bash entirely).
"""
import json
import os
import re
import sys

# Matches the protected path once it has been normalized (Edit/Write) or
# anywhere in raw command text (Bash, where normalization isn't meaningful).
STATE_FILE_RE = re.compile(r"specs/[^/\s]+/spec-state\.json")


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
    cwd = payload.get("cwd") or os.getcwd()

    if tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path", "") or ""
        # Resolve against cwd and collapse '..'/'.' before matching, so a
        # non-canonical path can't dodge the pattern while still resolving
        # to the protected file on disk.
        absolute = file_path if os.path.isabs(file_path) else os.path.join(cwd, file_path)
        canonical = os.path.normpath(absolute).replace(os.sep, "/")
        if STATE_FILE_RE.search(canonical):
            verb = "edits" if tool_name == "Edit" else "writes"
            deny(
                "spec-state.json is orchestrator-managed; direct %s are blocked. "
                "Use the bundled spec-state CLI "
                "(${CLAUDE_PLUGIN_ROOT}/scripts/spec-state)." % verb
            )

    elif tool_name == "Bash":
        command = tool_input.get("command", "") or ""
        if STATE_FILE_RE.search(command):
            deny(
                "spec-state.json is orchestrator-managed; direct shell writes are "
                "blocked, with no exceptions from this guard (a regex over shell "
                "text cannot safely allowlist a specific command). Use the bundled "
                "spec-state CLI (${CLAUDE_PLUGIN_ROOT}/scripts/spec-state) — "
                "`bootstrap <slug>` for first-time creation, everything else via "
                "apply-delta/log-event/set-gate. Neither takes a raw file path."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
