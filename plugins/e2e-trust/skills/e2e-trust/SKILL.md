---
name: e2e-trust
description: >-
  Raise confidence that end-to-end tests actually catch regressions, using
  mechanisms that fit E2E economics (mutation testing does NOT — see below).
  Maps a diff to the user flows it changes and the specs that cover them, gates
  on flake rate with a root-cause requirement, optionally seeds a few realistic
  defects and measures the suite's catch-rate, and lints specs for empty or
  mock-only assertions. Framework-aware for Playwright (web/desktop) and Detox
  (mobile). Use when the user invokes /e2e-trust:e2e-trust, or asks to check E2E
  coverage of a change, find flaky E2E tests, prove E2E tests catch bugs, or
  assess whether an E2E suite is trustworthy.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob, Edit, Write
---

# E2E Trust

E2E suites fail differently from unit suites: they don't lack coverage numbers,
they lack *trust* — flaky specs that pass on retry, specs that navigate but
assert nothing, and changed flows with no spec at all. This skill attacks those
directly.

## Why not mutation testing here (read once)

Mutation testing proves unit tests are meaningful by mutating source and checking
a test fails. **That does not scale to E2E.** Mutation cost = (#mutants) ×
(suite runtime per mutant); an E2E spec run is minutes and each mutant would
require rebuilding and redeploying the whole app. Hundreds of mutants × minutes
= days per diff. Stryker/gremlins target fast unit runners, not Playwright or
Detox. So this skill uses **cheaper, E2E-appropriate** signals instead. If the
user asks to "mutation test the E2E suite," explain this and steer them to the
modes below — and to a real mutation engine (gremlins for Go, Stryker for
Jest/Vitest) for the unit layer, which is outside this skill's scope.

## Detect the framework first

Do not assume. Detect from config files at the target path / repo root:

| Signal | Framework | Run command shape |
|--------|-----------|-------------------|
| `playwright.config.{ts,js}` | Playwright | `npx playwright test <spec> --grep <title>` |
| `.detoxrc.json` / `detox` in package.json | Detox | `detox test -c <config> <spec>` |
| `cypress.config.{ts,js}` | Cypress (legacy) | `npx cypress run --spec <spec>` |

Mattermost mapping (verified): web E2E = Playwright (`e2e-tests/playwright`) +
Cypress (legacy); mobile = Detox (`mattermost-mobile/detox`); desktop =
Playwright (`desktop/e2e`). Unit/component layers are Jest — out of scope here;
say so rather than reporting unit-layer gaps.

## Invocation

```text
/e2e-trust:e2e-trust                       # coverage map + assertion lint for the working diff
/e2e-trust:e2e-trust --base=main           # diff against an explicit base ref
/e2e-trust:e2e-trust --flake-runs=5        # also run affected specs N times and gate on flake rate
/e2e-trust:e2e-trust --seed                # also run defect seeding (needs a seed manifest, see Mode C)
/e2e-trust:e2e-trust --pr-summary          # emit ONLY the trimmed PR-comment block (see PR summary output)
/e2e-trust:e2e-trust e2e-tests/playwright  # restrict to a path
```

Default (no flags) runs only the **cheap, non-executing** modes A and D. Modes
B (flake) and C (seed) execute suites and cost real minutes — run them only when
asked.

## Two finding types: BUG and GAP — keep them in separate lanes

While reading the diff to build the coverage map you will notice two very
different things. Do not blend them:

- **BUG** — a likely *defect in the product code itself*, spotted in the diff
  (wrong query/variable, a stale helper the change breaks, a guard that no longer
  fires, an off-by-one boundary). This is the highest-value output. Report it as
  a **code-review finding**, not a test gap: what's wrong, the `file:line`, why
  it's wrong, and what an existing test it may break. A BUG does not get "add a
  spec" as its fix — it gets "fix the code," optionally plus a regression test.
- **GAP** — the product code looks correct but **no E2E spec exercises the
  changed flow**, so a future regression would ship green. This gets a proposed
  spec.

Lead every report with any BUGs (there are usually zero or one; when there is
one it matters more than all the gaps). Then the gaps. If you find no bug, say so
explicitly — don't invent one, and don't dress a gap up as a bug.

## Mode A — Diff → flow → spec coverage (default, cheap)

1. Compute changed product files from the diff (`git diff --name-only "$BASE"...HEAD`),
   excluding the E2E specs themselves.
2. Infer the **user flows / routes / UI surfaces** those files affect. Use route
   definitions, component names, `data-testid`s, and API endpoints as the join
   keys — grep the spec tree for those keys.
3. For each changed flow, report whether ≥1 spec exercises it.
4. **Runnability check (do this for every proposed spec — a gap you can't write
   is not write-ready).** Before you claim a gap is fillable, confirm the harness
   the spec would need actually exists in the repo. Concretely verify:
   - The `testID`/selector the spec targets **exists in the diff or the code**
     (grep for it) — never propose a spec against a selector you haven't seen.
   - The setup helpers it needs exist in the support tree (e.g. an
     `apiCreatePost` props bag, a feature-flag/license patch helper, a
     cold-start `launchApp({url})` path, a calls-join helper). Grep
     `detox/e2e/support` or the Playwright fixtures.
   - **Cite helper/fixture names only with grep evidence — this is where the
     skill fails.** DOM `data-testid`s/ids are greppable straight from the diff
     and safe to name. Support-tree *helper method names* are NOT — do not write
     `sidebarRight.postMessageReplyInRHS()` from memory. Grep the support file,
     paste the real `file:line`, and use the exact identifier. If you can't
     confirm the exact name, write "a helper like this exists in
     `<file>` — confirm the exact identifier" rather than inventing one. A
     fabricated helper name makes the whole suggestion untrustworthy.
   - Classify each gap as **write-ready** (harness exists) or **infra-required**
     (name the missing piece). An infra-required gap is still a valid signal —
     just don't imply it can be written today.

```markdown
## E2E Coverage Map
| Changed flow / surface | Source touched | Covered? | Runnable? | Gap / proposed spec |
|------------------------|----------------|----------|-----------|---------------------|
| Channel switcher (Ctrl+K) | webapp/.../quick_switch.tsx | ✅ quick_switcher.spec.ts | — | — |
| Scheduled posts modal | webapp/.../scheduled_post.tsx | ❌ none | write-ready (testID `scheduled_post_create` exists) | Open modal, schedule, assert row appears in Scheduled tab |
| Cold-start deep link | app/init/launch.ts | ❌ none | infra-required — no `launchApp({url})` harness in support tree | Gap real; needs a launch-with-URL helper first |
```

Rank gaps by risk — feed `qa-analysis` on the same diff to prioritize which
missing specs matter. Do **not** auto-generate specs here; report the gap and a
concrete one-line approach.

## Mode B — Flake-rate gate (`--flake-runs=N`, executes)

Flakiness is E2E's most expensive failure mode. For each spec covering a changed
flow, run it N times (default 5) and compute pass rate.

```bash
# Playwright supports repetition natively:
npx playwright test <spec> --repeat-each=5 --retries=0
# Detox: loop the invocation N times with retries disabled.
```

- **Retries MUST be disabled** during measurement — retries hide flakiness, they
  don't measure it.
- Classify: `stable` (N/N pass), `flaky` (1..N-1), `broken` (0/N).

**Root cause is mandatory — never mask (hard rule).** A flaky spec is exposing a
real race, a real timing bug, or a real product defect until proven otherwise.
You may NOT "fix" flake by adding `waitForTimeout`/sleeps, blind retries,
loosened assertions, or `test.skip`. For each flaky spec:

1. Diagnose the mechanism (race on async data, animation/timing, shared state /
   test-order dependence, real intermittent product bug).
2. Fix the mechanism — a proper `await expect(...).toBeVisible()` / web-first
   assertion / deterministic wait on the real condition, or a product fix.
3. Only quarantine (tag + tracked issue) when you have written down the root
   cause and it is genuinely external non-determinism. Silent quarantine is
   forbidden.

```markdown
## Flake Gate (5 runs each, retries off)
| Spec | Pass rate | Verdict | Root cause | Action |
|------|-----------|---------|-----------|--------|
| quick_switcher.spec.ts | 5/5 | stable | — | — |
| scheduled_post.spec.ts | 3/5 | flaky | asserts before the POST resolves; no wait on the row | replace fixed wait with `await expect(row).toBeVisible()` |
```

## Mode C — Defect seeding / bebugging (`--seed`, executes, opt-in)

The affordable analog of mutation testing: instead of hundreds of syntactic
mutants, seed a **handful of realistic defects** and measure the suite's
catch-rate. This is the only mode that *proves* specs catch bugs.

Requires a **seed manifest** (`e2e-trust.seeds.json` or user-provided) — each
seed is a small, revertible fault tied to a changed flow, e.g. a feature-flag
flip, a one-line patch behind a guard, or a mocked-broken API response. Do not
invent destructive seeds; use the manifest or ask the user to define seeds.

For each seed: apply it → run the specs for that flow → expect them to go **red**
→ revert the seed (always revert, even on error). A seed that stays green is a
proven gap in the specs for that flow.

```markdown
## Defect Seeding (catch-rate)
| Seed (realistic fault) | Flow | Specs went red? | Result |
|------------------------|------|-----------------|--------|
| Disable send-button enable-on-input | Message compose | ✅ | caught |
| Return 200 with empty body on /scheduled_posts | Scheduled posts | ❌ | GAP — no spec asserts the list renders |
```

**Catch-rate = caught / total seeds.** Report it; never leave a seed applied.

## Mode D — Assertion-quality lint (default, static, no execution)

Statically flag specs that create false confidence. This overlaps the
`test-evaluator` plugin's Playwright heuristics — run this for a fast pass, and
`test-evaluator` for a deeper review.

Flag:
- Specs that navigate/click but have **no assertion** on resulting state.
- `page.route('**/*', ...)` or blanket network mocking that defeats end-to-end.
- Specs that finish suspiciously fast (never wait for real data/side effects).
- Assertions only on presence (`toBeVisible`) where state/content matters.

```markdown
## Assertion Lint
| Spec | Issue | Fix |
|------|-------|-----|
| onboarding.spec.ts | Clicks through 4 screens, asserts nothing | Assert the landing state after finish (channel visible, welcome post present) |
| search.spec.ts | Mocks all of /api/v4 via page.route | Let real requests flow; assert on real results |
```

## PR summary output — the trimmed block a reviewer actually reads

The full tables above are your working notes. What lands on a PR must be short,
skimmable, and lead with the one thing that matters — otherwise developers
ignore it. When invoked with `--pr-summary` (or whenever the output is destined
for a PR comment), emit **only** this block. Rules for it:

- **≤ ~15 lines.** One screenful. No full coverage table, no assertion-lint
  table — just the verdict, the bug (if any), and the top 1–3 gaps.
- **Lead with the BUG** if there is one. If there isn't, don't manufacture one.
- Each gap is **one line**: flow → `write-ready`/`infra-required` → the single
  assertion that would catch the regression. Skip low-value gaps entirely.
- Say what's **already well covered** in one line, so the author sees you
  checked rather than pattern-matched.
- Never pad to look thorough. A PR with solid coverage should get a two-line
  "looks well covered, one minor gap" — and that honesty is what earns trust.

```markdown
**e2e-trust** · Detox · 2 files touch user flows

🐞 **Likely bug** — `recent_mentions/index.ts:129` counts logged-in *servers*, not
*teams* on this server; a single-server/multi-team user gets the wrong behavior
and it contradicts spec `MM-T4909`. Fix the query before adding tests.

**Coverage gaps**
- Weekly-recurring toggle → *write-ready* (testID `scheduled_post_options.repeat_weekly` exists): schedule with it on, assert `scheduled_post_header.repeats_weekly` shows in the Scheduled tab.
- Toggle hidden when a file is attached → *write-ready*: attach a file, assert the toggle is absent (guards a server-reject rule).

✅ Base scheduled-message flow is already well covered (`create_schedule_message.e2e.ts`, real state assertions).
```

## Hard rules

- **Detect the framework; never assume Playwright vs Detox vs Cypress.**
- **Separate BUG from GAP; lead with the bug.** A likely code defect is a
  code-review finding, not a test gap — and it's the most valuable output.
  Never dress a coverage gap up as a bug to seem sharper.
- **Never propose a spec against a selector/testID you haven't seen** in the diff
  or code, and label every gap `write-ready` or `infra-required` after checking
  the harness exists. A gap that needs missing infra must say so.
- **Never mask flake.** No sleeps, blind retries, loosened assertions, or skips
  to make a spec pass. Root-cause or quarantine-with-a-reason only.
- **Always revert seeds**, including on failure/interruption.
- **Default is cheap.** Only run modes B and C when explicitly asked; warn about
  runtime (minutes per spec × repetitions).
- **Report, don't auto-generate.** Surface coverage gaps with a concrete
  approach; write specs only if the user asks.
- **Earn trust with restraint.** Call well-covered PRs well-covered and unit-layer
  changes unit-layer; a padded report is worse than a two-line one. Numbers must
  be accurate (count cases, not files).
- **This is not mutation testing.** Don't claim mutation-grade guarantees;
  defect seeding is coarse by design.

## Relationship to sibling plugins

- **`qa-analysis`** — PR risk scoring. Use it to prioritize which changed flows
  deserve E2E budget (flake runs and seeds are expensive).
- **`test-evaluator`** — deeper static test-quality review, including Playwright.
  Mode D here is the fast pass; `test-evaluator` is the thorough one.
