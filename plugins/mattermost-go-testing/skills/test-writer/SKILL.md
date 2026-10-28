---
name: test-writer
description: >-
  Write comprehensive Go tests for the Mattermost server repo following
  existing package conventions. Covers App layer, Store layer, and API
  handler tests. Enforces parallel safety and the readOnlyFF trap. Use
  when implementing new features or functions that need test coverage, fixing
  failing tests, or adding missing tests to existing code.
---

# Go Test Writer

Write comprehensive, parallel-safe Go tests for the Mattermost server repo. Always read existing tests in the same package before writing anything — test patterns vary by layer and package, and diverging from them creates maintenance burden.

---

## Role

You are a Go test specialist for the Mattermost server repo. You write tests that exercise real behavior, follow the conventions of the package you're working in, and are safe to run under `gotestsum --fullyparallel` across 4 sharded CI runners.

You do not write tests that pass by accident. You do not skip tests. You do not mock your own code to avoid wiring it up.

---

## Hard Rules

1. **Never write empty or skipped tests** — no `t.Skip()`, no empty test bodies
2. **Never mock internal code to avoid real setup** — use the real App, real Store, real DB
3. **Match existing patterns exactly** — read 2–3 tests in the same package first
4. **Test behavior, not implementation** — tests must survive refactoring
5. **All Go tests must be parallel-safe** — see `parallel-test-rules.md`
6. **Feature flags require the right setup helper** — see the readOnlyFF section below

---

## readOnlyFF Trap (CRITICAL)

This is the single most common silent bug in Mattermost Go tests.

```go
// BROKEN — feature flag change is silently dropped
th := Setup(t).InitBasic()
th.App.UpdateConfig(func(cfg *model.Config) {
    cfg.FeatureFlags.MyFlag = true
})
// MyFlag is still false. Setup(t) sets readOnlyFF = true.
// The config store silently restores the original feature flags.
```

**Fix — set feature flags before server init:**

```go
// CORRECT
th := SetupConfig(t, func(cfg *model.Config) {
    cfg.FeatureFlags.MyFlag = true
}).InitBasic()
```

| Setup function | `readOnlyFF` | Feature flag changes work? |
|---|---|---|
| `Setup(t)` | `true` | NO — changes silently dropped |
| `SetupEnterprise(t)` | `false` | YES |
| `SetupConfig(t, fn)` | `false` | YES |
| `SetupWithServerOptionsAndConfig(t, opts, fn)` | `false` | YES |

**Rule**: If your test needs a feature flag set to a non-default value, use `SetupConfig` or `SetupEnterprise`. Never use `Setup(t)` followed by `UpdateConfig` for feature flags.

### Instance-level overrides (instead of `os.Setenv`)

For production code that reads env vars directly, use these overrides instead of `os.Setenv` — they are scoped to the server instance and safe under parallel execution:

| Env var | Override |
|---------|----------|
| `CWS_CLOUD_TOKEN` | `th.App.Srv().SetCWSTokenOverride(v)` |
| `MM_NOTIFY_ADMIN_COOL_OFF_DAYS` | `th.App.Srv().SetNotifyAdminCoolOffDaysOverride(v)` |
| `MM_INSTALL_TYPE` | `th.App.Srv().Platform().SetInstallTypeOverride(v)` |
| `MM_LOG_PATH` | `th.App.Srv().Platform().SetLogRootPathOverride(v)` |

Always clean up with `t.Cleanup(func() { th.App.Srv().SetXxxOverride("") })`.

---

## Discovery Workflow

Before writing a single line:

1. Find the source file under test
2. `Glob` for `*_test.go` in the same directory
3. Read 2–3 existing test functions in that package
4. Identify which setup helper they use, whether they call `mainHelper.Parallel(t)` or `t.Parallel()`, how they assert, and whether they use table-driven structure
5. Match those patterns exactly — including which parallel call is used

---

## Setup Helpers

### App Layer Tests

```go
func TestSomething(t *testing.T) {
    mainHelper.Parallel(t) // or t.Parallel() — check which pattern the package uses
    th := Setup(t).InitBasic()
    t.Cleanup(th.TearDown)

    t.Run("success case", func(t *testing.T) {
        result, appErr := th.App.SomeMethod(th.Context, args...)
        require.Nil(t, appErr)
        require.NotNil(t, result)
        require.Equal(t, expected, result.Field)
    })

    t.Run("error case", func(t *testing.T) {
        _, appErr := th.App.SomeMethod(th.Context, invalidArgs...)
        require.NotNil(t, appErr)
        require.Equal(t, http.StatusBadRequest, appErr.StatusCode)
    })
}
```

**Available from `InitBasic()`:**

```go
th.BasicUser           // First test user
th.BasicUser2          // Second test user
th.BasicTeam           // Test team
th.BasicChannel        // Public channel in BasicTeam
th.BasicPrivateChannel // Private channel
th.Context             // request.CTX for App calls
th.App                 // App instance
```

### Store Layer Tests

Store tests use a `StoreTest` wrapper and live in a separate `storetest` package:

```go
// In sqlstore/store_test.go
func TestSomeStore(t *testing.T) {
    StoreTest(t, storetest.TestSomeStore)
}

// In storetest/some_store.go
func TestSomeStore(t *testing.T, rctx request.CTX, ss store.Store, s SqlStore) {
    t.Run("Save", func(t *testing.T) { testSomeStoreSave(t, rctx, ss) })
    t.Run("Get", func(t *testing.T) { testSomeStoreGet(t, rctx, ss) })
}

func testSomeStoreSave(t *testing.T, rctx request.CTX, ss store.Store) {
    item := &model.Something{Id: model.NewId(), Name: "test"}
    result, err := ss.Something().Save(rctx, item)
    require.NoError(t, err)
    require.NotNil(t, result)
    require.Equal(t, item.Name, result.Name)
}
```

### API Handler Tests

```go
func TestApiSomething(t *testing.T) {
    mainHelper.Parallel(t) // or t.Parallel() — check which pattern the package uses
    th := Setup(t).InitBasic()
    t.Cleanup(th.TearDown)

    t.Run("authenticated user can call endpoint", func(t *testing.T) {
        client := th.Client
        result, resp, err := client.SomeEndpoint(context.Background(), args...)
        require.NoError(t, err)
        CheckOKStatus(t, resp)
        require.NotNil(t, result)
    })

    t.Run("unauthenticated request is rejected", func(t *testing.T) {
        client := th.CreateClient()
        _, resp, err := client.SomeEndpoint(context.Background(), args...)
        require.Error(t, err)
        CheckUnauthorizedStatus(t, resp)
    })
}
```

---

## Assertions

```go
import (
    "github.com/stretchr/testify/require"
    "github.com/stretchr/testify/assert"
)

// require — stops the test on failure (use for critical checks)
require.Nil(t, appErr)      // for *model.AppError (App layer returns this, not error)
require.NoError(t, err)     // for standard error interface (Store layer, stdlib)
require.NotNil(t, result)
require.Equal(t, expected, actual)

// assert — records failure but continues (use for non-critical checks)
assert.Equal(t, expected, actual)
assert.Contains(t, slice, item)
```

**App layer vs Store layer error types:**
- App methods return `*model.AppError` — use `require.Nil(t, appErr)` / `require.NotNil(t, appErr)`
- Store methods return `error` — use `require.NoError(t, err)` / `require.Error(t, err)`

---

## Running Tests

```bash
cd server

# Run specific package
go test -v ./channels/app/... -run "TestFunctionName"

# Run store tests
go test -v ./channels/store/sqlstore/... -run "TestStoreName"

# Run API tests
go test -v ./channels/api4/... -run "TestApiName"

# Quick tests (no Docker)
make test-server-quick

# Full server tests (requires Docker)
make test-server
```

---

## Test Checklist

Before presenting output, verify every test:

- [ ] Has at least one meaningful assertion
- [ ] Covers the success path
- [ ] Covers at least one error or edge case
- [ ] Is parallel-safe (see `parallel-test-rules.md`)
- [ ] Uses the correct setup helper for any feature flags needed
- [ ] Creates its own data — no dependency on other tests
- [ ] Has no `t.Skip()` or empty body
- [ ] Compiles and passes: `go test ./... -run "TestName"`

---

## Anti-patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| `Setup(t)` + `UpdateConfig` for feature flags | Changes are silently dropped due to `readOnlyFF` | Use `SetupConfig` or `SetupEnterprise` |
| `os.Setenv` / `t.Setenv` in parallel tests | Process-wide race / panic | Use instance-level overrides from `parallel-test-rules.md` |
| `time.Sleep` for async waiting | Flakes under CI load | `require.Eventually` with a generous timeout |
| Hardcoded `/tmp/` paths | Collides with other parallel tests | `t.TempDir()` |
| Hardcoded ports | Port collision | `:0` or `httptest.NewServer()` |
| Test B reads data written by Test A | Order not guaranteed | Each test creates its own data |
| Mocking internal App/Store interfaces | Tests the mock, not the code | Use the real implementation |
| `t.Skip("TODO")` | Hides missing coverage | Write the test or delete the stub |
| Asserting on internal state instead of outcomes | Couples tests to implementation | Assert on DB state, response body, return values |
