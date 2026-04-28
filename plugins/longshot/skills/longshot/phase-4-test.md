# Phase 4: Test

**Goal**: Comprehensive test coverage, all green.

Follow one of these TDD skills (first available wins):
- **`/tdd-workflows:tdd-cycle`** — full red/green/refactor cycle orchestration
- **`superpowers:test-driven-development`** — TDD discipline for any feature/bugfix

If none are installed, proceed inline with the steps below.

### Step 4.0: Reproduction Verification (bugs only)

If a reproduction test was written in Phase 1 (Step 1.0.2.5 or 1.2.5), verify the fix by running it:
1. Check `<artifact_dir>/repro/` for a failing test from Phase 1
2. Run it — it should now PASS (the fix from Phase 3 should resolve it)
3. If it still fails: the fix didn't address the root cause. STOP and report before writing more tests.
4. Move the repro test into the project's test directory (it becomes the regression test for this bug)

If no repro test exists but the ticket is a bug: write one now based on the ticket's steps to reproduce, then verify it passes.

**Layer choice for the repro test**: match the layer where the bug manifests, not where the fix happens. If the ticket says "user sees wrong X in modal/list/toast/timestamp/count", the repro test is E2E — the fix may be a one-line selector/dispatch change, but a unit test of that change does not reproduce the user-facing bug. Route accordingly through Step 4.3's decision gate.

### Step 4.1: Analyze Code Under Test
Read `<artifact_dir>/plan.md`, specifically the `## Test Plan` section, as the test specification. Also read implementation code to identify functions, public API, edge cases, and mocking needs.

Use the Test Plan's `### Regression Tests` list to identify related features that need regression verification. Run existing tests for those features before writing new tests.

### Step 4.2: Write Unit Tests

**Decision gate — unit tests are REQUIRED unless all three are true**:
1. No new logic and no modified branches were introduced (pure rename, comment-only, type-only refactor, dependency bump with no behavior delta).
2. Every modified branch is fully exercised by integration or E2E tests in the same PR, with assertions on the specific input→output relation — not just "it didn't crash" or "the action was dispatched."
3. The functions under test have no edge cases worth pinning: no nil / empty / zero handling, no permission / auth / security boundary, no error path, no boundary condition, and no semantically-significant default value (e.g. Go zero values like `TeamID == ""` that mean "DM/GM" rather than "unset").

If any answer is **no**, unit coverage is required. Write it.

**Required scope when unit tests are required** — every one of the following gets a test:
- **Each new or modified branch** of the changed code, including the "did not enter the branch" path.
- **Every error path** — explicit error returns, panics-converted-to-errors, validation rejections.
- **Every permission / auth / security boundary** — allow path AND deny path. These are not optional, because E2E rarely exercises the deny path comprehensively.
- **Edge values** — nil, empty string, empty slice, zero, max, "" vs not-set, type-defaulted fields with semantic meaning.
- **Each public function whose contract changed** — even if the change was "now also handles X", pin the new contract.

**Dodges to refuse** (these are not reasons to skip):
- *"It's covered by E2E."* — E2E proves the wired-up happy path works. Unit tests pin the contract for each branch — particularly security/permission/error paths E2E can't reach efficiently. A DM/GM permission check that bypasses `canViewTeam` when `TeamID == ""` needs a unit test for both the allowed AND denied path; an E2E that happens to walk one path is not a substitute.
- *"It's a small change."* — Bug class, not fix size, determines coverage. A one-line guard added to a security-sensitive function still needs both-paths assertion.
- *"It's a private / internal function."* — If it has branches, exercise it through its public caller with the same precision; or, if Go, write a `_test.go` in the same package and call it directly.
- *"It's pure plumbing."* — Plumbing that copies the wrong field, swallows an error, or selects the wrong branch is the most common regression class.
- *"Coverage is already high."* — Line coverage measures lines hit, not assertions made. 100% coverage with `require.NoError(err)` and no return-value assertion is worse than 80% with strong assertions.
- *"We have integration tests."* — Integration tests prove components compose; they don't pin individual function contracts.
- *"spec.md said no new tests."* — Same rebuttal as 4.3: scope was set before the bug was fully understood. If new code paths exist, pin them.
- *"N/A"* — Not an acceptable value. Either spell out which of the three exemption criteria applies with a concrete one-sentence justification, or write the test.

**Match existing patterns** (deviation is a finding):
- Before writing a single test, read **2–3 existing tests** in the same file or package. Copy their structural style — table-driven vs. flat, helper functions, fixture builders, mock setup, assertion library, naming.
- Use the project's existing mock infrastructure (`server/app/mocks/`, `mock_app.go`, `mock_store.go`, generated gomock files, Jest module mocks). **Never hand-roll a new mock** when a generated/maintained one exists. If the existing mock lacks a method you need, regenerate per project convention; do not introduce a parallel mocking system.
- Match the assertion library already in the file: testify/`assert` vs `require`, plain `t.Error*` vs `is.New(t)`, Jest `expect` vs Vitest `expect`. Mixing is a smell.
- Match naming convention. Examples in MM Go code: `TestRunView`, `TestRunView_DMGM_AllowsChannelMember`, table entries `name: "denies non-member of DM"`. Examples in MM webapp: `describe('runView', ...)` + `it('allows channel members in DM channels')`.

**Framework specifics**:
- **Go** — table-driven tests via `for _, tt := range []struct{...}{...}`, subtests via `t.Run(tt.name, ...)`. Use `testify/require` for hard preconditions (setup must succeed) and `testify/assert` for behavior assertions, matching whichever the surrounding file uses. `t.Cleanup()` over deferred teardown when the project uses it. Parallelize with `t.Parallel()` only when there is no package-level shared state. Use the project's existing fixture builders / setup helpers — do not invent new ones for a single test file.
- **JS/TS** — match the existing `describe/it` (or `test`) shape exactly. Mock modules with the same primitive the rest of the file uses (`jest.mock`, `vi.mock`, MSW handler). Use existing factories/builders for fixture data. Reset mocks in the same teardown style (`afterEach`, `beforeEach` reset, etc.).

**Anti-patterns to refuse** (these will be flagged in Phase 6 by `test-coverage-reviewer` and `test-unit-expert`):
- Tests that assert only "the function was called" without checking the inputs passed or the value returned.
- Tests that mock the function under test (you're testing the mock, not the code).
- Tests that copy the implementation's branching logic into the assertion (oracle problem — they pass by reproducing the bug).
- Tests with only happy-path coverage when error/edge paths exist in the diff.
- Tests that pass against the *previous* implementation as well as the new one (always-green tests aren't tests).
- `require.NoError(err)` followed by no assertion on the return value.
- Snapshot tests for anything but stable, intentionally-frozen output (rendered email templates, Markdown→HTML golden files). Don't snapshot React component structure or large objects.
- Skipped (`t.Skip`, `it.skip`, `xit`) or commented-out tests left in the diff.
- Tests that rely on execution order or package-level shared mutable state.
- Console/log noise: tests that produce unexpected stdout/stderr beyond what the test asserts. Treat as a failure, mirroring 4.3's console-error gate.

**Quality bar** — the falsifiability test:
- A meaningful unit test FAILS when a plausible regression is introduced. Before declaring a test done, mentally (or actually) mutate the implementation in one plausible way (flip a comparison, drop a guard, return the wrong field) — does the test catch it? If not, the test is not pinning the contract.
- Each test must be expressible in one sentence: "This test pins that `<function>` `<does specific thing>` when `<specific input condition>`." If you can't say it that way, the test is too broad or too narrow.
- Test names describe **behavior**, not the function being called. `TestRunView_when_TeamID_empty_and_user_is_channel_member_allows_access` beats `TestRunView`. The second tells you nothing when it fails in CI.

**Use domain agents** (per [rules.md §5.1](rules.md#51-agent-fallback)):
- `test-coverage-reviewer` — validates the coverage plan against the diff (every changed branch has a test).
- `test-unit-expert` — unit-test patterns, mock usage, anti-pattern detection.
- For server-side Go code in MM/MM-plugin profiles, also consult `go-backend` for idiomatic patterns and `app-reviewer` / `store-reviewer` / `api-reviewer` for layer-appropriate assertion targets.

**If skipping** (all three exemption criteria pass): write `<artifact_dir>/state.json.phases.4-test.unit_skip_reason` AND a line in the Phase 4 summary stating which of the three criteria applies, with a concrete one-sentence justification. Generic labels ("trivial", "covered elsewhere", "N/A") are rejected — name what regression class would slip through.

### Step 4.3: Write E2E Tests (Playwright preferred, Cypress fallback)

**Decision gate — E2E is REQUIRED unless all three are true**:
1. No user-visible change (backend-only API, internal refactor, pure data migration)
2. No DOM/render behavior involved — no "user sees X", modal/toast/list contents, timestamps, counts, visibility, ordering, or enablement
3. No cross-request/cross-session/cross-tab behavior — no state freshness, realtime updates, cache invalidation, WebSocket-driven UI, or multi-user flows

If any answer is **no**, E2E coverage is required. Write it.

**Dodges to refuse (these are not reasons to skip):**
- *"Unit test proves the action was dispatched / selector returns the right data."* — Dispatching an action does not prove a user sees the result in the DOM. State-freshness, render order, and reactivity bugs only surface through the real UI.
- *"The fix is small."* — Bug class, not fix size, determines coverage. A one-line fix to a user-visible rendering bug still needs a test that exercises the rendering.
- *"spec.md said no new E2E suites."* — That scope was set before the current bug was fully understood. If the bug class now requires E2E, revisit the spec constraint; don't hide behind it.
- *"E2E needs a running server / two sessions / time manipulation."* — That's infrastructure cost, not a principled exemption. Pay it.
- *"N/A"* — Not an acceptable value. Either spell out which of the three criteria applies, or write the test.

**If skipping**: write `<artifact_dir>/state.json.phases.4-test.e2e_skip_reason` AND an explicit line in the Phase 4 summary stating which of the three exemption criteria applies, with a concrete one-sentence justification. Generic labels ("N/A", "backend-only", "covered by unit") are rejected — name what the user would *not* see if this shipped broken.

**Framework selection**: Playwright if `e2e-tests/playwright/` or `@playwright/test` is present, else Cypress if `cypress/` or a `cypress` dep is present. If the gate mandates E2E but neither framework is installed (rare — most projects have one), report and ask the user before skipping.

Use domain agents:
- `e2e-test-writer`: E2E patterns, selectors, page objects
- `e2e-test-reviewer`: convention compliance

Write E2E specs covering the acceptance criteria from Phase 1. For **Playwright**:
- Use page object pattern if project follows it
- Test user flows end-to-end (create, read, update, delete cycles)
- Cover happy path + key error states
- Use `data-testid` selectors (prefer over CSS selectors). Naming convention: `{feature}-{component}-{role}` (e.g., `sidebar-channel-list-item`, `settings-notifications-toggle`). For dynamic lists: add testid to container, use index or data attributes on items.

For **Cypress**:
- **NEVER use `cy.api*` helper methods** (e.g., `cy.apiLogin`, `cy.apiCreateChannel`, `cy.apiCreateUser`) as shortcuts in E2E specs that are testing specific UI flows. These helpers bypass the UI and defeat the purpose of E2E testing.
- `cy.api*` helpers are ONLY acceptable for **setup** (creating precondition data before the test) or **ancillary/triggering flows** (e.g., another user sending a message to trigger a notification you're testing in the UI).
- The flow under test MUST go through the actual UI — click buttons, fill forms, navigate pages.

**Pattern distinction**: For Playwright, use TypeScript class-based page objects with locator methods. For Cypress, use `cypress/support/commands.ts` for reusable selectors — do NOT use page object classes (Cypress's chaining API doesn't suit them).

**No arbitrary timeouts.** Never use hard-coded waits (`cy.wait(5000)`, `page.waitForTimeout(3000)`, `setTimeout`, `sleep`). These are flaky, slow, and mask real issues. Instead:
- **Cypress**: Rely on built-in retry-ability and assertions. Use `cy.get().should()` which auto-retries. For network: use `cy.intercept()` + `cy.wait('@alias')` to wait for specific requests. Ref: https://docs.cypress.io/app/core-concepts/best-practices — see "Unnecessary Waiting" anti-pattern.
- **Playwright**: Use auto-waiting locators (`page.getByRole()`, `page.getByTestId()`), `expect(locator).toBeVisible()`, and `page.waitForResponse()` for network. Playwright locators auto-wait by default — explicit waits signal a test smell. Ref: https://playwright.dev/docs/best-practices — see "Use web-first assertions" and "Don't use manual assertions".

**Console error gate**: Collect `console.error` output during all E2E test runs. Fail if unexpected console errors appear — treat them as test failures requiring investigation. Only errors explicitly expected and asserted by the test are allowed through.

**Feature flag paths**: If the implementation uses a feature flag, E2E tests MUST cover both flag-on and flag-off states. Annotate which spec file and test block covers each state.

When **swarm mode** is available: spawn `test-backend`, `test-frontend`, `test-e2e` in parallel.

### Step 4.4: Run Tests
Execute using profile's test commands:
- Unit: profile-specific (e.g., `make test-server`, `npm test`)
- E2E: `npx playwright test <spec>` or `npx cypress run --spec <spec>`

If failures → Step 4.5.

### Step 4.5: Fix Failures
Retry budget and classification rules live in [rules.md §4](rules.md#4-retry--escalation-budgets) — 3 attempts per error signature, transient-retry once, STOP protocol on exhaustion.

Use `superpowers:systematic-debugging` (or `/incident-response:smart-fix` for code-bug classification) with structured classification:
1. **Classify each failure**:
   - `CODE_BUG`: implementation logic error → spawn `debugger` agent for root cause
   - `TEST_BUG`: test incorrectly written (wrong selector, bad assertion) → fix test directly
   - `SETUP_BUG`: infrastructure issue (DB connection, env var, mock setup) → fix configuration
   - `TRANSIENT`: timing/race/flaky — follow the retry rule in [rules.md §4](rules.md#4-retry--escalation-budgets)
2. For non-transient failures: apply fix, rerun ONLY the failing test(s) — not the full suite
3. On budget exhaustion, emit the standard STOP message per [rules.md §6](rules.md#6-stop-protocol) with `{test_file, error_type, error_signature, attempts, last_error, suggested_fix}`

### Step 4.6: Exploratory Testing

Use Playwright MCP (`mcp__plugin_playwright_playwright__*`) for automated browser validation:

1. `browser_navigate` to the feature
2. `browser_snapshot` for accessibility tree
3. Interact: `browser_click`, `browser_type`, `browser_fill_form`
4. Verify UI state; check `browser_console_messages` for errors
5. `browser_take_screenshot` for PR attachments
6. `browser_network_requests` for failed API calls

Checklist (from acceptance criteria):
- [ ] Feature visible and accessible
- [ ] Happy path works end-to-end
- [ ] Error/empty states render correctly
- [ ] No console errors or failed network requests
- [ ] Responsive behavior (if applicable)

Fallback (no Playwright MCP or no local instance): print the checklist with URLs/actions for manual verification.

Attach screenshots to the Phase 4 summary and Phase 7 PR.

Principle citation: [rules.md §8](rules.md#8-principle-applications) — scripted tests verify code correctness; exploratory verifies feature correctness.

**Gate**: All tests green + exploratory validation passes (or deferred to user). Update state.json per [rules.md §1.5](rules.md#15-statejson-update-ritual).

---
