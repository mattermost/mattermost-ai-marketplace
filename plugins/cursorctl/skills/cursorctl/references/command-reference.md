# cursorctl command reference

This reference matches the Cobra help and request builders in [cursorctl/internal/cli](https://github.com/nickmisasi/cursor-utils/tree/main/cursorctl/internal/cli). RPC field names use proto3 JSON lowerCamelCase. All commands also accept `-h, --help` (boolean, default `false`).

## Global flags

These flags are inherited by every command:

| Flag | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--api-key` | string | `""` | Cursor API key; sensitive and takes precedence over `--api-key-env` and stored profiles. |
| `--api-key-env` | string | `"CURSOR_API_KEY"` | Name of the environment variable containing the key. |
| `--profile` | string | `""` | Named auth profile. Overrides `CURSORCTL_PROFILE` and the stored default. |
| `--bridge-bin` | string | `""` | SDK Bridge binary path. Takes precedence over `CURSOR_SDK_BRIDGE_BIN`. |
| `--bridge-version` | string | `"v1.0.27"` | SDK Bridge release to install/use. |
| `--local-store` | string | `""` | Bridge local-store JSON (`sqlite`/`jsonl`; custom stores are for embedders). |
| `-o, --output` | string | `"json"` | Final/unary output: `json`, `yaml`, or `toon`. |
| `--timeout` | duration | `0s` | Whole invocation deadline, including downloads; `0` disables it. |
| `-v, --verbose` | bool | `false` | Write SDK Bridge diagnostics to stderr. |
| `--workspace` | string | current directory | Absolute workspace passed to the bridge; also the default local `cwd`. |

Agent, run, artifact, and catalog commands require the API key before their RPC is attempted. Resolution order is `--api-key`, then the env var named by `--api-key-env`, then `--profile`/`CURSORCTL_PROFILE`, then the stored default profile. `bridge ping` and `bridge version` start a per-invocation bridge but need no Cursor API key; `auth *`, `version`, `bridge install`, completion generation, and help make no RPC.

## Root and namespace commands

These commands organize leaves and make no RPC:

| Command | Positional arguments | Local flags | Output |
| --- | --- | --- | --- |
| `cursorctl` | none | none | Prints root help when invoked without a subcommand or with `--help`. |
| `agent` | none | none | Lists agent subcommands with `--help`. |
| `run` | none | none | Lists run subcommands with `--help`. |
| `artifact` | none | none | Lists artifact subcommands with `--help`. |
| `auth` | none | none | Lists auth subcommands with `--help`. |
| `bridge` | none | none | Lists bridge subcommands with `--help`. |
| `completion` | none | none | Hidden from root help; directly invoking it lists completion generators. |
| `help [command]` | zero or more command names | none | Prints help for the selected command. |

They inherit the global flags, although output/bridge/auth flags do not alter help text.

## Shared agent flags

### Creation/resume option set

`agent create`, `agent resume`, and `agent prompt` expose this set:

| Flag | Type | Default | Request mapping |
| --- | --- | --- | --- |
| `--model` | string | `""` | `options.model.id`; required by the SDK for local agents. |
| `--name` | string | `""` | `options.name`. |
| `--agent-id` | string | `""` | `options.agentId` (not the resume positional ID). |
| `--mode` | string | `""` | `options.mode`; accepts `agent` or `plan`. |
| `--cwd` | string | `""` | `options.local.cwd[0]`; if no cloud/local flag is given, uses global `--workspace`. |
| `--dir` | repeatable string | `[]` | `options.local.dirs[]`. |
| `--setting-source` | repeatable string | `[]` | `options.local.settingSources[]`; values: `project`, `user`, `team`, `mdm`, `plugins`, `all`. |
| `--sandbox` | bool | `false` | `options.local.sandboxOptions.enabled`. |
| `--auto-review` | bool | `false` | `options.local.autoReview`. |
| `--repo` | repeatable string | `[]` | `options.cloud.repos[]`; syntax `URL[@ref]`. |
| `--pr-url` | string | `""` | `options.cloud.repos[0].prUrl`; requires exactly one `--repo`. |
| `--env-type` | string | `""` | `options.cloud.env.type`; `cloud`, `pool`, or `machine`. |
| `--env-name` | string | `""` | `options.cloud.env.name`. |
| `--auto-create-pr` | bool | `false` | `options.cloud.autoCreatePr`. |
| `--skip-reviewer-request` | bool | `false` | `options.cloud.skipReviewerRequest`. |
| `--work-on-current-branch` | bool | `false` | `options.cloud.workOnCurrentBranch`. |
| `--env-var` | repeatable string | `[]` | `options.cloud.envVars`, each `KEY=VAL`. |
| `--metadata` | repeatable string | `[]` | `options.cloud.metadata`, each `KEY=VAL`. |
| `--open-as-github-app` | bool | `false` | `options.cloud.openAsCursorGithubApp`. |
| `--mcp-config` | string | `""` | `options.mcpServers`; JSON object, `@file`, or `-`. |
| `--agents-config` | string | `""` | `options.agents`; JSON object, `@file`, or `-`. |
| `--tool` | repeatable string | `[]` | `options.tools.names[]` built-in allowlist (local runtime). |
| `--disallowed-tool` | repeatable string | `[]` | `options.disallowedTools[]`. |

Local-option flags and cloud-option flags cannot be combined. Any cloud-option flag selects cloud options; otherwise cursorctl constructs local options.

`agent create` and `agent prompt` additionally expose `--idempotency-key`; `agent resume` does not because `ResumeAgent` has no idempotency field.

### Send option set

`agent send` exposes all of these. `agent prompt` exposes the execution flags; its `--model`, `--mode`, and `--mcp-config` come from the creation set and are also forwarded to Send. Its separate creation `--idempotency-key` is forwarded to both CreateAgent and Send.

| Flag | Type | Default | Request/CLI behavior |
| --- | --- | --- | --- |
| `--model` | string | `""` | `options.model.id` for this send. |
| `--mode` | string | `""` | `options.mode`; `agent` or `plan`. |
| `--mcp-config` | string | `""` | `options.mcpServers`; JSON object, `@file`, or `-`. |
| `--idempotency-key` | string | `""` | Top-level `idempotencyKey`. |
| `--message-file` | string | `""` | Read message text from a path or `-` (stdin); conflicts with positional text. |
| `--image` | repeatable string | `[]` | Local image path (base64 encoded) or HTTP(S) URL. |
| `--force` | bool | `false` | `options.local.force`. |
| `--send-env-var` | repeatable string | `[]` | `options.cloud.envVars`, each `KEY=VAL`, scoped to this run. |
| `--deltas` | bool | `false` | `options.enableDeltas`; request `interactionUpdate` events. |
| `--steps` | bool | `false` | `options.enableSteps`; request completed `step` events. |
| `--quiet` | bool | `false` | Suppress events and print only terminal `RunResult` through `-o`. |
| `--detach` | bool | `false` | Stop reading once a run ID is known; print `{agentId,runId}`. Conflicts with `--quiet`. |

### Custom-tool flags

Available on `agent create`, `agent prompt`, and `agent send`:

| Flag | Type | Default | Meaning |
| --- | --- | --- | --- |
| `--custom-tool` | repeatable string | `[]` | `NAME=COMMAND`. Create/prompt declares the local tool; send starts its executor. |
| `--custom-tool-config` | string | `""` | JSON, `@file`, or `-`: `{name:{description,inputSchema,command}}`. |

Custom tools are local-only. On send, these flags register callback executors but do not modify the Send request. The executor receives argument JSON on stdin and should emit a JSON object on stdout; non-object or non-JSON stdout is returned as `{"output":"..."}`.

## `agent` commands

### `agent create`

- Usage: `cursorctl agent create [flags]`; no positional arguments.
- RPC: `SdkAgentService/CreateAgent`.
- Flags: creation/resume option set, `--idempotency-key` (string, `""`), custom-tool flags, and `--json` (string, default `""`).
- `--json`: `CreateAgentRequest`:

```json
{
  "options": {
    "name": "delegate",
    "cloud": {
      "repos": [{"url": "https://github.com/acme/widgets", "startingRef": "main"}],
      "autoCreatePr": true
    }
  },
  "idempotencyKey": "issue-123"
}
```

Cursorctl injects `options.apiKey` unless supplied. Output:

```json
{"agentId": "bc-...", "model": {"id": "..."}}
```

### `agent resume`

- Usage: `cursorctl agent resume <agent-id> [flags]`; exactly one positional agent ID.
- RPC: `SdkAgentService/ResumeAgent`.
- Flags: creation/resume option set and `--json` (string, `""`). Resume does not register `--idempotency-key`.
- `--json`: `{"agentId":"bc-...","options":{"cloud":{}}}`; cursorctl injects `options.apiKey`.
- Output: `{"agentId":"bc-...","model":{"id":"..."}}`.

### `agent send`

- Usage: `cursorctl agent send <agent-id> [text] [flags]`.
- RPC: `ResumeAgent` then streaming `SdkAgentService/Send`, in the same bridge process. Cloud IDs (`bc-…`) resume with `{apiKey, cloud:{}}`; other IDs resume with `{apiKey, local:{cwd:[workspace]}}`.
- Positional text is optional only when `--message-file` or at least one `--image` supplies the message.
- Flags: complete send option set, custom-tool flags, and `--json` (string, `""`).
- `--json`: `SendRequest`:

```json
{
  "agentId": "bc-...",
  "message": {"text": "Run the tests and fix failures."},
  "options": {"enableSteps": true},
  "idempotencyKey": "follow-up-1"
}
```

Default output is NDJSON stream records. `--quiet` prints a `RunResult`; `--detach` prints `{"agentId":"bc-...","runId":"..."}`. See [output and JSON mode](output-and-json-mode.md).

### `agent prompt`

- Usage: `cursorctl agent prompt <text> [flags]`.
- Composite operation: `CreateAgent` → streaming `Send` → `CloseAgent`. `--detach` skips `CloseAgent` so a later `agent send` can follow up.
- Requires exactly one text argument or `--message-file`; images alone do not satisfy prompt's message check.
- Flags: creation/resume option set, `--idempotency-key` (string, `""`), send execution flags (`--message-file`, `--image`, `--force`, `--send-env-var`, `--deltas`, `--steps`, `--quiet`, `--detach`), custom-tool flags, and `--json` (string, `""`).
- `--json` is the composite shape, not an RPC request:

```json
{
  "options": {
    "cloud": {
      "repos": [{"url": "https://github.com/acme/widgets"}],
      "autoCreatePr": true
    }
  },
  "message": {"text": "Implement issue 123."},
  "sendOptions": {"enableSteps": true},
  "idempotencyKey": "issue-123"
}
```

Cursorctl injects `options.apiKey`; `idempotencyKey` is sent to both CreateAgent and Send. Output modes match `agent send`.

### `agent get`

- Usage/RPC: `agent get <agent-id>` → `GetAgent`.
- Flags: `--cwd` (string, `""`, local routing), `--json` (string, `""`).
- Payload: `{"agentId":"bc-...","options":{"cwd":"/repo"}}`; cursorctl injects `options.apiKey`.
- Output: `{"agent": SdkAgentInfo}` where info includes `agentId`, `name`, `summary`, `status`, timestamps, `archived`, and `local` or `cloud`.

### `agent list`

- Usage/RPC: `agent list` → `ListAgents`; no positionals.
- Flags:

| Flag | Type | Default | Options field |
| --- | --- | --- | --- |
| `--limit` | uint32 | `0` | `limit` |
| `--cursor` | string | `""` | `cursor` |
| `--runtime` | string | `""` | `runtime`; `local` or `cloud` |
| `--cwd` | string | `""` | `cwd` |
| `--pr-url` | string | `""` | `prUrl` |
| `--include-archived` | bool | `false` | `includeArchived` |
| `--json` | string | `""` | Complete request |

- Payload example: `{"options":{"runtime":"RUNTIME_CLOUD","limit":20,"includeArchived":false}}`; `options.apiKey` is injected.
- Output: `{"items":[SdkAgentInfo,...],"nextCursor":"..."}`.

### `agent messages`

- Usage/RPC: `agent messages <agent-id>` → `ListAgentMessages`.
- Flags:

| Flag | Type | Default | Options field |
| --- | --- | --- | --- |
| `--limit` | uint32 | `0` | `limit` |
| `--offset` | uint32 | `0` | `offset` |
| `--runtime` | string | `""` | `runtime`; local/cloud |
| `--cwd` | string | `""` | `cwd` |
| `--json` | string | `""` | Complete request |

- Payload: `{"agentId":"bc-...","options":{"limit":50,"offset":0}}`; `options.apiKey` is injected.
- Output: `{"messages":[{"type":"...","uuid":"...","agentId":"...","message":{...}},...]}`.

### `agent usage`

- Usage/RPC: `agent usage <agent-id>` → `GetUsage` (cloud only).
- Flags: `--run-id` (string, `""`, optional run filter), `--json` (string, `""`).
- Payload: `{"agentId":"bc-...","runId":"..."}`.
- Output: `{"usage":{"usage":{"inputTokens":"...","outputTokens":"...","totalTokens":"..."},"cost":{"rawCostCents":0,"chargedCents":0},"runs":[{"runId":"...","usage":{...},"cost":{...}}]}}`; cost fields may be absent.

### `agent archive` and `agent unarchive`

- Usage/RPC: `agent archive <agent-id>` → `ArchiveAgent`; `agent unarchive <agent-id>` → `UnarchiveAgent`.
- Flags on each: `--cwd` (string, `""`), `--json` (string, `""`).
- Payload: `{"agentId":"bc-...","options":{"cwd":"/repo"}}`; `options.apiKey` is injected.
- Output: `{}`.

### `agent delete`

- Usage/RPC: `agent delete <agent-id> --force` → `DeleteAgent`.
- Flags: `--cwd` (string, `""`), `--force` (bool, `false`, required safety confirmation), `--json` (string, `""`).
- `--force` is allowed with `--json` and is not part of the payload.
- Payload: `{"agentId":"bc-...","options":{}}`; `options.apiKey` is injected. Output: `{}`.

### `agent close` and `agent reload`

- Usage/RPC: `agent close <agent-id>` → `CloseAgent`; `agent reload <agent-id>` → `ReloadAgent`.
- Flags on each: `--json` (string, `""`).
- Payload: `{"agentId":"..."}`. Output: `{}`.

## `run` commands

Run snapshots/results contain `runId`, `agentId`, lifecycle `status`, assistant `result`, model, duration, git metadata, timestamps, and optional usage.

### `run get`

- Usage/RPC: `run get <run-id>` → `GetRun`.
- Flags: `--runtime` (string, `""`, local/cloud), `--cwd` (string, `""`), `--agent-id` (string, `""`, routing hint), `--json` (string, `""`).
- Group payload example:

```json
{
  "runId": "run-...",
  "options": {"runtime": "RUNTIME_CLOUD", "agentId": "bc-..."}
}
```

Cursorctl injects `options.apiKey`. Output: `{"run": RunSnapshot}`.

### `run list`

- Usage/RPC: `run list <agent-id>` → `ListRuns`.
- Flags: `--limit` (uint32, `0`), `--cursor` (string, `""`), `--runtime` (string, `""`, local/cloud), `--cwd` (string, `""`), `--json` (string, `""`).
- Payload: `{"agentId":"bc-...","options":{"limit":20,"runtime":"RUNTIME_CLOUD"}}`; `options.apiKey` is injected.
- Output: `{"items":[RunSnapshot,...],"nextCursor":"..."}`.

### `run wait`

- Usage/RPC: `run wait <run-id>` → `WaitLiveRun`.
- Flags: `--json` (string, `""`).
- Payload: `{"runId":"run-..."}`.
- Output: cursorctl unwraps the RPC response and prints the inner `RunResult`. Terminal failure statuses exit `2`.

### `run watch`

- Usage/RPC: `run watch <run-id>` → streaming `ObserveRun`.
- Flags: `--after-offset` (string, `""`), `--quiet` (bool, `false`), `--json` (string, `""`).
- Payload: `{"runId":"run-...","afterOffset":"opaque-token"}`.
- Output: NDJSON events, or terminal `RunResult` through `-o` with `--quiet`. The offset must come from a previous ObserveRun (`run watch`) stream.

### `run cancel`

- Usage/RPC: `run cancel <run-id>` → `CancelRun`.
- Flags: `--agent-id` (string, `""`, routing hint), `--json` (string, `""`).
- Payload: `{"runId":"run-...","agentId":"bc-..."}`. Output: `{}`.

### `run conversation`

- Usage/RPC: `run conversation <run-id>` → `GetRunConversation`.
- Flags: `--json` (string, `""`).
- Payload: `{"runId":"run-..."}`.
- RPC output is `{"conversationJson":"<JSON string>"}`; cursorctl decodes that string and prints the resulting JSON value through `-o`.

## `artifact` commands

### `artifact list`

- Usage/RPC: `artifact list <agent-id>` → `ListArtifacts`.
- Flags: `--json` (string, `""`).
- Group payload example: `{"agentId":"bc-..."}`.
- Output: `{"artifacts":[{"path":"reports/result.txt","sizeBytes":"123","updatedAt":"..."},...]}`.

### `artifact download`

- Usage/RPC: `artifact download <agent-id> <path>` → streaming `DownloadArtifact`.
- Flags: `--file` (string, `""`; `-` or unset means stdout), `--json` (string, `""`).
- Payload: `{"agentId":"bc-...","path":"reports/result.txt"}`.
- With `--file -` or no `--file`, stdout is the raw artifact bytes and `-o` does not apply. With `--file PATH`, cursorctl removes a partial destination on stream/write failure, then prints `{"path":"PATH","bytes":123}` through `-o` after success.

## Catalog commands

All three use `SdkCursorService`, take no positionals, expose only `--json` (string, `""`), and hard-require `options.apiKey`. Cursorctl injects the resolved key into this group payload:

```json
{"options": {}}
```

| Command | RPC | Output |
| --- | --- | --- |
| `me` | `Me` | `{"user":{"apiKeyName":"...","userId":"...","userEmail":"...",...}}` |
| `models` | `ListModels` | `{"items":[{"id":"...","displayName":"...","description":"...","parameters":[],"variants":[]},...]}` |
| `repos` | `ListRepositories` | `{"items":[{"url":"https://github.com/acme/widgets"},...]}` |

## Auth commands

Auth commands write and read `credentials.json` under `$CURSORCTL_CONFIG_DIR`, else `$XDG_CONFIG_HOME/cursorctl`, else `~/.config/cursorctl`. The file is `0600`; the directory is `0700`. They print through `-o` and never emit full API keys (fingerprints are `…` plus the last four characters). They need no Cursor API key and make no RPC.

Profile names match `[A-Za-z0-9][A-Za-z0-9._-]*`.

| Command | Positional/local flags | Output |
| --- | --- | --- |
| `auth add <name>` | `--stdin` (bool, `false`), `--default` (bool, `false`), `--force` (bool, `false`) | `{"name":"work","fingerprint":"…wxyz","default":true}`. Reads the key from stdin when `--stdin` is set; otherwise prompts on a TTY with a hidden `ReadPassword`. Replacing an existing name requires `--force`. The first stored profile becomes the default; `--default` switches it. |
| `auth list` | none | `{"defaultProfile":"work","profiles":[{"name":"personal","fingerprint":"…abcd","default":false},{"name":"work","fingerprint":"…wxyz","default":true}]}`. |
| `auth default [name]` | optional profile name | `{"defaultProfile":"work"}`. With a name, sets that profile as default. With no name, reports the current default (empty string if none). |
| `auth remove <name>` | none | `{"name":"work","removed":true}`. If the removed profile was default, `defaultProfile` is cleared rather than silently reassigned. |

`--api-key` on `auth add` is not accepted as the stored secret (argv leakage). Use `--stdin` or the TTY prompt.

## Bridge and version commands

The two bridge control RPCs expose `--json`; the non-RPC `bridge install` and `version` commands do not.

| Command | Positional/local flags | RPC | Output |
| --- | --- | --- | --- |
| `bridge install` | none | none | `{"version":"v1.0.27","path":"...","cached":true}`; pre-fetches/verifies the bridge and needs no API key. |
| `bridge ping` | `--json` (string, `""`) | `SdkBridgeControlService/Ping` with `{}` | `{"message":"pong"}`. |
| `bridge version` | `--json` (string, `""`) | `SdkBridgeControlService/GetVersion` with `{}` | `{"bridgeVersion":"1.0.0","protocolVersion":"sdk.v1","capabilities":[...]}`. |
| `version` | none | none | `{"version":"...","bridgeVersion":"v1.0.27","goVersion":"go..."}`; needs no API key. |

`bridge ping` and `bridge version` need no Cursor API key. Their raw JSON payload is passed through without API-key injection.

## Completion commands

The default `completion` command is hidden from root help but remains directly invokable. `completion bash`, `completion fish`, `completion powershell`, and `completion zsh` take no positional arguments and write a shell completion script to stdout. Each has `--no-descriptions` (bool, default `false`) plus inherited global flags. They have no RPC, no `--json`, and do not require an API key.
