# Gate Checklists — UX Spec Generation System

**Version 1.2 | Mattermost Information Control & Zero Trust Design Team**

> Every gate that *runs* is a hard stop. No agent advances to Phase N+1 until Phase N's gate is recorded in the Spec State Object. These checklists define what "done" means for each phase.
>
> **Shared vocabularies — severity (P1–P3), classification/impact enum, and the 7-criteria scoring rubric — are defined once in [`conventions.md`](conventions.md). This file references them; it never redefines them.**

---

## Ceremony scales with complexity tier (`meta.complexity_tier`)

The orchestrator enforces only the checklist items **in scope for the active tier**. Each item below carries an **`Applies to:`** marker; if an item omits one, treat it as **`all`**.

| Marker | Enforced on | Meaning |
|---|---|---|
| **`all`** | Tier 1, 2, **and** 3 | Core item — load-bearing at every tier. Never scales away. |
| **`T1–T2`** | Tier 1 and Tier 2 | Standard-rigor item; dropped for Tier 3 incremental specs. |
| **`T1`** | Tier 1 only | Full-spec ceremony (e.g., compliance appendix, persona panel, exhaustive coverage); dropped for Tier 2 and Tier 3. |

**Phase inclusion by tier** (which gates run at all):
- **Tier 1 — Full Spec:** all phases run; every gate is a hard stop with multi-approver sign-off.
- **Tier 2 — Standard Spec:** Phases 1–7 run; every gate is a hard stop.
- **Tier 3 — Incremental Spec:** Phases 3, 4, 7 are the minimum incremental set and always run with hard gates. A phase whose context is fully inherited from the parent spec (`meta.parent_spec_ref` = the parent of record in `meta.related_specs[]`) may be **skipped** — its gate is recorded as `bypassed` with a parent-reference justification (a logged inheritance, not a skipped approval). Tier 3 specs **must** cite the parent spec they extend.

Tier never weakens the non-negotiables: the **intake clarification round (item N.0) is REQUIRED at every tier** wherever the phase runs (only the question count scales — see `clarification-protocol` Round Limits), explicit gate approval is required wherever a gate runs, and the v1.2 two-stage clarification check always applies.

---

## Gate Protocol

**Precondition for every gate — state object + typed audit trail.** A gate can only pass against a real
`specs/<slug>/spec-state.json` (the orchestrator auto-bootstraps or refuses when one is missing — no freeform
runs). Every gate transition writes a **typed** `audit_log[]` event from the closed vocabulary in
`spec-state-object.json::$conventions.audit_event_vocabulary` (`phase_started`, `phase_completed`,
`gate_approved`, `gate_bypassed`, `scope_locked`, `scope_change`, `verify_decision_checkpoint`, …) with a
**real ISO-8601 timestamp**. Synthetic `T00:00:0N` placeholders and timestamp-as-status-string are protocol
violations — a gate validated against a fabricated audit trail is invalid.

**Before surfacing a gate artifact to the designer:**
1. Orchestrator verifies the phase's **intake clarification round** is recorded in `gates.phase_N.intake_clarifications` (per the `clarification-protocol` skill). It applies the **v1.2 two-stage check**: (a) `rounds_completed > 0` OR `bulk_accept_used == true`, AND (b) each resolved item carries `chosen_via ∈ {user_response, accept_recommendations_bulk}` with a non-empty `user_message_ref`. Self-resolved "Recommended" defaults without user evidence are rejected as a protocol violation.
2. Orchestrator runs the checklist validator against the artifact
3. If any REQUIRED item is missing or marked `[TBD]`, the artifact is returned to the Phase Agent for completion
4. The designer only sees complete artifacts

**The intake clarification row appears as item N.0 in every phase's checklist below** (e.g., 1.0, 2.0, 3.0, etc.). It is REQUIRED for all phases.

**To approve a gate:**
```
spec gate approve --phase N --approver [Name] --role [Role]
```

**To bypass a gate (exception only):**
```
spec gate bypass --phase N --approver [Name] --role [Role] --justification "[Written reason]"
```
Bypasses are permanently recorded in the audit log and visible in the spec's Key Decisions table.

---

## Phase 1 Gate — Problem Statement

**Required Approvers:** PM, Security Architect

**Required Approvers (by tier):** Tier 1/2 — PM + Security Architect · Tier 3 — PM (Security Architect only if the addendum touches an access-control/classification surface).

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 1.0 | Phase 1 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_1.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 1.1 | BLUF problem statement present (≤ 3 sentences) | all | REQUIRED | Length check, BLUF format check |
| 1.2 | Problem states operational consequence, not solution | all | REQUIRED | Manual review |
| 1.3 | Affected user roles listed with descriptions | all | REQUIRED | Non-empty array |
| 1.4 | Current workaround documented | all | REQUIRED | Non-empty string |
| 1.5 | Failure mode if unaddressed documented | all | REQUIRED | Non-empty string |
| 1.6 | Compliance risk cited (specific control or regulation) | all | REQUIRED | Contains control ID or regulation reference |
| 1.7 | Out-of-scope adjacent problems listed | T1–T2 | REQUIRED | Non-empty array |
| 1.8 | Clarifying questions generated | all | REQUIRED | ≥ 1 question (count ceiling scales by tier per `clarification-protocol`) |
| 1.9 | Clarifying questions answered by stakeholder | all | REQUIRED | All questions have non-empty responses |
| 1.10 | Assumptions extracted and categorized | T1 | RECOMMENDED | Assumption table present |
| 1.11 | User research notes synthesized (if available) | all | CONDITIONAL | Required if interview data provided |
| 1.12 | Scope locked into state (tier + scope + surface/comparator counts) | all | REQUIRED | `scope_lock.locked == true` with non-null `complexity_tier`, `surface_count`, `comparator_count`; `scope_locked` audit event present |

**Gate Decision Criteria:**
- All in-scope REQUIRED items must be complete (Tier 3 drops the `T1–T2`/`T1` items above)
- PM confirms the problem is worth solving and correctly scoped
- Security Architect confirms compliance risk is accurately stated (Tier 1/2, or Tier 3 access-control addenda)
- **Scope-lock (1.12) is non-negotiable at every tier** — the locked tier/scope/surface/comparator counts are what Phase 3 re-confirms; an unlocked scope is the late-scope-drift failure mode and blocks the gate.
- **Tier 3:** the problem statement must cite `meta.parent_spec_ref` and state only the *delta* from the parent

---

## Phase 2 Gate — Research Brief

**Required Approvers:** PM

> **Tier 3:** Phase 2 is the most common skip. If `meta.parent_spec_ref` already carries equivalent, still-valid research, skip this phase — record a `phase_skipped` event and `bypass` Gate 2 citing the parent's Research Brief. Run Phase 2 only for *new* compliance/competitive surface the addendum introduces.

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 2.0 | Phase 2 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_2.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 2.1 | Relevant compliance controls identified | all | REQUIRED | Non-empty controls array |
| 2.2 | Every control ID has a [SOURCE] citation | all | REQUIRED | No control without source |
| 2.3 | No control IDs flagged [VERIFY] remain unresolved | all | REQUIRED | Zero unresolved [VERIFY] flags |
| 2.4 | UX implication documented per control | all | REQUIRED | Each control has ux_implication field |
| 2.5 | Competitive landscape analyzed (min 3 platforms) | T1–T2 | REQUIRED | Platform count ≥ 3 |
| 2.6 | Patterns to leverage identified | T1–T2 | REQUIRED | Non-empty array |
| 2.7 | Patterns to avoid/adapt for classified environments | all | REQUIRED | Non-empty array |
| 2.8 | Differentiation opportunities documented | T1–T2 | REQUIRED | Non-empty array |
| 2.9 | Research gaps flagged with recommended next steps | T1 | RECOMMENDED | Research gaps section present |
| 2.10 | ATO-critical controls identified separately | T1 | RECOMMENDED | ATO-critical subset documented |

**Gate Decision Criteria:**
- All compliance control IDs verified through web search
- PM confirms research scope is sufficient for PRD generation
- No critical research gaps that would block Phase 3
- **Tier 3 (if Phase 2 runs):** only the new-surface delta is researched; inherited controls are cited from the parent, not re-derived

---

## Phase 3 Gate — PRD

**Required Approvers:** PM, Eng Lead

> **Anchor phase — always runs at every tier** (Tier 3 produces a *PRD delta*: only the requirements the addendum adds/changes, citing the parent for the rest). Security items (3.6, 3.12, 3.13) never scale away — UI-layer threat coverage is load-bearing at every tier.

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 3.0 | Phase 3 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_3.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 3.1 | Executive Summary in BLUF format | all | REQUIRED | BLUF format check |
| 3.2 | User stories present for every identified role | all | REQUIRED | Role coverage check (Tier 3: roles touched by the delta) |
| 3.3 | User stories follow "As a [role]..." format | all | REQUIRED | Format check |
| 3.4 | Functional requirements numbered and grouped by role | all | REQUIRED | Numbered, grouped |
| 3.5 | Every functional requirement is testable | all | REQUIRED | No vague language ("may", "could") |
| 3.6 | Non-functional requirements include security controls | all | REQUIRED | Contains control citations |
| 3.7 | Non-functional requirements include accessibility (508/WCAG) | all | REQUIRED | Accessibility section present |
| 3.8 | Success metrics are quantitative and measurable | all | REQUIRED | No qualitative-only metrics |
| 3.9 | Out of scope list with reasoning for each exclusion | T1–T2 | REQUIRED | Each item has reasoning |
| 3.10 | Dependencies listed with blocker flags | all | REQUIRED | Dependencies section present |
| 3.11 | All [VERIFY WITH PM] items resolved | all | REQUIRED | Zero unresolved [VERIFY] flags |
| 3.12 | Threat model completed — UI-layer risks identified | all | REQUIRED | Threat model section present (Tier 3: scoped to the delta's surface) |
| 3.13 | No unmitigated P1 threats | all | REQUIRED | P1 threat count = 0 or all mitigated |
| 3.14 | Pre-flight review passed | all | REQUIRED | No vague/unmeasurable requirements flagged |
| 3.15 | Internal contradictions resolved | all | REQUIRED | Zero contradictions from pre-flight (incl. against the parent spec for Tier 3) |
| 3.16 | Scope re-confirmed before PRD (Phase-1 lock still accurate, or change logged) | all | REQUIRED | `scope_lock.reconfirmed_at_phase_3 == true`; any change recorded in `scope_lock.changes[]` + a `scope_change` audit event (never a silent rerun) |

**Gate Decision Criteria:**
- PM signs off on scope, user stories, and success metrics
- Eng Lead confirms requirements are implementable and dependencies are manageable
- All P1 threats have documented mitigations
- No vague requirements remain
- **Scope re-confirm (3.16) runs before intake at Phase 3** — if scope changed since Phase 1, it is a deliberate, logged `scope_change` (with a re-run offer when the tier flips), not a silent multi-phase rerun.
- **Tier 3:** the PRD delta is internally consistent with the inherited parent PRD (no contradictions)
- **3.7:** Automated a11y validation is not yet wired. `${CLAUDE_PLUGIN_ROOT}/templates/a11y-manual-checklist.md` is mandatory Tier 1–2 / advisory Tier 3. Specs claim "designed for conformance," never "compliant."

---

## Phase 4 Gate — Solution Direction

**Required Approvers:** Design, PM

> **Anchor phase — always runs at every tier.** Tier 3 may compare a **minimum of 2** approaches (the delta rarely warrants 3–5); Tier 1/2 keep the 3-approach floor.

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 4.0 | Phase 4 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_4.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 4.1 | Distinct solution approaches documented (Tier 1/2: ≥ 3 · Tier 3: ≥ 2) | all | REQUIRED | Approach count ≥ 3 (T1/T2) / ≥ 2 (T3) |
| 4.2 | Each approach describes: UX paradigm, admin experience, end-user experience | all | REQUIRED | Three sections per approach |
| 4.3 | Evaluation matrix completed (the 7 canonical criteria per conventions.md §3 × N approaches, weighted + normalized) | all | REQUIRED | 7 criteria × N; normalized score reported |
| 4.4 | All scores justified with rationale (not just numbers) | all | REQUIRED | Justification per score |
| 4.5 | BLUF recommendation present | all | REQUIRED | Recommendation section present |
| 4.6 | Recommendation justified using the matrix | all | REQUIRED | References matrix scores |
| 4.7 | Top 3 risks of recommended approach with mitigations | T1–T2 | REQUIRED | Risk count ≥ 3 (Tier 3: ≥ 1 P1/P2 risk with mitigation) |
| 4.8 | Trade-offs explicitly stated | all | REQUIRED | Trade-offs section present |
| 4.9 | Recommended approach aligns with Phase 2 compliance constraints | all | REQUIRED | Cross-reference check (Tier 3: against inherited parent research) |
| 4.10 | Mobile/field usability explicitly addressed | all | RECOMMENDED | Mobile criterion scored |
| 4.11 | Carried-forward directions recorded in `gates.phase_4.carried_forward[]` at approval (minimum: the recommended direction) | all | REQUIRED | `gates.phase_4.carried_forward[]` non-empty at approval |

**Gate Decision Criteria:**
- Design confirms recommended approach is sound and achievable in Figma
- PM confirms approach aligns with roadmap priorities and user needs
- No unaddressed compliance constraints

---

## Phase 5 Gate — Wireframe/Flow Approval

**Required Approvers:** PM, Eng Lead

> **Tier 3:** skippable when the addendum reuses the parent spec's flows unchanged — record a `phase_skipped` event and `bypass` Gate 5 citing the parent's flows. If the addendum changes any flow, run Phase 5 scoped to the changed flows only. Security items (5.4, 5.5) never scale away.

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 5.0 | Phase 5 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_5.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 5.0a | Decide-or-fork checkpoint cleared before Phase 5 (no open `[VERIFY WITH PM]` blocker) | all | REQUIRED | Every `open_questions[]` item with `status=="open"` AND `blocker==true` is now `resolved` or `branched` (with `branch_spec_ref`); `verify_decision_checkpoint` audit event + `context.verify_decision_checkpoints[]` record present for `at_phase: 5` |
| 5.1 | All PRD user stories have corresponding flows | all | REQUIRED | Story-to-flow mapping complete (Tier 3: delta stories) |
| 5.2 | Each flow shows: entry point, happy path, exit point | all | REQUIRED | Flow structure check |
| 5.3 | Error paths documented for all flows | all | REQUIRED | Error paths present |
| 5.4 | Security audit completed — no access bypass vectors — verified per carried-forward direction | all | REQUIRED | Security findings = 0 unresolved P1 |
| 5.5 | No flows leak information about restricted resources — verified per carried-forward direction | all | REQUIRED | Information leakage check |
| 5.6 | Navigation patterns consistent with existing Mattermost UX | all | REQUIRED | Nav consistency report clean |
| 5.7 | Mobile flows documented or explicitly marked desktop-only | all | REQUIRED | Mobile coverage check |
| 5.8 | Feedback disposition recorded in the Phase-5 artifact and gate-approval note — one of: (a) real feedback synthesized with source refs; (b) synthetic persona-lens critique labeled [SYNTHETIC — persona-lens, not stakeholder input]; (c) none, with one-line reason. Inferring stakeholder feedback from artifact content alone is prohibited. | T1–T2 | REQUIRED | Disposition (a)/(b)/(c) recorded — never inferred |
| 5.9 | All MUST-FIX feedback items resolved | all | REQUIRED | Zero unresolved MUST-FIX |
| 5.10 | Flow definitions present for EVERY carried-forward direction (generated via flow-generator or designer-provided), rendered per the Mermaid/inline-SVG rule (Tier 3: scoped to the changed flows only) | all | REQUIRED | Flow-definition set present per direction in `gates.phase_4.carried_forward[]` |

**Gate Decision Criteria:**
- The decide-or-fork checkpoint (5.0a) runs *before* Phase 5 intake — a load-bearing `[VERIFY WITH PM]` blocker must be **decided or explicitly branched into a named sibling spec**, never deferred into a silent fork.
- PM confirms flows cover all user stories
- Eng Lead confirms flows are technically feasible
- No unresolved security findings at P1 severity

---

## Phase 6 Gate — Prototype Design Options Review

**Required Approvers:** Design Lead, PM

> **Tier 1:** Phase 6 always runs (option-rich prototyping). **Tier 2:** runs. **Tier 3:** runs only if the addendum needs new prototyping; otherwise skip and `bypass` Gate 6 citing the parent's selected option. When Tier 3 *does* run, option count still equals `gates.phase_4.carried_forward[]` length for that run — one option per surviving direction, never a fixed floor. Build integrity (6.3), no-phantom-components (6.5), and the core state set never scale away.

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 6.0 | Phase 6 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_6.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 6.0a | Decide-or-fork checkpoint cleared before Phase 6 (no open `[VERIFY WITH PM]` blocker) | all | REQUIRED | Every `open_questions[]` item with `status=="open"` AND `blocker==true` is now `resolved` or `branched` (with `branch_spec_ref`); `verify_decision_checkpoint` audit event + `context.verify_decision_checkpoints[]` record present for `at_phase: 6` |
| 6.1 | One design option prototyped per carried-forward direction (count matches gates.phase_4.carried_forward[]; each conceptually distinct) | all | REQUIRED | Option count == carried_forward[] length |
| 6.2 | Each option covers all PRD user story flows | all | REQUIRED | Story-to-option coverage complete (Tier 3: delta flows) |
| 6.3 | All options build (`npm run build` in the sandbox playground passes) | all | REQUIRED | Build exit 0 |
| 6.4 | UI states per screen per option — Tier 1: all 6 (default, populated, loading, error, disabled, empty) · Tier 2/3: at minimum default + error + empty, others where applicable | all | REQUIRED | State coverage check (6 for T1; ≥ 3 core for T2/T3) |
| 6.5 | Only components from the sandbox library used (gaps justified and flagged) | all | REQUIRED | No phantom components; gaps in COMPONENT_GAP list |
| 6.6 | Theme switching works across all themes for all options | T1–T2 | REQUIRED | Theme render check (Tier 3: default theme sufficient) |
| 6.7 | Demo data uses realistic fixtures (not placeholder text) | all | REQUIRED | No lorem/placeholder |
| 6.8 | Option index page created with titles, philosophies, recommended badge | T1–T2 | REQUIRED | Index page present |
| 6.9 | Option comparison matrix completed (the 7 canonical criteria per conventions.md §3, weighted + normalized, scored with rationale) | all | REQUIRED | 7 criteria × N options; justification per score |
| 6.10 | BLUF recommendation stated with justification | all | REQUIRED | Recommendation present |
| 6.11 | Prototype URLs accessible for all options | all | REQUIRED | URLs resolve |
| 6.12 | Stakeholder has reviewed and selected preferred option | all | REQUIRED | `gates.phase_6.selected_option` set |

**Gate Decision:** Design Lead confirms option quality; PM confirms PRD coverage. Selected option recorded in spec state.

> **Note:** Figma design files are NOT required for Phase 6 gate approval. The code prototype is the primary design artifact.

---

## Phase 7 Gate — UX Spec

**Required Approvers (by tier):** Tier 1 — PM, Eng Lead, Security Architect, Mobile Eng (all four) · Tier 2 — PM, Eng Lead (+ Security Architect if the feature touches access control/classification) · Tier 3 — PM (+ the parent spec's approver of record for the changed surface).

> **Anchor phase — always runs at every tier; it IS the deliverable.** The spec template is a *menu, not a checklist* — INCLUDE-WHEN-NEEDED items appear only when the feature warrants them, at any tier. The markers below scale the always-on rigor: Tier 3 can gate-pass with the core sections + folded-in validation (target ~8 sections), Tier 1 carries the full appendix/multi-approver ceremony.

| # | Checklist Item | Applies to | Required | Validator |
|---|---|---|---|---|
| 7.0 | Phase 7 intake clarification round recorded (or bulk-accepted) — question count scales by tier | all | REQUIRED | `gates.phase_7.intake_clarifications.rounds_completed > 0` OR `bulk_accept_used == true` |
| 7.1 | Header block complete (all links, metadata) | all | REQUIRED | All header fields populated |
| 7.2 | Hero image present | T1–T2 | REQUIRED | Image embedded |
| 7.3 | Overview section complete (problem, summary, roles, scope) | all | REQUIRED | All required subsections present (Tier 3: delta scope + parent ref) |
| 7.4 | Terminology section present | INCLUDE WHEN NEEDED | Only if feature introduces new concepts |
| 7.5 | Admin/Configuration UX: settings described with defaults and behavior | all | REQUIRED | Settings documented |
| 7.6 | End-User UX Flows: key behaviors described with mockup references | all | REQUIRED | Flow coverage check |
| 7.7 | UI Component Specifications for novel components | INCLUDE WHEN NEEDED | Only for components not in design system |
| 7.8 | Non-obvious edge cases documented | all | REQUIRED | At least P1 findings addressed |
| 7.9 | All P1 edge case findings resolved | all | REQUIRED | P1 resolved count = P1 total |
| 7.10 | Roles & Permissions documented | INCLUDE WHEN NEEDED | Only for complex permission models; simple permissions noted contextually |
| 7.11 | Accessibility considerations for non-standard interactions | INCLUDE WHEN NEEDED | Only for non-standard interaction patterns |
| 7.12 | Licensing & SKU section populated | T1–T2 | REQUIRED | Section present (Tier 3: only if SKU/licensing changes) |
| 7.13 | Analytics events defined | INCLUDE WHEN NEEDED | Only when PM requests specific tracking |
| 7.14 | Open Questions: all have owner + target date | all | REQUIRED | No ownerless questions |
| 7.15 | No unresolved [TBD] items | all | REQUIRED | TBD count = 0 |
| 7.16 | PRD requirements have coverage (internal validation) | all | REQUIRED | Internal traceability check passed (Tier 3: delta requirements) |
| 7.17 | Compliance appendix | T1 | INCLUDE WHEN NEEDED | Tier 1, or any-tier access-control feature; attach as sub-page |
| 7.18 | Mobile differences or parity noted | all | REQUIRED | Mobile section present |
| 7.19 | Deprecated Explorations section preserves abandoned approaches | T1 | RECOMMENDED | Sub-page if applicable |
| 7.20 | Future Considerations section documents deferred decisions | T1–T2 | RECOMMENDED | Sub-page if applicable |

**Gate Decision Criteria:**
- PM confirms spec addresses PRD requirements (internal traceability check passed)
- Eng Lead confirms spec is implementable and unambiguous
- Security Architect confirms security edge cases addressed (Tier 1, or any-tier access-control/classification feature)
- Mobile Eng confirms mobile behavior is documented (Tier 1; folded into Eng Lead sign-off at Tier 2/3)
- All **in-scope** approvers must sign off — gate remains open until all required-by-tier approvers are recorded

---

## Gate Status Tracking

The Spec State Object tracks gate status in real-time:

```json
{
  "phase_N": {
    "status": "pending | in_review | approved | bypassed",
    "required_approvers": ["Role1", "Role2"],
    "approved_by": [
      { "name": "Jane Doe", "role": "PM", "timestamp": "2026-03-10T14:30:00Z" }
    ],
    "bypass": {
      "bypassed_by": null,
      "justification": null,
      "timestamp": null
    }
  }
}
```

---

**Document ends. Version 1.2** — adds the self-tracking / scope-discipline gates: a state-object + typed-audit-trail precondition on the Gate Protocol; scope-lock (1.12) at Phase 1 re-confirmed before Phase 3 (3.16) with any change logged as a `scope_change`; and the decide-or-fork checkpoint (5.0a / 6.0a) that forbids advancing past a load-bearing open `[VERIFY WITH PM]` blocker without a recorded decision or a named sibling-spec branch. All carry `Applies to: all` — these are decision-integrity guarantees that never scale away. **Version 1.1** added the `Applies to:` tier marker (`all` / `T1–T2` / `T1`) on every item and per-phase tier framing, so Tier 2/3 gates are lighter than Tier 1. Phase inclusion, intake question count, and gate rigor scale with `meta.complexity_tier`; the intake round, explicit gate approval where a gate runs, and the v1.2 two-stage clarification check remain mandatory at all tiers.
