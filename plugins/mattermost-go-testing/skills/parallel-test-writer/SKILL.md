---
name: parallel-test-writer
description: >-
  Write new Go tests that are safe for Mattermost's fully-parallel sharded CI,
  or audit existing Go tests for parallel-safety violations. Loads
  parallel-test-rules.md as a reference. Use when the user asks to write Go
  tests in the Mattermost server repo, audit tests for t.Parallel() correctness,
  fix flaky CI failures caused by shared state, or review a test file for
  parallel safety classification.
---

# Parallel Test Writer

Mattermost runs server tests with `gotestsum --fullyparallel` across 4 sharded CI runners. Every test may run concurrently with every other test. Tests that mutate process-wide state will panic, race, or flake silently.

**Core principle**: The safest test is one with no shared mutable state. If you reach for `os.Setenv`, a global variable, or a hardcoded path — stop and inject the dependency instead.

Load `parallel-test-rules.md` from the same directory as this skill before proceeding.

---

## Role

This skill operates as a Go test specialist with deep knowledge of Mattermost's CI constraints and server test infrastructure. It does not guess — it reads existing test files to understand the package's conventions before writing a single line.

It operates in two modes:

- **Write mode** — given source code or a feature description, write new parallel-safe Go tests
- **Audit mode** — given existing test files, classify each test and flag violations

---

## Write Mode

Use when the user asks you to write tests for Go code in the Mattermost server repo.

### Step 1: Read the source code

Read the file(s) under test. Identify:
- Exported functions and methods to cover
- Error paths and edge cases
- Any config, feature flags, or env vars the code reads

### Step 2: Find existing tests as analogues

Before writing anything, locate 2–3 existing test files in the same package or a sibling package. Read them to understand:
- Which setup helper is used (`Setup`, `SetupConfig`, `SetupEnterprise`, `SetupWithServerOptionsAndConfig`)
- Whether `mainHelper.Parallel(t)` or `t.Parallel()` is used at the top level
- The assertion style (`require` vs `assert`)
- Whether the package uses table-driven tests

### Step 3: Write the tests

Apply every Hard Rule from `parallel-test-rules.md`. For every test:

- Call `t.Parallel()` or `mainHelper.Parallel(t)` as the first statement unless the test is intentionally serial
- Use `t.TempDir()` for any filesystem paths
- Use `:0` or `httptest.NewServer()` for any ports
- Use `require.Eventually` instead of `time.Sleep`
- Create all required data within the test; never rely on data from other tests
- Use `SetupConfig` or `SetupEnterprise` when feature flags must be set — never `Setup(t)` followed by `UpdateConfig`
- Use instance-level overrides instead of `os.Setenv` (see `parallel-test-rules.md`)

Add a classification comment above each test function:

```go
// SAFE_FOR_PARALLEL
func TestCreatePost(t *testing.T) {
```

```go
// INTENTIONALLY_SERIAL — tests env var behavior directly
func TestElasticsearch_EnvConfig(t *testing.T) {
```

### Step 4: Verify

Re-read every test you wrote against the Hard Rules in `parallel-test-rules.md`. Fix any violations before presenting output.

---

## Audit Mode

Use when the user asks you to review, audit, or check existing test files for parallel safety.

### Step 1: Read the test files

Read all test files the user points at.

### Step 2: Scan for Hard Rule violations

For every test function, look for:

| Rule | What to look for |
|------|-----------------|
| Env var mutation | `t.Setenv`, `os.Setenv`, `os.Unsetenv` |
| Working directory change | `os.Chdir` |
| Package-level mutable state | writes to package-level vars, `TestMain` config mutation |
| Cross-test data deps | hardcoded usernames/IDs used across multiple tests |
| Hardcoded filesystem paths | `"/tmp/`, hardcoded absolute paths |
| Hardcoded ports | specific port numbers in `net.Listen` strings |
| Fixed sleeps | `time.Sleep` |
| readOnlyFF trap | `Setup(t)` followed by `th.App.UpdateConfig()` for feature flags |

### Step 3: Produce the audit report

Output a table with one row per test function:

| Test | Classification | Violations | Action |
|------|---------------|------------|--------|
| `TestCreatePost` | `SAFE_FOR_PARALLEL` | — | None |
| `TestConfig_Env` | `INTENTIONALLY_SERIAL` | `t.Setenv` (intentional) | Add classification comment |
| `TestHandleWebhook` | `UNSAFE_FOR_PARALLEL` | `os.Setenv` without isolation | Replace with instance-level override |

After the table, list every `UNSAFE_FOR_PARALLEL` test with a specific fix referencing the relevant Hard Rule number from `parallel-test-rules.md`.

---

## Anti-patterns

Flag any of these immediately:

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| `t.Setenv` with `t.Parallel()` | Panics at runtime under parallel execution | Use instance-level override or remove `t.Parallel()` with a serial comment |
| `os.Setenv` anywhere in a parallel test | Process-wide race — other tests see the mutation | Use instance-level overrides from `parallel-test-rules.md` |
| `time.Sleep` for async waiting | Flakes under CI load when runners are busy | `require.Eventually` with generous timeout |
| `Setup(t)` + `UpdateConfig` for feature flags | Feature flag changes are silently dropped | Use `SetupConfig` or `SetupEnterprise` |
| Hardcoded `/tmp/` paths | Collides with parallel tests writing the same path | `t.TempDir()` generates an isolated directory per test |
| Hardcoded port numbers | Port collision when tests run in parallel | `:0` lets the OS assign a free port |
| Test B reads data created by Test A | Ordering not guaranteed in parallel runs | Each test creates its own data with unique IDs |
| Skipping a test instead of fixing it | Masks unsafe behavior instead of resolving it | Classify correctly and apply the appropriate fix |
