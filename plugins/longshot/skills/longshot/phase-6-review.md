# Phase 6: Review (skip with `--skip review`)

**Goal**: Multi-dimensional review driven by [`/comprehensive-review:full-review`](../../plugins/comprehensive-review/), cataloged to longshot findings, polished via `/review`.

Principle citation: [rules.md §8](rules.md#8-principle-applications) — strong self-review; reviewers aren't a safety net.

**Prerequisite**: `state.json.artifact_dir` resolved. Full pipeline sets this in Phase 0; `--only` invocations run a minimal Phase 0 first ([phase-0-setup.md § Minimal Phase 0 for `--only`](phase-0-setup.md#minimal-phase-0-for---only)). If unset, STOP.

---

## Step 6.1: Run Comprehensive Review

Invoke `/comprehensive-review:full-review`. It orchestrates specialist agents across dimensions — Phase 6 supplies context and captures output.

**Inputs to pass**:

- Diff: `git diff <base_branch>..HEAD`
- Scope (XS/S/M/L/XL), affected layers, security classification, feature flag status (from state.json / spec.md / plan.md)
- Depth signal (see table below)
- Dimension emphasis notes (below) — longshot-specific severity calibration

### Scope → Depth Signal

| Scope | Depth | Dimensions emphasized |
|-------|-------|------------------------|
| **XS** | minimal | Code quality + Security only |
| **S** | focused | Code quality + Security; plus one dimension matching the change (a11y if UI, concurrency if async introduced, observability if new endpoint, etc.) |
| **M+** | full | All applicable dimensions |

### Dimension Emphasis Notes

Only include dimensions that apply. These calibrate `comprehensive-review` — not separate steps.

**Accessibility** (webapp changes)
- WCAG 2.1 Level AA is the baseline
- **MUST_FIX**: missing keyboard navigation on interactive elements; missing ARIA on custom controls; missing focus management in modals/drawers; focus loss on `useEffect` cleanup
- **SHOULD_FIX**: contrast ratios on unchanged elements; decorative image alt text
- React-specific: focus restoration on modal close; `aria-live` regions for async updates; custom components with `role` attributes must have keyboard support

**Concurrency & race conditions**
- Go: goroutine leaks, race conditions, mutex usage, channel safety
- React/TS: stale closures in async callbacks; `useEffect` dependency array completeness (all referenced values listed); avoid inline object/array literals as deps (prefer `useMemo`/`useCallback`); state update races in concurrent renders; context cancellation propagation

**Observability** (new endpoints, exported functions, state changes)
- Structured logging with context, error level, and relevant fields
- Metrics emission for new API endpoints (latency, error rate)
- Error messages are user-friendly — no raw stack traces
- WebSocket events documented if real-time features

**Feature flags** (high-risk changes: API, auth, DB migrations)
- Gating verified (if project uses flags)
- Rollback strategy with explicit kill-switch path
- Rollout plan: percentage-based (0% → 10% → 50% → 100%)
- Monitoring metrics identified (error rate, latency, crash reports)
- Rollback trigger: specific thresholds that warrant rollback

**UX edge cases** (webapp changes)
- Empty, loading, and error states
- Responsive behavior across breakpoints
- Consistency with existing design patterns
- Keyboard and touch interaction patterns

**Security** (always runs; depth scales with `security.is_security_issue`)

*Standard depth* (all tickets):
- OWASP Top 10 issues introduced by the change (XSS, injection, broken auth, data exposure)
- New API endpoints: auth/authz consistent with existing endpoints
- Input validation at system boundaries
- Error responses don't expose internal stack traces or system paths
- No sensitive data in logs (PII, tokens, passwords)

*Deep pass when `is_security_issue: true`* — all [rules.md §3](rules.md#3-security-handling) language/test/PR rules apply, plus:
- **Fix effectiveness**: does the fix close the reported attack vector, or only its surface manifestation? Search the codebase for similar patterns; assess whether the fix introduces new attack surface.
- **OWASP verification** (scoped to the vuln type from state.json):
  - XSS: output encoding in all rendering paths; no `dangerouslySetInnerHTML` without explicit sanitization
  - Injection (SQL/command): parameterized queries or allowlist validation everywhere
  - Auth/AuthZ: privilege check applied consistently, not just at entry point
  - Data exposure: sensitive fields not logged, not in error responses, not timing-leaked
- **Info leakage scan**: error messages don't expose the attack vector; log statements don't capture exploit content verbatim
- **Commit log audit** per [rules.md §3.5](rules.md#35-commit-log-audit-phase-6): scan `git log <base_branch>..HEAD --oneline` for forbidden terms; advise squash-rewrite if found

---

## Step 6.2: Catalog Findings

Use the `Write` tool to persist:

1. `<artifact_dir>/findings/phase6/comprehensive-review/<dimension>.md` — raw output, one file per dimension, verbatim
2. `<artifact_dir>/findings/phase6/synthesis.md` — unified finding list (format below), the only file read downstream

```text
<artifact_dir>/findings/phase6/
├── comprehensive-review/
│   ├── architecture.md
│   ├── code-quality.md
│   ├── security.md
│   └── ... (one file per dimension)
├── round-1/
├── round-2/
└── synthesis.md
```

Per [rules.md §7](rules.md#7-swarm-mode-file-ownership--convergence), only `synthesis.md` enters the leader context.

**synthesis.md format** (required):

```text
## Phase 6 Review Synthesis

Verdict: READY | NEEDS_WORK | MAJOR_REVISION
Round: <N>/2
Dimensions run: <list>

### MUST_FIX (<count>)
- [<dimension>] <file:line> — <finding> — fix: <one-line suggestion>
- ...

### SHOULD_FIX (<count>)
- [<dimension>] <file:line> — <finding>
- ...

### NITS (<count>)
- ...
```

---

## Step 6.3: Package Presentation with `/review`

Run `/review` over `synthesis.md` to produce a PR-ready summary: findings ranked by severity, grouped by area, file:line quoted with context, suggested patches inline, PR-body block at the end. `/review` is presentation only — no new findings, no re-analysis.

Use the `Write` tool to save to `<artifact_dir>/findings/phase6/review-report.md`. This artifact feeds the Phase 6 gate and the Phase 7 PR body. Print the absolute path.

---

## Step 6.4: Fix Iteration

Round budget: **2** ([rules.md §4](rules.md#4-retry--escalation-budgets)).

For each round:
1. Fix all MUST_FIX items from `synthesis.md`
2. Archive current findings to `<artifact_dir>/findings/phase6/round-<N>/`
3. Re-run from Step 6.1 (`/comprehensive-review:full-review` picks up the new diff)
4. Regenerate `synthesis.md` and `review-report.md`

After 2 rounds:
- **0 MUST_FIX**: gate passes
- **Non-security MUST_FIX remain**: report in PR body warning, proceed to Phase 7
- **Security MUST_FIX remain**: STOP per [rules.md §3.7](rules.md#37-must_fix-discipline) — security issues do not get the 2-round escape; fix, or escalate to the Security team

---

## Step 6.5: Gate

Present `review-report.md` to the user:

> Review READY. Approve to ship?

SHOULD_FIX items are reported in the PR description but don't block shipping. NITS are captured in findings but usually omitted from the PR body.

In **swarm mode** (default when agent teams available), `/comprehensive-review:full-review` and Phase 6 share the swarm protocol in [rules.md §7](rules.md#7-swarm-mode-file-ownership--convergence).

Update state.json per [rules.md §1.5](rules.md#15-statejson-update-ritual). Record checkpoint commit SHA per [rules.md §1.6](rules.md#16-checkpoint-commits-at-gates).

---
