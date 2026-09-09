# Output, streams, JSON payloads, and exit codes

## Final and unary output

`-o, --output` accepts:

| Format | Behavior | Use when |
| --- | --- | --- |
| `json` | Pretty-printed JSON; default. | Shell parsing with `jq`, logs, interchange. |
| `yaml` | Two-space YAML. | Human review or YAML-native tooling. |
| `toon` | Deterministic, compact token-oriented object/array notation. | Feeding large, repetitive catalog/list results to an LLM where TOON's tabular arrays reduce tokens. |

The format name is case-insensitive. See [toon-format.md](https://github.com/nickmisasi/cursor-utils/blob/main/docs/toon-format.md) for TOON syntax.

`-o` applies to unary responses, quiet terminal results, detach summaries, and file-download summaries. It does not transform:

- live run event streams (always NDJSON);
- artifact bytes written to stdout;
- generated shell completion scripts.

## NDJSON run streams

`agent send`, `agent prompt`, and `run watch` normally emit one compact JSON object per line. Each bridge envelope is flattened into:

```json
{"event":"sdkMessage","type":"assistant","message":{"text":"hello"},"offset":"opaque-1"}
{"event":"result","agentId":"bc-...","runId":"run-...","status":"FINISHED","result":{"runId":"run-...","agentId":"bc-...","status":"FINISHED","result":"done"},"offset":"opaque-2"}
{"event":"done","agentId":"bc-...","runId":"run-..."}
```

Envelope kinds:

| `event` | Payload |
| --- | --- |
| `sdkMessage` | SDK message fields. Known `type` values are `system`, `assistant`, `user`, `tool_call`, `thinking`, `status`, `task`, `usage`, and `request`. |
| `result` | Stream result metadata plus nested terminal `RunResult` in `result`. |
| `done` | End marker with agent/run identity. |
| `interactionUpdate` | Interaction deltas, requested with `--deltas`. |
| `step` | Completed conversation steps, requested with `--steps`. |

If the bridge supplies an `offset`, cursorctl copies it to the line. Empty keepalive envelopes are ignored. Normal order is `result`, then `done`, then the Connect EndStream frame.

Use line-oriented `jq` directly:

```bash
cursorctl run watch "$run_id" |
  jq -c 'select(.event == "sdkMessage" and .type == "assistant")'
```

`--quiet` suppresses every event and prints only the nested terminal `RunResult` using `-o`. `--detach` reads until it can identify the run, prints `{agentId,runId}` using `-o`, closes the stream, and exits without cancelling the run. `--quiet` and `--detach` conflict.

Offsets are opaque exclusive resume tokens. `run watch --after-offset` must receive an offset from an earlier `run watch` (`ObserveRun`) stream; do not use offsets emitted by the initial `agent send` stream.

## Raw `--json` request mode

Every RPC-backed leaf exposes `--json` as an alternative to positional and per-field request construction. Accepted sources:

```bash
# Literal object.
cursorctl run get --json '{"runId":"run-...","options":{"runtime":"RUNTIME_CLOUD"}}'

# File contents.
cursorctl agent create --json @create-agent.json

# Stdin.
generate_request | cursorctl agent send --json -
```

The input must be exactly one JSON object. Arrays, `null`, malformed JSON, and multiple JSON values are rejected.

Rules:

1. Use proto3 JSON lowerCamelCase names: `agentId`, `runId`, `afterOffset`, `autoCreatePr`, and so on.
2. `--json` is the whole request. It conflicts with every positional argument.
3. Per-field local flags conflict by default. Explicit non-payload exceptions are:
   - `--quiet` and `--detach` on send/prompt;
   - `--quiet` on run watch;
   - `--file` on artifact download;
   - `--force` on agent delete;
   - custom-tool executor/declaration flags on create/send/prompt.
4. Global flags such as `-o`, `--api-key`, `--profile`, `--timeout`, and bridge selection remain valid.
5. Cursorctl resolves the API key even in raw mode for auth-backed RPCs. Where the request needs `options.apiKey`, it creates `options` if absent and injects the key unless `apiKey` already exists. Bridge control RPCs need no key.
6. Apart from API-key injection and requested custom-tool declaration injection, raw payloads are forwarded as supplied; the bridge performs protobuf validation.

For create/resume and option-bearing management calls:

```json
{
  "options": {
    "apiKey": "injected unless already present",
    "cloud": {"repos": [{"url": "https://github.com/acme/widgets"}]}
  }
}
```

Catalog RPCs (`me`, `models`, `repos`) always need `options.apiKey`; bridge environment fallback is not sufficient for those RPCs.

`agent prompt --json` is the one composite payload rather than one wire request:

```json
{
  "options": {"cloud": {"repos": [{"url": "https://github.com/acme/widgets"}]}},
  "message": {"text": "Implement issue 123."},
  "sendOptions": {"enableSteps": true},
  "idempotencyKey": "issue-123"
}
```

Cursorctl turns it into CreateAgent, Send, and CloseAgent operations and injects the key into `options`.

Bridge control RPCs accept `bridge ping --json <object>` and `bridge version --json <object>`; their normal request is `{}`. Non-RPC commands (`bridge install`, `version`, hidden completion generation, and help) do not expose `--json`.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Command/RPC succeeded. For send/prompt/watch/wait, the evaluated terminal run status is `FINISHED`. A successful `--detach` also exits `0` before terminal status is known. |
| `1` | CLI validation, missing key, bridge install/start, transport, RPC, malformed/truncated stream, output, or other operational failure. |
| `2` | A run-returning command evaluated a terminal result with status `ERROR`, `CANCELLED`, or `EXPIRED`. |

Do not treat every non-finished snapshot as exit `2`: inspection commands such as `run get` only report an RPC snapshot and exit `0` when that RPC succeeds, even if `.run.status` says the run failed. `agent send`, `agent prompt`, `run watch`, and `run wait` evaluate terminal results and return `2` for failed terminal statuses.

Likewise, a stream-level/RPC error is exit `1`, while a successful stream carrying a failed `RunResult` is exit `2`. stderr contains the CLI error line; stdout may already contain useful NDJSON events or a printed terminal result.
