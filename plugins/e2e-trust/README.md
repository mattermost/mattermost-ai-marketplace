# e2e-trust

**Raise trust in end-to-end suites where mutation testing doesn't fit.**

Unit tests have mutation testing — mutate the source, prove a test fails. That
doesn't scale to E2E: rebuilding the app per mutant across hundreds of specs
would take days per diff. E2E suites also fail differently —
their problem isn't a missing coverage number, it's **trust**: flaky specs that
pass on retry, specs that click through a flow and assert nothing, and changed
flows with no spec at all. `e2e-trust` attacks those directly.

## Framework-aware

Detects and supports **Playwright** (Mattermost web + desktop) and **Detox**
(mattermost-mobile), with legacy **Cypress** recognized. It never assumes the
framework — it reads the config.

## Four modes

| Mode | Cost | What it does |
|------|------|--------------|
| **A. Coverage map** (default) | cheap, no run | Maps the diff → changed user flows → which specs cover them → gaps |
| **B. Flake gate** (`--flake-runs=N`) | runs specs N× | Measures flake rate with retries **off**; requires root cause, never masks |
| **C. Defect seeding** (`--seed`) | runs specs | Seeds a few realistic faults, checks the specs go red, reports catch-rate — the affordable analog of mutation testing |
| **D. Assertion lint** (default) | static | Flags specs that navigate but assert nothing, or mock the whole network |

## Usage

```text
/e2e-trust:e2e-trust                       # coverage map + assertion lint for the working diff
/e2e-trust:e2e-trust --base=main           # diff against an explicit base ref
/e2e-trust:e2e-trust --flake-runs=5        # add the flake-rate gate
/e2e-trust:e2e-trust --seed                # add defect seeding (needs a seed manifest)
/e2e-trust:e2e-trust e2e-tests/playwright  # restrict to a path
```

Default runs only the cheap, non-executing modes. `--flake-runs` and `--seed`
execute suites and cost real minutes — opt into them deliberately.

## Principles

- **Never mask flake.** No sleeps, blind retries, loosened assertions, or skips
  to force a green. A flaky spec is a real race or bug until proven otherwise —
  root-cause it, or quarantine it with a written reason and a tracked issue.
- **Always revert seeds**, including on error.
- **Report, don't auto-generate.** Coverage gaps come with a concrete approach;
  specs are written only when you ask.
- **Not mutation testing.** Defect seeding is coarse by design; it doesn't claim
  mutation-grade guarantees.

## Companion plugins

Pair with [`qa-analysis`](../qa-analysis/) (prioritize which flows deserve the
expensive E2E budget) and [`test-evaluator`](../test-evaluator/) (deep static
review). For the unit layer, use a real mutation engine directly — gremlins for
Go, Stryker for Jest/Vitest.
