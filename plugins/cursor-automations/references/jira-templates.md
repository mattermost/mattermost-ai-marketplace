# Jira ticket description templates — `server-flaky-test`

Loaded on demand by §8 / §8b of
`commands/server-flaky-test.md`. Only the escalation paths need these;
the fix-PR path (§7) never reads this file.

All three are passed to `createJiraIssue` as `description` with
`contentFormat: "markdown"`. The surrounding `createJiraIssue` fields
(`projectKey: MM`, `issueTypeName: Task`, labels, priority, assignee
lookup) and the follow-up `addCommentToJiraIssue` @-mention of Maria
Nunez are identical for all three and are specified in §8 step 3.

---

## 1. Default — could not fix with high confidence (§8)

`summary`: `Flaky test: <TEST_NAME> in <package basename>`

```
## Flaky test
- Test: `<TEST_NAME>`
- Package: `<PACKAGE_PATH>`
- File: `<path/to/file_test.go>`

## Reproduction
<exact commands you used and how often it failed, e.g. "5/100 with
`-race -count=100` on master @ <sha>">

## Symptoms
<stack trace excerpt, race report, or assertion diff. Include 10–30 lines
max; link to a gist if longer.>

## Hypotheses considered
<bullet list of root causes you ruled in/out and why. Cite file:line.>

## Why no PR
<e.g. "Root cause appears to be in production code (Hub.Broadcast races
with Hub.Unregister); a tests-only fix would mask it.">

## Last meaningful author
<short-sha> by <name> <email> (GitHub: <login>) — <commit subject>
<!-- Plain text, no @-mention. GitHub handles in Jira would not trigger
     a GitHub notification anyway, but kept consistent with the PR
     rule: never @-mention an unverified-org-member original author. -->

## Environment
- Branch: master @ <sha>
- Go: <go version>
- OS: <uname -a one-liner>

---
cc @marianunez (requester of the automated investigation)
```

---

## 2. Prior fix insufficient (§2 escalation only)

Use **only** when a merged **Fix flaky** PR (`<EXISTING_PR_KIND>` = `fix`)
is an ancestor of the branch under test and the flake still reproduces.
Never use it for a merged **Skip flaky** PR — those stay on the
already-addressed path. The goal is a **holistic human review**, not
another incremental tests-only patch.

`summary`: `Flaky test: <TEST_NAME> in <package basename>`

```
## Flaky test
- Test: `<TEST_NAME>`
- Package: `<PACKAGE_PATH>`
- File: `<path/to/file_test.go>`

## Prior automated fix (insufficient)
- Previous fix PR: <EXISTING_PR_URL> (merged)
- Merge commit: `<MERGE_SHA>`
- Outcome: flake still reported after the fix landed in the branch
  under test (`git merge-base --is-ancestor` confirmed present).

## Why human review
Automated remediation already attempted a tests-only fix for this
exact test and it did not resolve the flakiness. A second automated
fix attempt is likely to stack band-aids rather than address the
root cause. This ticket requests a **holistic review** — the
assignee should investigate whether the issue requires production
code changes, test architecture changes, or a different testing
strategy altogether.

## Reproduction
<If you ran any repro before escalating, include commands and
failure rate. Otherwise note "Escalated from §2 without a fresh
repro ladder — prior merged fix already establishes the flake is
active on this branch.">

## Symptoms
<Stack trace / race report from the triggering CI run or prior
investigation, if available.>

## Hypotheses considered
- Prior tests-only fix (<EXISTING_PR_URL>) was merged but did not
  resolve the flake — root cause may be deeper than what a
  targeted test patch can address.
<Add any additional hypotheses from reading the test and the prior
fix diff.>

## Why no PR
Prior automation fix was insufficient; escalating for human review
rather than attempting a second automated fix.

## Last meaningful author
<short-sha> by <name> <email> (GitHub: <login>) — <commit subject>

## Environment
- Branch: master @ <sha>
- Go: <go version>
- OS: <uname -a one-liner>

---
cc @marianunez (requester of the automated investigation)
```

---

## 3. Test seam — the honest fix is a production change (§8b)

Use when production code exposes no injection seam, so the test can only
exercise the path by mutating a package-level global (§5 pattern 14,
§6 tier 2).

`summary`: `Flaky test: <TEST_NAME> in <package basename> (needs test seam)`

```
## Flaky test
- Test: `<TEST_NAME>`
- Package: `<PACKAGE_PATH>`
- File: `<path/to/file_test.go>`

## Root cause
`<production symbol>` reads package-level `<var(s)>` directly, so a
test can only exercise `<scenario>` by overwriting process-global
state and restoring it with `defer`. That shared mutable state is
the flake — <one or two sentences tying it to the observed failure,
citing file:line>.

## Reproduction
<exact commands and failure rate, e.g. "3/100 with `-race -count=100`
on master @ <sha>">, plus the failing output.

## Symptoms
<stack trace excerpt, race report, or assertion diff — 10–30 lines.>

## Proposed fix (test seam)
<Concrete design, not a vague suggestion:>
- Move `<var(s)>` onto `<type>` as fields.
- Add `New<Type>()` seeded from the current package-level values;
  call it from `init()` and `<existing reset helper>`.
- Update the <N> existing call sites: <list them>.
- Tests then construct an isolated instance and never touch globals —
  include a 5–15 line Go sketch of the resulting test setup, fenced as
  a `go` code block in the ticket description.
- Blast radius: <files touched, whether behavior changes (it should
  not), and anything signature/API-visible>.
- Prototype status: <"prototyped locally: builds, gofmt-clean, passes
  50x under -race -parallel=32" — only if you actually ran it;
  otherwise "not prototyped">.

## Alternatives rejected
- <Higher/lower tier options and why. Explicitly state that locking
  the global was rejected: it serializes access without removing the
  shared state, and §4a showed <no concurrent access | the race is
  incidental>.>

## Why no PR
The fix requires a production change (`<production file>`), which is
outside this automation's tests-only contract. A skip PR is opened to
unblock CI; this ticket tracks the seam work.

## Last meaningful author
<short-sha> by <name> <email> (GitHub: <login>) — <commit subject>

## Environment
- Branch: master @ <sha>
- Go: <go version>
- OS: <uname -a one-liner>

---
cc @marianunez (requester of the automated investigation)
```
