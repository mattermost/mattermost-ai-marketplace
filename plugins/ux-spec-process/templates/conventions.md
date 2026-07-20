# UX-Spec Tooling — Canonical Conventions

Single source of truth for the shared vocabularies every agent and skill must use. When any agent or skill needs a **severity level**, a **classification/impact level**, or a **scoring rubric**, it references THIS file — it does not redefine them locally.

---

## 1. Severity scale (findings, threats, edge cases, feedback)

One scale everywhere. Use **P1 / P2 / P3** for any finding's severity — security gaps, edge cases, flow issues, review findings, threat severity, and stakeholder-feedback priority.

| Level | Meaning | Gate effect |
|---|---|---|
| **P1** | Blocker — breaks the mission, leaks data, violates a DoD control, or has no effective mitigation. | Must be resolved/mitigated before the gate passes. |
| **P2** | Should-fix — real degradation of usability/security/coverage, but a workaround exists. | Resolve, or explicitly defer with recorded rationale. |
| **P3** | Nice-to-have — polish, edge refinement, minor inconsistency. | Track; non-blocking. |

Human-facing synonyms (display labels only, never separate scales): **P1 = MUST-FIX, P2 = SHOULD-FIX, P3 = NICE-TO-HAVE**. Do **not** introduce Critical/High/Medium/Low or P0 — map any such inputs onto P1/P2/P3.

---

## 2. Classification / impact level (`meta.mission_tier`)

One enum everywhere for `meta.mission_tier` and any per-item impact classification:

```
IL2 | IL4 | IL5 | IL6 | UNCLASSIFIED | MIXED
```

- Default for new specs: **IL5**.
- **MIXED** = the artifact spans multiple impact levels (e.g., a cross-domain feature).
- Do **not** use `UNCLASSIFIED/CONFIDENTIAL/SECRET/TOP_SECRET` as a tier enum, and do **not** overload P0–P3 to mean impact level.
- (A feature's in-product per-message *data classification* labels are a separate product concept — not this field.)

---

## 3. Solution / option scoring rubric (Phase 4 **and** Phase 6)

Phase 4 (`solution-scorer`) and Phase 6 (`option-presenter`) use the **same 7 weighted criteria**, so a Phase-4 direction and its Phase-6 options are directly comparable.

**Score each criterion 1–5** (5 = best) with a one-sentence, evidence-based justification that cites a PRD requirement, a control, or a threat.

| # | Criterion | 1 ⟶ 5 |
|---|---|---|
| 1 | **Compliance Coverage** | fails NIST/DoD controls ⟶ exceeds them |
| 2 | **Admin Cognitive Load** | very high admin burden ⟶ low burden |
| 3 | **End-User Cognitive Load** | high operator overhead ⟶ intuitive |
| 4 | **Misconfiguration Risk** | trivially misconfigured ⟶ hard to misconfigure |
| 5 | **Engineering Complexity** | very high effort ⟶ simple to build |
| 6 | **Extensibility** | dead end ⟶ strong foundation for later phases |
| 7 | **Mobile / Field Usability** | breaks in low-bandwidth/field ⟶ optimized for tactical use |

**Default weights by tier** (override only with a stated rationale, recorded in `solution_direction.evaluation_matrix`):

| Criterion | IL5 / IL6 | IL4 / UNCLASSIFIED |
|---|---|---|
| Compliance Coverage | 2.00 | 1.50 |
| Misconfiguration Risk | 1.75 | 1.25 |
| Mobile / Field Usability | 1.50 | 1.25 |
| End-User Cognitive Load | 1.25 | 1.25 |
| Admin Cognitive Load | 1.00 | 1.00 |
| Extensibility | 1.00 | 1.00 |
| Engineering Complexity | 0.75 | 1.00 |
| **Σ weights** | **9.25** | **8.25** |

- **Weighted score** = Σ(score × weight).
- **Normalized score (always report this)** = Σ(score × weight) ÷ Σ(weights), on a **0–5** scale → report as `X.XX / 5.00`. Never report a raw weighted sum against "/5".
- Score **3–5 approaches** (Phase 4) — schemas must allow up to 5. Score **one option per carried-forward direction** (Phase 6; count = `gates.phase_4.carried_forward[]` length) — schemas must not cap this at a fixed range.
- **Anti-gaming:** a single P1 compliance/security failure outweighs several cosmetic wins. Call it out and recommend RECONSIDER even when the number looks high.
- **Tie-break:** if two are within 0.20 normalized, recommend the simpler one (higher Engineering Complexity score).

---

## 4. Gate vocabulary

- Gate status enum (`gates.phase_N.status`): `pending | in_review | approved | bypassed`.
- Gate pass/fail criteria live **only** in [`gate-checklists.md`](gate-checklists.md).
- Approver lists live in `gate-checklists.md` and the state object, kept identical.
- Intake enforcement is the `clarification-protocol` v1.2 two-stage check (round exists **and** each resolved item carries `chosen_via` + `user_message_ref`).

---

## 5. Self-resolving references (artifact readability)

Never cite a bare internal code that forces the reader to look it up elsewhere. Every reference to a requirement, edge case, threat, or control ID must carry its meaning at the point of use.

- **Inline gloss (default):** write `FR-10 (admins bulk-assign attributes by policy)`, not `FR-10`. Same for edge cases, threats, and controls: `EC-21 (offline token expiry mid-mission)`, `AC-2 (account management)`.
- **Stable IDs across phases:** a requirement keeps the same ID from PRD → flow → spec, so any citation resolves to a single definition. Assign IDs once (in the PRD) and reuse them downstream.
- **In HTML artifacts:** render the ID as a hover/expand that reveals the full text (the `html-spec-renderer` surface does this); the markdown still carries the inline gloss so it reads correctly without the HTML.
- **Rule of thumb:** a reader skimming one section should never have to scroll to a glossary or open another file to understand a cited code.

---

## 6. Two-layer outputs (skim + deep)

Every phase artifact opens with a **skim layer** (the `artifact-frontmatter` block: TL;DR, phase + tier, what changed since the last version, decisions locked, open `[VERIFY WITH PM]` items, a one-line reading guide) so a reader gets the gist in under a minute. The detailed body follows for anyone who needs to dive in. Default to the skim layer; never make the reader parse the whole body to find the decision.
