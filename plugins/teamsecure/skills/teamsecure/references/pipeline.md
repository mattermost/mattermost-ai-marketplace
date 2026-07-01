# teamsecure pipeline (canonical procedure)

This is the single source of truth for how a teamsecure review runs. The `teamsecure`
skill follows it, and `teamimplement`'s security stage cites it. Improve the pipeline
here and both callers inherit the change.

The orchestrator is whoever drives this procedure: the `teamsecure` skill in standalone
mode, or a `teamimplement` lead in integrated mode. The orchestrator spawns the agents
(`security-paranoid-reviewer`, `security-critical-reviewer`), enforces the gates, and owns
Step 5 (verification). The orchestrator does NOT do the first-pass find or the validation.

> **Agents report idle, not results.** A finished finder or validator sends an idle/available
> notification — it does NOT automatically hand you its report. You MUST explicitly request
> each agent's full output by message and wait for it to arrive. An idle agent you have not
> collected from is NOT done. Never treat un-collected results as "no findings" — that is
> silent data loss and defeats the coverage gate.

> **Threat-model scoping (applies to every finding, at the finder, validator, and your
> Step-5 verification).** (1) **System administrators are all-powerful** — a finding only an
> actor with the sysadmin role can reach is OUT OF SCOPE (not a vulnerability). A finding any
> other role (including delegated admin roles like team/channel admin or system manager) can
> reach that exceeds that role's granted permissions IS in scope. (2) **Plugins are a trusted
> component** — do not treat a server-side plugin's own capabilities (or malicious plugin
> code) as an attacker. Bots, webhooks, slash-command integrations, OAuth apps, and external
> content remain untrusted and in scope.

## Step 1 — Resolve scope

Determine the review scope and build the authoritative list of changed files.

- **PR mode (`<PR number>`):** resolve the repo dynamically, never hardcode it:
  ```bash
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  gh pr view <N> --json number,title,body,baseRefName,headRefName,files --repo "$REPO"
  gh pr checkout <N> --repo "$REPO"
  ```
  If the PR does not exist in this repo, stop and report it. Do NOT fall back to another repo.
  The diff command for the agents is `gh pr diff <N> --repo "$REPO"`.
  Note: `gh pr view --json files` caps at 100 files. For large PRs get the full list with
  `gh api repos/$REPO/pulls/<N>/files --paginate --jq '.[].filename'`.
- **Local diff mode (`--diff`):** the change is the uncommitted working tree (used by
  teamimplement, which reviews freshly-implemented code that is not yet a PR). File list:
  `git diff --name-only` (add `--staged` if changes are staged). Diff command: `git diff`.
  If a base ref is provided, use `git diff --name-only <base>...HEAD` and `git diff <base>...HEAD`.
- **File-list mode (`--files ...`):** the scope is exactly the provided files.

Capture the authoritative file list. It is the coverage scope passed to the finder and the
yardstick for the coverage gate. If reviewing a remote PR, ensure the agents can read full
files (check out or clone the PR head) — the methodology requires reading whole files, not
just hunks.

## Step 2 — Paranoid pass

Spawn `security-paranoid-reviewer`. Pass it:
- The scope (PR number / "local diff" / file list) and the exact diff command to use.
- The COMPLETE authoritative file list, verbatim, as the coverage scope: every backend
  (non-test) file must be read in full and assigned a status.
- The PR title and body as PR CONTEXT (PR mode), or a one-line description of the change
  (other modes).

The finder returns a coverage inventory table followed by findings (F-IDs, no severity).
**Collect the report explicitly** (see the idle/results note above): the finder will report
idle without delivering anything — request its full coverage table + findings and wait.

## Step 3 — Coverage gate

Before continuing, validate the finder's coverage against `coverage-inventory.md`:
- The number of files in the coverage table equals the number of files in the authoritative list.
- Every non-test backend file has a `reviewed-no-findings` or `reviewed-with-findings [IDs]`
  status — never "omitted".
- When deciding whether an unlisted file is omittable, match it against the test-file patterns
  enumerated in `coverage-inventory.md` (do not let an unfamiliar test-naming convention such
  as `*.e2e.*` or `*.cl.*` trigger a false gate failure).

If any backend file is missing or unreviewed, send the finder back (re-dispatch / SendMessage)
to complete coverage. **Do not advance with incomplete coverage.** Silence is not coverage.

## Step 3.5 — Reconcile (only if finders ran in parallel)

Skip this step if a single finder produced a single findings list. When multiple finders ran
in parallel (see Parallelism), their outputs WILL overlap at the seams — two finders tracing
the same data flow from opposite ends legitimately report the same vulnerability under
different IDs. Reconcile BEFORE validation:

1. **Cluster by root cause / shared sink, not by ID.** Group findings that point at the same
   file:line, the same data-flow sink, or the same underlying bug. In practice one real issue
   can arrive from 3–4 finders (e.g. an open-redirect flagged from the transport side and the
   markdown side; a recursion DoS flagged by the translation finder and the render finder).
2. **Assign one canonical ID per cluster, preserving the source IDs as aliases** (e.g.
   "C-001 / D-001") so traceability survives into the report.
3. **De-duplicate; do not renumber blindly.** Finders already use distinct prefixes, so the
   risk is not ID collision — it is the same bug fragmented across several IDs. Collapse those.

Hand each *cluster* (not each raw finding) to the critical pass, so every real issue is
validated exactly once. Validating un-reconciled parallel output makes N validators rate N
copies of one bug independently, producing a report with the same finding listed several
times at several severities.

## Step 4 — Critical pass (context isolation)

Spawn `security-critical-reviewer`. Pass it:
- The scope and diff command.
- The COMPLETE findings — the reconciled clusters from Step 3.5 if finders ran in parallel,
  otherwise the single finder's list — verbatim, with all F-IDs/aliases.

Pass the findings ONLY. The validator must NOT receive the finder's reasoning, exploration
steps, or intermediate thoughts. This isolation is intentional and mandatory — it stops the
validator from inheriting the finder's assumptions.

For a large finding set you may run several critical reviewers in parallel, each owning a
disjoint group of clusters; each still receives findings ONLY. Like finders, a validator
reports idle when done and must be asked to deliver its full verdict report — collect every
one before Step 5.

The validator returns, per finding: a verdict (TRUE POSITIVE / TRUE POSITIVE adjusted
severity / FALSE POSITIVE), a severity, an analysis, and — for every MEDIUM+ TRUE
POSITIVE — a concrete code-traced attack example with a precondition-reachability trace.

## Step 5 — Verification (orchestrator, not an agent)

You independently verify every TRUE POSITIVE rated MEDIUM or higher before it ships. This
step is mandatory.

For each MEDIUM+ finding:
1. Re-read the relevant code yourself — go back to the actual files, not the agents' summaries.
2. Re-trace the full execution path and the validator's attack example step by step. For
   each step confirm: the attacker can perform it at their stated privilege, the code path
   executes as described, and no upstream check blocks it.
3. Re-check precondition reachability: can the data that triggers the bug actually be created
   or mutated into the vulnerable state at the required privilege level?
4. Re-check the integration boundary: do the new code and the existing code it touches
   actually agree on who validates/authorizes?
5. Decide:
   - **High confidence:** keep the finding as-is.
   - **Confidence collapsed (likely false positive):** drop it. Record it in the dropped
     section with the reason.
   - **Confidence dropped but still real:** keep it, append a short confidence note
     explaining what introduced doubt and why it is still reportable. Downgrade severity if
     warranted.

LOW / INFO findings do not require this independent re-verification.

## Step 6 — Output

Write the structured findings file per `findings-format.md`. Findings list only — no HTML
report, no chat widget, no serve.py.

In PR mode, output is read-only: never post comments, reviews, approvals, labels, branches,
commits, or trigger workflows. The findings file is the only artifact.

## Parallelism

For large diffs, the orchestrator may spawn multiple `security-paranoid-reviewer` agents
partitioned by file/package (give each a distinct F-ID prefix, e.g. A-, B-, C-). Merge their
coverage tables for the coverage gate (Step 3), then **reconcile their findings in Step 3.5**
before the critical pass — overlap at partition seams is expected, not exceptional. The
critical pass and verification run over the reconciled clusters, and the critical pass itself
may be parallelized across disjoint cluster groups.

Remember: finders and validators report idle when finished; their reports must be explicitly
requested, not awaited passively.
