# Findings output format

The teamsecure deliverable is a single structured markdown file. No HTML report, no chat
widget, no serve.py.

## File name and location
- **Standalone PR mode:** `security-review-pr-<N>.md` in the current working directory.
- **Standalone diff/file mode:** `security-review-<slug>.md`, where `<slug>` is a short
  descriptor of the change.
- **teamimplement per-phase:** `.planning/phase-{n}/security-review.md`.
- **teamimplement final pass:** `.planning/security-review-final.md`.

## Structure

```markdown
# Security Review — <scope> (<date>)

## Summary
- Scope reviewed: <PR #N / local diff / N files>
- Files reviewed: <count> (backend: <n>, webapp: <n>, other: <n>)
- Findings: <count> confirmed (CRITICAL <n> / HIGH <n> / MEDIUM <n> / LOW <n>), <n> dropped

## Coverage
<the finder's coverage inventory table, after the gate passed>

## Findings
<one block per confirmed finding, highest severity first>

## Dropped Findings (False Positives)
<findings discarded at the critical pass or orchestrator verification, with the reason — kept for educational value and to show what was considered>
```

## Confirmed finding block

```markdown
### [F-00X] Title  —  SEVERITY

**Location:** file:line(s)
**Verdict:** TRUE POSITIVE (or TRUE POSITIVE, adjusted from <reported>)

**What it is:** plain-language explanation.

**Attack example (required for MEDIUM+):**
1. Attacker is <position/privilege>.
2. <step, referencing endpoint/function/action> → <what the code does>.
3. ... (each step traced through actual code)
4. Impact: <concrete outcome>.

**Precondition reachability:** how the vulnerable state is created/mutated and at what privilege.

**Integration boundary / cross-repo:** any seam between new and existing code (or another repo) the finding depends on.

**Remediation:** concrete fix; note any regression risk.

> ⚠️ Confidence note: (only if orchestrator verification introduced doubt but the finding still holds) what was found and why it is still reportable.
```

For LOW / INFO findings, a one-paragraph description with a one-sentence exploitation path
is sufficient — no full attack example required.

## Severity scale
- **CRITICAL** — remote exploit, no auth required, full compromise or mass data breach.
- **HIGH** — low-privilege exploit, significant data exposure or privilege escalation.
- **MEDIUM** — requires specific conditions or chaining, moderate impact.
- **LOW** — limited impact, hard to exploit, defense-in-depth.
- **INFO** — best-practice note, no direct security impact.

## teamimplement remediation handoff
In integrated mode, the structured findings file is the contract handed back to the
implementation engineer (per-phase) or logged as remediation tasks (final pass). Each
confirmed MEDIUM+ finding becomes a remediation item; the phase/loop is not clean until
they are resolved and re-reviewed.
