# Feedback Synthesizer — Worked Example

A full worked example (raw stakeholder feedback in → categorized output) for the `feedback-synthesizer` skill. See `SKILL.md` for the contract; this file is the on-demand reference.

**Input:**
```json
{
  "raw_feedback": "[Security Architect]: 'Section 2 renders the channel name in search results BEFORE the access check. This is a spillage path — a user sees \"Restricted Channel #SCI-X\" even if they lack Need-to-Know. Filter results to accessible channels before display.'\n\n[Compliance Officer]: 'Section 5 doesn't show audit logging. All access-policy changes must be logged per NIST 800-53 AU-2. This is a requirement.'\n\n[PM]: 'Could we add bulk attribute import in this phase? User research showed admins want to load many attributes at once.'\n\n[UX Designer]: 'Help text on the attribute field uses \"ABAC\" without explaining it. Should expand.'\n\n[Accessibility Lead]: 'The classification state relies on color alone — no icon or text. Fails Section 508 / WCAG 2.1 AA.'\n\n[Mobile Researcher]: 'Mobile section just says \"Identical to web\" but on a tactical handset the policy panel covers the full screen and scrolls. Need to be explicit about field constraints.'\n\n[PM again]: 'Section 2 says auto-save, but Section 3 says click Save button. Which is it?'\n\n[QA]: 'What happens if a user's clearance is revoked while a policy edit is pending? Edge case.'",
  "review_context": "Design Review Date: 2026-01-15\nArtifact: Environmental Attributes for ZT ABAC — UX Spec (v2.1)\nPhase: Phase 5 wireframe gate review\nReviewers: Security Architect (mandatory), Compliance Officer, PM, UX Designer, Accessibility Lead, Mobile Researcher, QA\nContext: IL5 DoD/defense environment. Security and compliance are mandatory approval items. Bulk attribute import was explicitly deferred to a later phase per PRD. Accessibility required for Section 508 / WCAG 2.1 AA."
}
```

**Output:**
```json
{
  "executive_summary": {
    "total_feedback_items": 8,
    "must_fix_count": 4,
    "should_fix_count": 3,
    "nice_to_have_count": 0,
    "out_of_scope_count": 1,
    "blocking_issues": true,
    "estimated_fix_effort": "MODERATE",
    "gate_recommendation": "REJECT",
    "gate_rationale": "Spec has 4 MUST-FIX (P1) items: a spillage path (classified channel name shown pre-check), a compliance gap (NIST 800-53 AU-2 audit logging), a Section 508 / WCAG 2.1 AA violation (color-only classification state), and a contradiction (auto-save vs. manual save). These block the gate and must be resolved before implementation. Estimated effort: 1-2 days to fix, 1 day for re-review. Recommend scheduling follow-up review for end of week.",
    "advisory_note": "REJECT here is an advisory recommendation to the orchestrator, not a gate decision. The orchestrator owns gate outcomes per gate-checklists.md."
  },
  "feedback_table": [
    {
      "category": "MUST_FIX",
      "reviewer": "Security Architect",
      "feedback_summary": "Access check renders restricted resource names to users without Need-to-Know (spillage path)",
      "affected_section": "Section 2: Policy Search Workflow",
      "detailed_description": "Section 2 renders the channel name in search results before the access check. A user sees 'Restricted Channel #SCI-X' in the dropdown even without Need-to-Know. This reveals the existence of a restricted resource to an unauthorized user — a spillage path.",
      "suggested_resolution": "Move the access check BEFORE display. Spec should state: 'The system filters search results to channels the user has Need-to-Know for. Channels the user cannot access are not shown.'",
      "impact_if_not_fixed": "Users can discover restricted channels they shouldn't know exist. Violates the DoD Need-to-Know model and NIST 800-207 ZT enforcement.",
      "duplicate_mentions": null
    },
    {
      "category": "MUST_FIX",
      "reviewer": "Compliance Officer",
      "feedback_summary": "Audit logging requirement missing entirely from spec",
      "affected_section": "Section 5 (entire section)",
      "detailed_description": "The PRD requires all access-policy changes to be logged for audit. The spec does not document this. For DoD deployment, audit logging per NIST 800-53 AU-2 is mandatory.",
      "suggested_resolution": "Add a section documenting: what events trigger audit log entries (policy create, edit, apply, revoke), what data is captured (timestamp, actor, subject, attributes changed), where logs are stored (audit service), and retention policy. Include an example log entry.",
      "impact_if_not_fixed": "Spec cannot pass the Security Architect gate. Feature cannot deploy to an IL5 environment without audit logging.",
      "duplicate_mentions": null
    },
    {
      "category": "MUST_FIX",
      "reviewer": "Accessibility Lead",
      "feedback_summary": "Classification state uses color alone (Section 508 / WCAG 2.1 AA failure)",
      "affected_section": "Section 4: Classification States",
      "detailed_description": "Section 4 conveys the classification state with a colored band only — no icon or text label. Users who are colorblind cannot distinguish the state. Violates Section 508 / WCAG 2.1 AA (mandatory for DoD).",
      "suggested_resolution": "Add to Section 4: 'The classification marking pairs the color band with the level text (e.g., \"SECRET\") and a lock icon. State is conveyed by color, text, and icon together.'",
      "impact_if_not_fixed": "Spec fails Section 508 / WCAG 2.1 AA. Feature cannot pass the accessibility gate.",
      "duplicate_mentions": null
    },
    {
      "category": "MUST_FIX",
      "reviewer": "PM",
      "feedback_summary": "Contradiction between auto-save behavior in different sections",
      "affected_section": "Section 2 vs. Section 3",
      "detailed_description": "Section 2 states 'Settings auto-save after user stops typing', but Section 3 says 'User clicks Save button to save settings'. Spec contradicts itself on whether save is automatic or manual. Implementation will be ambiguous.",
      "suggested_resolution": "Choose one behavior and apply consistently: Either (a) auto-save after inactivity timer, or (b) manual save with explicit button. Update both sections to be consistent. If auto-save, explain what happens if user navigates away — is save in progress?",
      "impact_if_not_fixed": "Engineering will receive ambiguous spec and have to guess which behavior is correct. Likely causes implementation to not match design intent.",
      "duplicate_mentions": ["PM mentioned this again in later feedback"]
    }
  ],
  "must_fix_summary": [
    {
      "issue_id": "MUST-FIX-001",
      "summary": "Spillage path: access check happens after restricted resource names are rendered",
      "severity": "P1",
      "blocking_reason": "Reveals existence of a restricted channel to a user without Need-to-Know",
      "resolution_steps": [
        "Review Section 2 Policy Search Workflow",
        "Move the access check before search-result display",
        "Update spec to state: 'The system filters results to channels the user has Need-to-Know for'",
        "Add security note: 'Restricted channels are not revealed in search results to unauthorized users'"
      ],
      "re_review_required": true
    },
    {
      "issue_id": "MUST-FIX-002",
      "summary": "Missing compliance requirement: audit logging not documented",
      "severity": "P1",
      "blocking_reason": "NIST 800-53 AU-2 audit logging is mandatory for IL5 deployment",
      "resolution_steps": [
        "Create a section documenting audit logging requirements",
        "Specify events: policy create, edit, apply, revoke, and any access changes",
        "Document data captured: timestamp, actor, subject, attributes changed",
        "Include an example audit log entry and retention policy",
        "Reference NIST 800-53 AU-2 / DoD ZT RA"
      ],
      "re_review_required": true
    },
    {
      "issue_id": "MUST-FIX-003",
      "summary": "Accessibility violation: classification state uses color alone",
      "severity": "P1",
      "blocking_reason": "Section 508 / WCAG 2.1 AA failure; blocks the accessibility gate",
      "resolution_steps": [
        "Update Section 4 Classification States",
        "Pair the color band with the level text and a lock icon",
        "Ensure the level text clearly identifies the classification",
        "Verify color contrast meets WCAG 2.1 AA (4.5:1 for text)"
      ],
      "re_review_required": true
    },
    {
      "issue_id": "MUST-FIX-004",
      "summary": "Contradiction: auto-save vs. manual save behavior",
      "severity": "P1",
      "blocking_reason": "Ambiguous spec; engineering would have to guess the intended behavior",
      "resolution_steps": [
        "Determine intended behavior: auto-save or manual save",
        "Update Section 2 and Section 3 to be consistent",
        "If auto-save: specify delay timer, in-progress indicators, what happens on navigation",
        "If manual-save: specify Save button location and success/failure feedback"
      ],
      "re_review_required": true
    }
  ],
  "should_fix_summary": [
    {
      "issue_id": "SHOULD-FIX-001",
      "summary": "Help text uses unexplained acronyms (ABAC, etc.)",
      "rationale": "Help text mentions ABAC without explaining it. Not every admin will know the term. Makes the spec less accessible to non-specialist stakeholders.",
      "suggested_fix": "Change help text from 'Define ABAC rules' to 'Define attribute-based rules (which user attributes and values grant access) for this channel.'"
    },
    {
      "issue_id": "SHOULD-FIX-002",
      "summary": "Mobile behavior needs explicit documentation beyond 'Identical to web'",
      "rationale": "Mobile section vaguely states 'Identical to web' but a tactical handset has real constraints: the policy panel goes full-screen on narrow screens, the classification badge can truncate, etc. Mobile-specific documentation prevents implementation surprises.",
      "suggested_fix": "Expand mobile section: 'Mobile: the policy panel is full-width and scrollable on narrow screens. The classification badge keeps its icon and level text when space is tight (color band may compress). Touch interactions identical to web (no swipe gestures). Leave space for the on-screen keyboard (panel max height 60% of viewport).'"
    },
    {
      "issue_id": "SHOULD-FIX-003",
      "summary": "Undefined behavior when a user's clearance is revoked mid-edit",
      "rationale": "QA raised an edge case: if a subject's clearance is revoked while a policy edit is pending, the spec doesn't say what happens to the in-flight change. Leaving it undefined risks an inconsistent or unsafe state.",
      "suggested_fix": "Add an edge-case note to Section 3: on clearance revocation, cancel any pending edit by that user, surface a non-specific notice, and re-evaluate access on the next action (no partial apply)."
    }
  ],
  "out_of_scope_items": [
    {
      "feedback_item": "Add bulk attribute import in this phase",
      "reason_out_of_scope": "Bulk attribute import was explicitly marked out-of-scope for this phase in the PRD. It is a valid request for a later phase.",
      "deferred_to_phase": "Later phase (TBD)",
      "documentation_note": "Bulk attribute import (CSV upload or API batch): deferred. The single-attribute flow in this phase is the foundation for a later bulk import."
    }
  ],
  "conflicts_and_decisions": [
    {
      "conflict_description": "Contradictory feedback on save behavior between two spec sections",
      "reviewer_a": "Section 2",
      "reviewer_a_position": "Settings auto-save after user stops typing",
      "reviewer_b": "Section 3",
      "reviewer_b_position": "User clicks Save button to save settings",
      "recommended_decision": "Implement auto-save behavior (Section 2 is correct). Manual save creates extra clicks and friction.",
      "decision_rationale": "Auto-save is modern UX pattern and reduces user friction. However, spec must clarify: (1) How long does inactivity timer wait? (2) What if user navigates away during save? (3) Is there a visible 'Saving...' indicator? Update Section 3 to match Section 2."
    }
  ],
  "next_steps": {
    "immediate_actions": [
      "Schedule 1-hour refinement session with PM, Security Lead, and Accessibility Lead to discuss MUST-FIX-001 and MUST-FIX-004 (the complex ones)",
      "Assign spec revision task: 2 hours to implement MUST-FIX fixes (audit logging section, error state icons, consistency on save behavior)",
      "Assign security review: 30 min for Security Lead to verify information leakage fix",
      "Schedule 30-min re-review with focused scope on the 4 MUST-FIX items"
    ],
    "spec_revision_required": true,
    "re_review_scope": "FOCUSED",
    "timeline_estimate": "Spec revision: 2 hours. Re-review: 1 hour. Recommended schedule: Revisions by end of Wednesday, re-review Thursday morning, approved by Thursday EOD."
  }
}
```
