# Troubleshooting cursorctl

## Authentication failures

For agent, run, artifact, and catalog commands, cursorctl resolves a key before starting the bridge:

1. `--api-key` if non-empty;
2. otherwise the environment variable whose name is set by `--api-key-env`;
3. otherwise `--profile` if non-empty, else `CURSORCTL_PROFILE`;
4. otherwise the stored default profile from `credentials.json`;
5. otherwise exit `1`.

`bridge ping` and `bridge version` are control-plane exceptions: they start the bridge and call their RPC without requiring or injecting a Cursor API key. `auth` commands only touch the local credentials file.

For example:

```bash
cursorctl --api-key-env MY_CURSOR_KEY models
```

Without that variable and with no stored profile:

```text
error: missing Cursor API key: set --api-key, environment variable MY_CURSOR_KEY, or run cursorctl auth add <name>
```

Unknown `--profile` / `CURSORCTL_PROFILE` names fail with `unknown auth profile "work"` (the credentials path is not included).

Set the variable by name, not literally `CURSOR_API_KEY`, when overriding:

```bash
export MY_CURSOR_KEY="cursor_..."
cursorctl --api-key-env MY_CURSOR_KEY me
```

Prefer `cursorctl auth add` over putting `CURSOR_API_KEY` in `~/.zshrc`. Cursor’s `agent` CLI resolves `CURSOR_API_KEY` before keychain/`agent login`, and an invalid or mismatched env key exits instead of falling back. cursorctl reads the profile itself and injects the key only into the SDK Bridge child process.

```bash
cursorctl auth add work --stdin --default
cursorctl --profile work me
```

Credentials live at `$CURSORCTL_CONFIG_DIR/credentials.json`, else `$XDG_CONFIG_HOME/cursorctl/credentials.json`, else `~/.config/cursorctl/credentials.json` (file mode `0600`). Load fails if the file is group- or world-readable.

`me`, `models`, and `repos` are special at the wire layer: catalog RPCs require `options.apiKey` and do not fall back to the bridge process environment. Cursorctl injects the resolved key, including for `--json '{}'`. If calling with raw JSON, an existing `options.apiKey` is preserved.

An RPC `UNAUTHENTICATED`, `UNAUTHORIZED`, or `API_KEY_NOT_FOUND` after local key resolution means the bridge/backend rejected the key; it is not the same as cursorctl's local “missing” error. Check key validity and repository/account access. Do not use `--verbose` in a context where bridge diagnostics may expose sensitive surrounding data.

## Bridge install and startup failures

The first bridge-backed command installs pinned release `v1.0.27` under:

```text
~/.cache/cursorctl/sdk-bridge/v1.0.27/bin/cursor-sdk-bridge
```

The installer downloads `SHA256SUMS.txt` and the platform archive from the SDK Bridge GitHub release, then verifies SHA-256 before publishing it. Pre-fetch while online:

```bash
cursorctl bridge install
```

`bridge install`, `bridge ping`, and `bridge version` need no Cursor API key. For offline execution, pre-populate the cache or point at a regular local bridge binary:

```bash
export CURSOR_SDK_BRIDGE_BIN=/opt/cursor/bin/cursor-sdk-bridge
# or, with higher precedence:
cursorctl --bridge-bin /opt/cursor/bin/cursor-sdk-bridge bridge version
```

The override is not copied into the cache. Ensure it is executable; validation only confirms that it is a regular file, so a permission problem appears when cursorctl tries to start it.

Common errors:

| Error text/pattern | Action |
| --- | --- |
| `download bridge checksums` / `download bridge archive` | Restore network access to GitHub Releases, pre-install elsewhere, or use a binary override. |
| `bridge archive checksum mismatch` | Do not bypass it. Remove the suspect download path/cache entry and retry from the official release. |
| `unsupported bridge platform` / `unsupported bridge architecture` | The built-in installer currently maps Linux/macOS on amd64/arm64. Supply a compatible standalone bridge with `--bridge-bin`/`CURSOR_SDK_BRIDGE_BIN` on another supported bridge platform. |
| `bridge did not become ready within 30s` | Run with `--verbose`; verify binary compatibility, execute permission, workspace access, and local process restrictions. |
| `bridge stderr closed before ready handshake` | Inspect the appended startup stderr in the error; the binary exited before publishing its handshake. |
| handshake schema/transport/protocol error | The selected binary is incompatible. Use the pinned bridge or a protocol-compatible build. |

`--timeout` covers download plus the command and can expire before the bridge's own 30-second readiness limit. `--bridge-version` changes the requested release; do so only when protocol compatibility has been verified.

## Truncated or malformed streams

A Connect stream must end with an EndStream frame. Abrupt network/process termination produces an exit-`1` error such as:

```text
run stream ended unexpectedly: stream closed without EndStream frame: unexpected EOF
```

Other useful distinctions:

- `run stream ended without a result`: the transport ended normally but no terminal result envelope arrived.
- `run stream ended before reporting a run ID`: `--detach` never received an init/result/done run ID.
- `decode ... stream envelope`: the bridge returned malformed JSON for that envelope.
- A Connect EndStream `error` is an RPC/stream failure, also exit `1`.

Closing or losing Send observation does not itself cancel the server-side run. Recover with the identifiers each command requires: `run get` needs both the recorded `run_id` and `agent_id` (cloud routing hint). `run watch` and `run wait` take only the recorded `run_id` and do not accept routing flags.

```bash
cursorctl run get "$run_id" --runtime cloud --agent-id "$agent_id"
cursorctl run watch "$run_id"
cursorctl run wait "$run_id"
```

Resume `run watch --after-offset TOKEN` only from an offset emitted by an earlier `run watch`. A Send-stream offset is not interchangeable.

## RPC failure versus run failure

These require different responses:

| Symptom | Exit | Meaning |
| --- | --- | --- |
| Missing key, validation error, bridge failure, non-200 unary error, EndStream error, truncated stream | `1` | The CLI/RPC/observation failed. Fix configuration or transport; determine separately whether a run started. |
| Terminal result status `ERROR`, `CANCELLED`, or `EXPIRED` from send/prompt/watch/wait | `2` | The RPC stream worked and the agent run reached a failed terminal state. Inspect prior status events, `.result`, conversation, and artifacts. |
| `run get` successfully reports an ERROR snapshot | `0` | Snapshot retrieval succeeded. Check `.run.status`; inspection commands do not convert observed status into process exit `2`. |

On agent failures, human-readable details may be in an earlier `sdkMessage` with `type: "status"` even when the stream result's `errorCode` is empty. Preserve NDJSON when diagnosing:

```bash
cursorctl run watch "$run_id" | tee run.ndjson
jq -c 'select(.event == "sdkMessage" and .type == "status")' run.ndjson
```

## Local versus cloud runtime

The CLI does not have a single `--runtime` switch for creation. Runtime is selected by creation flags:

- Any cloud option (`--repo`, `--auto-create-pr`, `--env-type`, and so on) builds `options.cloud`.
- Otherwise cursorctl builds `options.local` and defaults its primary cwd to global `--workspace`.
- Local and cloud creation flags cannot be combined.

Local agents:

- require `--model` according to the SDK contract;
- operate on this machine's paths, so use the same `--cwd` when routing later local management calls;
- may use built-in tool allowlists, local settings, sandboxing, and cursorctl custom tools;
- can use additional roots through repeatable `--dir`.

For a custom-tool run, keep the `agent send`/`agent prompt` process attached: cursorctl owns the loopback executor only for that command's lifetime, so detaching also shuts down the executor needed by later tool calls.

Cloud agents:

- clone one or more `--repo URL[@ref]` values;
- have IDs beginning with `bc-`, which the SDK uses for cloud routing;
- may omit a model and let the backend select it;
- do not support cursorctl custom tools;
- reject cloud environment variable names in the reserved `CURSOR_*` namespace at the SDK/backend layer.

If only a run ID is available, routing may be ambiguous. Supply hints:

```bash
cursorctl run get "$run_id" --runtime cloud --agent-id "$agent_id"
```

Do not pass a `bc-...` agent ID where a run ID is required. For local agent listing/get/messages/archive operations, preserve the original working directory and pass `--cwd`.

`--pr-url` on creation requires exactly one `--repo`. `--repo` accepts HTTPS or SSH-style values and treats a final `@ref` after the last slash as the starting ref.

## Follow-up send and Unknown agent

Each `cursorctl` invocation starts a fresh SDK Bridge. `Send` only sees agents loaded in that process. `agent send` therefore calls `ResumeAgent` before `Send` so a later `cursorctl agent send bc-...` can follow up after `agent prompt --detach` or `agent create`.

If resume/send still returns `Unknown agent`, the cloud record is gone (`agent get` will also fail) or the ID is not a `bc-` cloud agent and needs `--cwd` / `--workspace` matching the original local agent. Do not run a separate `agent resume` in one process and `agent send` in another and expect the first resume to persist.
