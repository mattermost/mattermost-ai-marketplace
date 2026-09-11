---
name: parallel-test-rules
description: Rules for writing Go tests compatible with Mattermost's fully-parallel sharded CI. Referenced by the parallel-test-writer skill.
---

# Parallel Test Safety Rules

Mattermost runs server tests with `gotestsum --fullyparallel` across 4 sharded CI runners. Every test may run in parallel. Tests that modify process-wide state will panic, race, or flake.

**Core principle**: The safest test is one with no shared mutable state. If you reach for `os.Setenv`, a global variable, or a hardcoded path — inject the dependency instead.

## Hard Rules (violations = MUST_FIX)

### 1. No environment variable mutation

| Pattern | Problem |
|---------|---------|
| `t.Setenv()` | Panics under `t.Parallel()` |
| `os.Setenv()` / `os.Unsetenv()` | Process-wide race condition |

**Fix**: If the code reads env vars directly, use an instance-level override (see Mattermost Helpers below). For feature flags, use `SetupConfig` or `SetupEnterprise` — NOT `th.App.UpdateConfig()`, which is silently dropped when `readOnlyFF = true` (see Setup variants below). For non-feature-flag config changes, `th.App.UpdateConfig()` works fine.

**Exception**: Tests that ARE testing env var behavior (config tests, Elasticsearch tests) may use `t.Setenv` but must NOT call `t.Parallel()` and must include a comment: `// intentionally serial — testing env var behavior`.

### 2. No working directory changes

| Pattern | Problem |
|---------|---------|
| `os.Chdir()` | Process-wide, affects all goroutines |

**Fix**: Use `t.Chdir()` (Go 1.24+) or pass absolute paths.

### 3. No package-level mutable state

| Pattern | Problem |
|---------|---------|
| Writing to package-level vars | Data race |
| Mutating shared config from `TestMain` | Data race |

**Fix**: Clone per test — `cfg := defaultConfig.Clone()`.

### 4. No cross-test data dependencies

| Pattern | Problem |
|---------|---------|
| Test B assumes rows created by Test A | Ordering not guaranteed |
| Fixed usernames/IDs shared across tests | Collision |

**Fix**: Each test creates its own data. Use unique IDs.

### 5. No hardcoded filesystem paths

| Pattern | Problem |
|---------|---------|
| `"/tmp/export.zip"` | Collision with parallel tests |

**Fix**: `filepath.Join(t.TempDir(), "export.zip")`.

### 6. No hardcoded ports

| Pattern | Problem |
|---------|---------|
| `net.Listen("tcp", ":8999")` | Port collision |

**Fix**: Use `:0` or `httptest.NewServer()`.

### 7. No fixed sleeps for async waiting

| Pattern | Problem |
|---------|---------|
| `time.Sleep(3 * time.Second)` | Insufficient under CI load |

**Fix**: `require.Eventually(t, func() bool { ... }, 15*time.Second, 200*time.Millisecond)`.

## Soft Rules (violations = SHOULD_FIX)

### 8. Widen time-based query windows
Narrow before/after windows around DB operations fail under load. Use generous buffers (seconds, not milliseconds).

### 9. Use far-future timestamps when ordering matters
Tests that create records with "now" timestamps and assert recency/ordering will collide with parallel tests. Use far-future timestamps to isolate test data.

### 10. Parallel subtests must be independent
If subtests depend on sibling ordering or side effects (create then delete), do NOT call `t.Parallel()` on them. The parent can be parallel; sequential subtests within it are fine.

## Mattermost-Specific Helpers

### Setup variants and `readOnlyFF`

**Critical**: Feature flag changes via `th.App.UpdateConfig()` are SILENTLY DROPPED when `readOnlyFF = true`. The config store restores old feature flags.

| Setup function | `readOnlyFF` | Feature flag changes work? |
|---|---|---|
| `Setup(t)` | `true` | NO — changes silently dropped |
| `SetupEnterprise(t)` | `false` | YES |
| `SetupConfig(t, updateConfig)` | `false` | YES |
| `SetupWithServerOptionsAndConfig(t, opts, updateConfig)` | `false` | YES |

**Rule**: To set feature flags, either:
- Use `SetupConfig(t, func(cfg *model.Config) { cfg.FeatureFlags.X = true })` — applies before server init
- Use `SetupEnterprise(t)` — sets `readOnlyFF = false`
- Do NOT use `Setup(t)` followed by `th.App.UpdateConfig()` for feature flags

If a feature flag's default value (in `model.FeatureFlags.SetDefaults()`) already matches what you need, no `UpdateConfig` is necessary.

### Config that must be set before server init

Audit settings, some service settings, and other config read at startup must be applied before `NewServer` runs. Use `SetupWithServerOptionsAndConfig`:

```go
th := SetupWithServerOptionsAndConfig(t, options, func(cfg *model.Config) {
    cfg.ExperimentalAuditSettings.FileEnabled = model.NewPointer(true)
    cfg.ExperimentalAuditSettings.FileName = model.NewPointer(logFile.Name())
})
```

### Instance-level overrides (instead of env vars)

For production code that reads env vars directly, use the instance-level overrides:

| Env var | Override |
|---------|----------|
| `CWS_CLOUD_TOKEN` | `th.App.Srv().SetCWSTokenOverride(v)` |
| `MM_NOTIFY_ADMIN_COOL_OFF_DAYS` | `th.App.Srv().SetNotifyAdminCoolOffDaysOverride(v)` |
| `MM_INSTALL_TYPE` | `th.App.Srv().Platform().SetInstallTypeOverride(v)` |
| `MM_LOG_PATH` | `th.App.Srv().Platform().SetLogRootPathOverride(v)` |

Always clean up with `t.Cleanup(func() { ...SetOverride("") })`.

### `mainHelper.Parallel(t)`

Many test functions call `mainHelper.Parallel(t)` at the top level. This marks the test as parallel-safe. Subtests within it run sequentially unless they individually call `t.Parallel()`.

## Classification

When reviewing or generating tests, classify each as:

| Classification | Meaning |
|---|---|
| `SAFE_FOR_PARALLEL` | No shared mutable state hazards |
| `INTENTIONALLY_SERIAL` | Tests env var behavior or process-wide state by design. Must include comment explaining why. |
| `UNSAFE_FOR_PARALLEL` | Would panic, race, or flake under parallel execution |
