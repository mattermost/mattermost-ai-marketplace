# Cloud delegation patterns

These recipes assume a stored default profile (`cursorctl auth add work --stdin --default`) or a CI one-off `CURSOR_API_KEY`, and:

```bash
repo="https://github.com/acme/widgets@main"
```

Do not export `CURSOR_API_KEY` in shell rc files; it shadows Cursor’s `agent` CLI login. See [troubleshooting](troubleshooting.md).

Cloud agent IDs begin with `bc-`. Keep agent IDs and run IDs separate.

## Spawn a cloud agent and let it open a PR

Goal: delegate one task, wait for completion, and receive one parseable result.

```bash
cursorctl agent prompt \
  --repo "$repo" \
  --auto-create-pr \
  --skip-reviewer-request \
  --quiet \
  "Implement issue 123, run the relevant tests, and open a PR." \
  > result.json

status="$(jq -r '.status' result.json)"
summary="$(jq -r '.result' result.json)"
pr_url="$(jq -r '.git.branches[]? | select(.prUrl != "") | .prUrl' result.json)"
```

`--quiet` makes the output one JSON `RunResult`, so normal `jq` expressions work. Without it, consume NDJSON as shown below.

## Detach, poll, and resume event observation

Goal: launch work without holding the caller open, then inspect or wait later.

```bash
agent_id="$(
  cursorctl agent create \
    --repo "$repo" \
    --auto-create-pr \
    --skip-reviewer-request |
  jq -r '.agentId'
)"

cursorctl agent send "$agent_id" --detach \
  "Implement issue 123, verify it, and update the PR." \
  > detached.json

run_id="$(jq -r '.runId' detached.json)"
```

Detaching returns after the stream reports the run ID:

```json
{
  "agentId": "bc-...",
  "runId": "..."
}
```

The run continues server-side. Choose one observation method:

```bash
# Non-blocking snapshot.
cursorctl run get "$run_id" --runtime cloud --agent-id "$agent_id"

# Block for the terminal RunResult.
cursorctl run wait "$run_id" > result.json

# Stream durable events as NDJSON.
cursorctl run watch "$run_id" | tee run-events.ndjson
```

If a `run watch` connection ends and emitted offsets, resume exclusively after its last offset:

```bash
last_offset="$(
  jq -r 'select(.offset != null) | .offset' run-events.ndjson |
  tail -n 1
)"
cursorctl run watch "$run_id" --after-offset "$last_offset"
```

Only reuse offsets from `run watch`/`ObserveRun`. Initial `agent send` offsets are not valid resume tokens for `run watch`.

NDJSON is `jq`-friendly because each line is a complete object:

```bash
jq -r 'select(.event == "sdkMessage" and .type == "assistant") | .message' \
  run-events.ndjson
jq -r 'select(.event == "result") | .result.result' run-events.ndjson
```

## Keep a durable agent and send follow-ups

Goal: preserve conversation context across multiple delegated turns.

```bash
agent_id="$(
  cursorctl agent create \
    --name "issue-123" \
    --repo "$repo" \
    --auto-create-pr |
  jq -r '.agentId'
)"

cursorctl agent send "$agent_id" --quiet \
  "Implement issue 123 and run focused tests." > first-run.json

cursorctl agent send "$agent_id" --quiet \
  "Review your changes, add missing regression coverage, and update the PR." \
  > follow-up.json
```

Parse `.runId`, `.status`, `.result`, and `.git.branches[].prUrl` from each quiet result. For live output, omit `--quiet` and select the NDJSON `result` event.

For an agent created in an earlier process, send directly to its `bc-...` ID. Each CLI invocation starts a new bridge, so `agent send` calls `ResumeAgent` in that process before `Send`:

```bash
cursorctl agent get "$agent_id"
cursorctl agent send "$agent_id" --quiet "Address the remaining review comments."
```

`agent resume` is still available when you need to pass extra create/resume flags (model, MCP, local cwd). Ordinary cloud follow-up only needs `agent send bc-...`.

## Collect conversations and artifacts

Goal: retrieve the agent's transcript-derived conversation and generated files.

```bash
cursorctl run conversation "$run_id" > conversation.json

cursorctl artifact list "$agent_id" > artifacts.json
jq -r '.artifacts[] | [.path, .sizeBytes, .updatedAt] | @tsv' artifacts.json

cursorctl artifact download "$agent_id" "reports/test-results.json" \
  --file test-results.json
```

`run conversation` decodes the bridge's `conversationJson` string before printing it. `artifact download --file PATH` prints a `{path,bytes}` summary after writing; without `--file`, stdout is raw bytes, so do not pipe that mode through `jq`.

## List and triage the agent fleet

Goal: find active or archived cloud delegates and inspect token/cost usage.

```bash
cursorctl agent list --runtime cloud --limit 50 > agents.json
jq -r '.items[] | [.agentId, .status, .name, .summary] | @tsv' agents.json

next_cursor="$(jq -r '.nextCursor // empty' agents.json)"
if [ -n "$next_cursor" ]; then
  cursorctl agent list --runtime cloud --limit 50 --cursor "$next_cursor"
fi

cursorctl run list "$agent_id" --runtime cloud --limit 20
cursorctl agent usage "$agent_id"
cursorctl agent usage "$agent_id" --run-id "$run_id"
```

Use `--pr-url URL` on `agent list` to find an agent associated with one PR. Add `--include-archived` when triaging historical agents.

## Cancel and clean up

Goal: stop a run, then archive or permanently remove its agent.

```bash
cursorctl run cancel "$run_id" --agent-id "$agent_id"
cursorctl run get "$run_id" --runtime cloud --agent-id "$agent_id"

cursorctl agent archive "$agent_id"
```

Archive is reversible:

```bash
cursorctl agent unarchive "$agent_id"
```

Deletion is irreversible and requires explicit confirmation:

```bash
cursorctl agent delete "$agent_id" --force
```

Closing a client stream, including `--detach`, is not cancellation. A successful cancel RPC means the request was accepted; inspect the run afterward for its terminal status.
