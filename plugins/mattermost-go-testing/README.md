# mattermost-go-testing

Skills for writing, reviewing, and auditing Go tests in the Mattermost server repo. Captures institutional knowledge around parallel CI constraints, layer-specific test patterns, and the `readOnlyFF` trap — things that burn engineers and aren't documented anywhere in the codebase.

## Skills

| Skill | Description |
|-------|-------------|
| `test-writer` | Write comprehensive parallel-safe Go tests for App, Store, and API layers |
| `test-coverage-reviewer` | Review staged changes for missing coverage and parallel-safety violations |
| `parallel-test-writer` | Write or audit Go tests specifically for `t.Parallel()` correctness |

## Usage

```text
/mattermost-go-testing:test-writer
```

Point it at a source file or function and it will read existing tests in the package as analogues, then write comprehensive parallel-safe tests covering success paths, error paths, and edge cases.

```text
/mattermost-go-testing:test-coverage-reviewer
```

Run before committing. Scans staged Go changes for new functions without tests, incomplete coverage, and parallel-safety violations — including the `readOnlyFF` feature flag trap.

```text
/mattermost-go-testing:parallel-test-writer
```

Use in write mode to generate parallel-safe tests from scratch, or in audit mode to classify existing tests as `SAFE_FOR_PARALLEL`, `INTENTIONALLY_SERIAL`, or `UNSAFE_FOR_PARALLEL` with specific fix instructions.

## How It Works

All three skills share `parallel-test-rules.md` as a reference — a comprehensive ruleset covering Mattermost's `gotestsum --fullyparallel` CI constraints across 4 sharded runners.

**test-writer** reads the source under test, finds 2–3 existing tests in the same package as analogues, then writes tests that match the package's conventions exactly. Enforces parallel safety and correct setup helper usage throughout.

**test-coverage-reviewer** inspects staged changes using `git diff`, identifies new exported functions and modified logic, checks for corresponding tests, and audits all touched test files for parallel-safety violations with tagged findings (`parallel:READONLY_FF`, `parallel:ENV_MUTATION`, etc.).

**parallel-test-writer** focuses entirely on the parallel dimension — either writing new tests with parallel safety built in from the start, or auditing existing test files and producing a per-test classification report.

## Guiding Principles

- **Read before writing** — always find analogues in the package before writing a single test
- **Real over mocked** — use the real App, real Store, real DB; never mock internal interfaces
- **Parallel by default** — every Go test is parallel-safe unless explicitly marked serial with a comment explaining why
- **The readOnlyFF trap is always checked** — `Setup(t)` + `UpdateConfig` for feature flags silently drops the change; the correct setup helper is always enforced
- **Classify, don't skip** — a skipped test hides the problem; classify it correctly and fix it

## Author

Pablo Vélez
