# Phase 3: Implement

**Goal**: Implement the plan with quality gates.

Follow one of these implementation skills (first available wins):
- **`/conductor:implement`** — TDD task execution against a conductor track's implementation plan
- **`superpowers:subagent-driven-development`** — parallel subagent execution of independent plan tasks in the current session
- **`superpowers:executing-plans`** — multi-session plan execution with review checkpoints

If none are installed, proceed inline with the steps below.

### Step 3.1: Read Plan from file
Per [rules.md §1.4](rules.md#14-artifacts-are-source-of-truth), read `<artifact_dir>/plan.md` from disk — never reconstruct from conversation context. Parse tasks, files to modify, acceptance criteria, and implementation order (waves).

### Step 3.2: Dependency Verification (multi-wave plans)
For each prior wave, verify files exist on disk using Glob. Print verification matrix. If incomplete → ask user.

### Step 3.3: Implement Each Task
Default: **TDD mode** (RED → GREEN → REFACTOR).

When **swarm mode** is available (MM profile with layer separation):
- Spawn one agent per layer with file ownership boundaries
- Sequential dependencies: model → store → app → API → webapp
- After each layer completes, broadcast interface summary to remaining agents

Without swarm mode: implement sequentially in the leader context.

Principle citation: [rules.md §8](rules.md#8-principle-applications) — production-ready, not just test-passing.

**Comment discipline ([rules.md §1.8](rules.md#18-comment-discipline))**: default to no comments. Do not narrate the diff with `// added for <task>`, `// TODO`, or commented-out code — that context belongs in the commit message and ticket, not the source. Multi-line comments require a strong, specific WHY (non-obvious invariant, upstream-bug workaround with link, public-API contract). Before completing each task, re-scan the diff and delete any comment that fails the §1.8 test. Apply this in both leader-mode and swarm-mode; brief each layer agent on §1.8 in their dispatch prompt.

### Step 3.4: Auto-Review (MANDATORY)
Run review agents scaled to what changed:
- **Tier 1** (always): `simplicity-reviewer`, `error-handling-reviewer`, `duplication-reviewer`
- **Tier 3** (if Go): `api-reviewer`, `app-reviewer`, `store-reviewer`, `pattern-reviewer`
- **Tier 4** (if TS/React): `react-frontend`, `redux-expert`, `component-reviewer`
- **Tier 5** (if tests): `test-coverage-reviewer`
- **Tier 6** (if model/API surface): `backwards-compatibility-reviewer`, `null-safety-reviewer`

Round budget: 2 ([rules.md §4](rules.md#4-retry--escalation-budgets)). Fix MUST_FIX items. After 2 rounds, report any remaining.

Update state.json per [rules.md §1.5](rules.md#15-statejson-update-ritual). Record checkpoint commit SHA per [rules.md §1.6](rules.md#16-checkpoint-commits-at-gates).
