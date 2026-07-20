# Solution Scorer — Worked Example

Full input + output for the canonical classified-messaging scenario: three approaches (per-message classification, channel-only, hybrid) evaluated for an IL5 tactical environment. Schemas are in [schema.md](schema.md).

## Input Example

```json
{
  "prd_summary": "Fighter pilots and mission coordinators need to send classified messages without risking spillage to unclassified channels. The feature must display classification levels visibly, prevent sending to unvetted recipients, and create an audit trail. Three approaches are under consideration: (1) Message-level classification markers with pre-send verification modal, (2) Channel-level classification enforcement with no message-level override, (3) Hybrid: channel-level default + optional message-level override only for security-officer-approved users.",
  "approaches": [
    {
      "name": "Approach A: Message-Level Classification with Pre-Send Modal",
      "description": "Each message can be independently classified [UNCLASSIFIED | CONFIDENTIAL | SECRET | TOP SECRET]. Channel has a default classification, but users can override. Before send, a confirmation modal shows: channel classification, message classification, recipient clearance levels (from AD), and requires explicit 'Confirm Send' click. Mobile version uses a HOLD gesture (2 seconds) to prevent accidental sends. Classified messages cannot be forwarded or exported outside Mattermost. Comprehensive audit logging of all classification decisions.",
      "assumptions": [
        "Active Directory is accessible for clearance level lookups",
        "Mobile users have network connectivity for pre-send AD queries",
        "Users understand the concept of per-message classification (not just channel-level)",
        "Admins will monitor audit logs weekly"
      ]
    },
    {
      "name": "Approach B: Channel-Level Classification Enforcement Only",
      "description": "Each channel is assigned a single classification level. All messages in that channel inherit this level automatically. No per-message overrides allowed. Users cannot change the classification of a message they send. Access control is enforced at the channel level: admins set who can join and thus who can see messages. Simpler UI (no per-message classification markers). Simpler backend (no per-message classification logic). If users need multiple classification levels in conversation, they must create separate channels. Pre-send verification shows only the channel classification (not dynamic per-message).",
      "assumptions": [
        "Users will create multiple channels for mixed-classification conversations (no single conversation spans levels)",
        "Channel management overhead is acceptable (creates many channels)",
        "Admins properly configure channel ACLs"
      ]
    },
    {
      "name": "Approach C: Hybrid (Channel Default + Admin-Approved Override)",
      "description": "Each channel has a default classification. Regular users cannot override classification. Only security officers can mark individual messages with higher classification (e.g., mark a [SECRET] message in a [CONFIDENTIAL] channel). This bridges Approaches A and B: allows flexibility for edge cases while minimizing user choice. Overrides are logged with security officer name and reason. Pre-send modal shows override status to all recipients. Less cognitive load on regular users (they don't think about message classification), but security officers have additional responsibility for override decisions.",
      "assumptions": [
        "Security officers are dedicated to this task (not ad-hoc)",
        "Security officers understand classification policy and can make sound decisions",
        "Clear escalation path when a regular user needs a message over-classified"
      ]
    }
  ],
  "constraints": {
    "mission_tier": "IL5",
    "bandwidth_context": "tactical_ops_2Mbps",
    "user_population_size": 300,
    "phase_timeline": "Q2 2026 (8 weeks)",
    "engineering_resources": "2 backend engineers + 2 frontend engineers + 1 mobile engineer",
    "critical_blockers": [
      "Active Directory API not available until April 2026 (delays Approach A by 4 weeks)",
      "Mobile team at 70% capacity; cannot take on major new features"
    ]
  },
  "known_threats": [
    {
      "threat_name": "Message Misdirection to Lower-Classification Channel",
      "severity": "P1",
      "relevant_approaches": ["A", "C"]
    },
    {
      "threat_name": "Incomplete AD Clearance Data",
      "severity": "P1",
      "relevant_approaches": ["A"]
    },
    {
      "threat_name": "Admin Misconfigures Channel ACLs",
      "severity": "P2",
      "relevant_approaches": ["B", "C"]
    },
    {
      "threat_name": "Copy/Paste Spillage of Classified Content",
      "severity": "P2",
      "relevant_approaches": ["A", "B", "C"]
    }
  ],
  "weighting_guidance": {
    "prioritize_compliance": true,
    "prioritize_simplicity": false,
    "prioritize_mobile": true,
    "prioritize_extensibility": true,
    "notes": "This is an IL5 classified environment. Compliance cannot be compromised. Mobile is primary interface (tactical pilots). We can invest engineering effort if needed."
  }
}
```

## Output Example (Partial)

```json
{
  "scoring_metadata": {
    "analysis_timestamp": "2026-03-10T16:00:00Z",
    "approaches_evaluated": 3,
    "mission_tier": "IL5",
    "timeline": "Q2 2026"
  },
  "evaluation_matrix": {
    "rubric_source": "${CLAUDE_PLUGIN_ROOT}/templates/conventions.md §3",
    "phase": "phase_4",
    "mission_tier": "IL5",
    "criteria": [
      "Compliance Coverage", "Admin Cognitive Load", "End-User Cognitive Load",
      "Misconfiguration Risk", "Engineering Complexity", "Extensibility", "Mobile / Field Usability"
    ],
    "weights": {
      "Compliance Coverage": 2.00,
      "Misconfiguration Risk": 1.75,
      "Mobile / Field Usability": 1.50,
      "End-User Cognitive Load": 1.25,
      "Admin Cognitive Load": 1.00,
      "Extensibility": 1.00,
      "Engineering Complexity": 0.75
    },
    "weights_rationale": "default IL5/IL6 table (no override)",
    "sum_weights": 9.25,
    "scores": {
      "Approach A: Message-Level Classification with Pre-Send Modal": {
        "Compliance Coverage": { "score": 5, "justification": "Per-message classification (AC-3), pre-send verification, audit logging (AU-2), non-exportable classified messages (SC-7) — exceeds controls." },
        "Admin Cognitive Load": { "score": 3, "justification": "Admins must track channel default + message overrides + audit review; trainable but not light." },
        "End-User Cognitive Load": { "score": 4, "justification": "Pre-send modal makes channel/message/clearance explicit, but users juggle three concepts." },
        "Misconfiguration Risk": { "score": 3, "justification": "System blocks sends to insufficient clearance, but audit-review is a manual detective control that can lapse." },
        "Engineering Complexity": { "score": 2, "justification": "Per-message data model + AD integration + modal (desktop/mobile) + audit logging; AD API delay compresses the 8-week window." },
        "Extensibility": { "score": 4, "justification": "Per-message classification is a strong base for retention/DLP/downgrade in later phases." },
        "Mobile / Field Usability": { "score": 4, "justification": "HOLD-to-send modal works on mobile; AD lookups add latency at 2Mbps unless cached." },
        "weighted": 34.75,
        "normalized": "3.76 / 5.00"
      },
      "Approach B: Channel-Level Classification Enforcement Only": {
        "Compliance Coverage": { "score": 3, "justification": "Channel ACL covers AC-3 but no per-message audit (weak AU-2) and no mixed-classification control." },
        "Admin Cognitive Load": { "score": 4, "justification": "Simple concept, but channel proliferation and per-channel ACL/retention management add ongoing burden." },
        "End-User Cognitive Load": { "score": 5, "justification": "Classification is automatic per channel; no modal, no per-message decision." },
        "Misconfiguration Risk": { "score": 2, "justification": "Admin can create a SECRET-named channel and forget the ACL; nothing in the system prevents it." },
        "Engineering Complexity": { "score": 5, "justification": "Reuses existing channel classification field; shippable in 2-3 weeks." },
        "Extensibility": { "score": 2, "justification": "Channel-only architecture is a dead end for per-message retention/DLP — requires re-architecture." },
        "Mobile / Field Usability": { "score": 3, "justification": "User must find the right channel among many on a small screen; no pre-send guard." },
        "weighted": 30.00,
        "normalized": "3.24 / 5.00"
      },
      "Approach C: Hybrid (Channel Default + Admin-Approved Override)": {
        "Compliance Coverage": { "score": 4, "justification": "AC-3 via channel ACL + AU-2 via logged officer overrides; removes user-driven misclassification, but not full per-message flexibility." },
        "Admin Cognitive Load": { "score": 4, "justification": "Clear rule and responsibility boundary; officers handle a bounded override queue." },
        "End-User Cognitive Load": { "score": 5, "justification": "Regular users make zero classification decisions — send to channel, done." },
        "Misconfiguration Risk": { "score": 4, "justification": "Channel-ACL risk remains, but user-level misclassification is eliminated and overrides are logged/reversible." },
        "Engineering Complexity": { "score": 3, "justification": "Adds override role + officer-only UI + audit logging; no message-level AD integration; ~4-5 weeks." },
        "Extensibility": { "score": 3, "justification": "Override layer is forward-compatible; full per-message classification would need an added layer later." },
        "Mobile / Field Usability": { "score": 5, "justification": "Identical to desktop — send to channel, automatic classification, no modal in the common path." },
        "weighted": 38.00,
        "normalized": "4.11 / 5.00"
      }
    },
    "recommended": "Approach C: Hybrid (Channel Default + Admin-Approved Override)",
    "tie_break_applied": false,
    "anti_gaming_flag": null
  },
  "recommendation": {
    "recommended_approach": "Approach C: Hybrid (Channel Default + Admin-Approved Override)",
    "bluf": "Recommend Approach C because it balances compliance (strong audit trail + AC-3 enforcement), usability (simplest for tactical pilots), and engineering feasibility (4-5 weeks with current team). It defers the complexity of per-message classification decisions to a trained security officer role, reducing user error and misconfiguration risk. Normalized score: 4.11 / 5.00 (best of the three).",
    "primary_reason": "Approach C scores highest (4.11 / 5.00) under the canonical IL5 default weights (Compliance 2.00, Misconfiguration 1.75, Mobile 1.50). It avoids the engineering complexity and timeline risk of Approach A (AD integration delay) while maintaining significantly stronger compliance and security posture than Approach B (which has a critical misconfiguration risk).",
    "key_advantages": [
      "BEST NORMALIZED SCORE (4.11 / 5.00, vs. A=3.76, B=3.24) under the IL5 default weights",
      "Lowest engineering complexity (4-5 weeks vs. 6-8 for A) — fits timeline despite AD delay",
      "Zero classification decisions for regular users (lowest user cognitive load = 5/5) — perfect for pilots under time pressure",
      "Strong compliance (audit logging + AC-3) without the full complexity of per-message classification",
      "Clear role boundary: security officers own override decisions; pilots execute send. No ambiguity.",
      "Addresses threat models: prevents misdirection (channel-level ACL), logs decisions (AU-2), avoids misconfiguration from user errors"
    ],
    "trade_offs": [
      {
        "trade_off": "Less flexible than Approach A (security officers must approve overrides; regular users cannot mark messages higher)",
        "rationale": "This is a BENEFIT, not a trade-off. Reducing user choice reduces error risk. In IL5 environments, controlled flexibility is better than unlimited choice."
      },
      {
        "trade_off": "More complex than Approach B (adds override mechanism, security officer role)",
        "rationale": "Worth it. Approach B has unacceptable misconfiguration risk (P2 threat: admins forget ACLs). Approach C mitigates this by removing classification decisions from regular users."
      },
      {
        "trade_off": "Does not achieve full per-message classification (unlike Approach A)",
        "rationale": "Acceptable for Phase 1. Overrides cover 95% of use cases (mixed-classification conversations). If Phase 2 needs true per-message classification, we can upgrade at that point (design is forward-compatible)."
      }
    ]
  },
  "risk_analysis": {
    "top_3_risks": [
      {
        "risk_rank": 1,
        "risk_name": "Security officers do not respond quickly to override requests, creating delays for pilots",
        "description": "A pilot needs to send a [SECRET] message in a [CONFIDENTIAL] channel. She submits an override request. If the security officer is busy or offline, the override might take hours. In a tactical scenario, this delay could be mission-critical.",
        "likelihood": "Medium",
        "impact": "Pilots perceive the system as unresponsive and fall back to email or voice comms, defeating the purpose of the feature.",
        "mitigation": "DESIGN: Create a 'request override' button that submits a pre-filled form to the security officer. OPERATIONAL: Establish SLA for override response (e.g., 'security officer responds within 15 minutes'). Ensure security officer role has no other duties during peak operational hours. FALLBACK: If no security officer is available, allow pre-approved trusted users to self-approve overrides (with post-hoc audit review)."
      },
      {
        "risk_rank": 2,
        "risk_name": "Channel ACL misconfiguration still occurs, exposing lower-clearance users to higher-classification messages",
        "description": "Admin creates [SECRET] channel but forgets to set ACL. A user with [CONFIDENTIAL] clearance joins and sees [SECRET] content (via an admin-approved override). This is a compliance violation.",
        "likelihood": "Medium (same misconfiguration risk as Approach B)",
        "impact": "Classified data exposed to unauthorized user. Incident report required. Training gap identified.",
        "mitigation": "DESIGN: When admin creates a classified channel, require explicit ACL configuration before channel can be published (no 'create and configure later'). Show a warning: 'This channel is [SECRET]. Only users with SECRET+ clearance can join. Who should have access?' Force admin to select users or groups. OPERATIONAL: Audit classified channels monthly for ACL correctness. Escalate any public or overly-permissive channels. SYSTEM: Implement read-ahead validation in pre-send modal: check if this recipient can actually read the channel (verify ACL before send is confirmed)."
      },
      {
        "risk_rank": 3,
        "risk_name": "Override audit logs are not reviewed, so unauthorized overrides go undetected",
        "description": "A rogue security officer approves overrides for messages they shouldn't (e.g., favoring certain people). Audit logs exist, but nobody reviews them. Months pass before this is discovered.",
        "likelihood": "Low (requires motivated insider)",
        "impact": "Insider threat succeeds. Classified information shared with unauthorized recipients. Detection is months delayed.",
        "mitigation": "OPERATIONAL: Establish a policy: override logs are reviewed weekly by a second security officer (dual approval for auditing). Random spot-checks are performed (10% of overrides reviewed in detail). DESIGN: Highlight override requests in a dashboard with summary metrics: 'security officers approved X overrides this week'. Unusual patterns (one officer approving >10/week) trigger alerts. SYSTEM: Flag overrides that send to users with lower-than-message clearance (even if override was approved, this is a red flag for review)."
      }
    ],
    "threat_model_coverage": "Approach C mitigates most known threats: Message Misdirection (addressed by channel-level ACL + pre-send verification), Incomplete AD Clearance Data (no issue because Approach C does not require real-time AD queries for regular message sends), Admin Misconfiguration (partially; still vulnerable to ACL misconfiguration), Copy/Paste Spillage (same risk as all approaches). Overall coverage: HIGH for this threat model.",
    "unmitigated_threats": [
      {
        "threat_name": "Copy/Paste Spillage of Classified Content",
        "severity": "P2",
        "why_unmitigated": "All three approaches allow this (it's a fundamental OS capability). Would require OS-level or copy-disabled UI (present in Approach A recommendations, not in Approach C by default). Recommend adding copy-disabled mode for Approach C as an enhancement."
      }
    ]
  },
  "stakeholder_impact": {
    "for_engineering": "Approach C is BEST for engineering. 4-5 weeks of work (fits timeline even with AD delay). No AD integration needed for Phase 1. Uses existing channel schema. Clear scope boundary. Less risk of bugs due to simpler implementation. Recommend assigning 4 engineers (2 backend, 1 frontend, 1 mobile) for 4 weeks.",
    "for_security": "Approach C is ACCEPTABLE for security. Provides audit trail (AU-2) and access control (AC-3). Does NOT fully address per-message classification (like Approach A), but compensates with controlled override process and logging. Request that security team review override approval criteria before launch (what counts as a valid reason for override?).",
    "for_operations": "Approach C creates NEW operational workload: security officers must handle override requests. Estimate 1-2 hours/week for 8 security officers managing 300 users (0.25-0.5 hours/officer/week). This is manageable. SLA must be 15 minutes max for response. Monitor override request volume weekly.",
    "for_end_users": "Approach C is BEST for pilots and coordinators. Simplest UX: send to channel, done. No modal dialogs, no classification decisions. Classification is automatic. Users with special needs (need to send higher-classification messages) have a clear escalation path (request override). Expected adoption: HIGH (simplest to understand and use). Training required: minimal (30 minutes per user)."
  },
  "scenario_testing": [
    {
      "scenario": "Active Directory is down for 2 hours (common in DoD environments)",
      "impact_on_recommendation": "ZERO IMPACT. Approach C does not depend on AD for regular message sends. Only channel ACLs (which are cached) are used. System remains fully functional.",
      "mitigation_if_needed": "None. This is an advantage of Approach C over Approach A (which would fail or degrade)."
    },
    {
      "scenario": "New security officer hired; they are not trained on override approval criteria",
      "impact_on_recommendation": "MEDIUM IMPACT. Untrained officer might approve invalid overrides. System still logs the decisions (audit trail exists), but compliance risk is present until officer is trained.",
      "mitigation_if_needed": "Require security officer training before granting override role. Use template/checklist for override decisions (e.g., 'Is the sender authorized to handle [LEVEL] information? Is the recipient cleared for [LEVEL]?'). First 10 overrides reviewed by a senior officer."
    },
    {
      "scenario": "Pilot requests an override but no security officer is available (off-shift, holiday)",
      "impact_on_recommendation": "MEDIUM IMPACT (operational urgency). Pilot cannot send time-critical classified message and falls back to insecure channel.",
      "mitigation_if_needed": "DESIGN: Create 'expedited override' process for time-critical scenarios (e.g., pilot talks to their commanding officer, who approves and is logged as the approver). OPERATIONAL: Ensure security officer on-call rotation covers all operational hours. Estimated impact: 5-10 expedited overrides per month (low frequency)."
    },
    {
      "scenario": "Phase 2 requires true per-message classification (not just overrides)",
      "impact_on_recommendation": "LOW IMPACT. Approach C architecture is forward-compatible. Can add per-message classification UI layer on top of the override mechanism. Design can be extended without major rework.",
      "mitigation_if_needed": "Document this assumption clearly: 'Approach C is a Phase 1 MVP. If Phase 2 needs unrestricted per-message classification, we will extend this design.' No rework expected."
    }
  ],
  "go_no_go_assessment": {
    "recommendation": "PROCEED WITH CONDITIONS",
    "reasoning": "Approach C scores highest (4.11 / 5.00 normalized) and is the best fit for this IL5 tactical environment. It balances compliance, usability, and engineering feasibility. However, two conditions must be met before launch: (1) Security team must define override approval criteria in writing, (2) Security officers must complete override training, (3) On-call security officer rotation must be established for tactical operations hours.",
    "conditions_if_conditional": [
      "Security team (Infosec leadership) approves the override approval criteria document (what qualifies as a valid override reason) by [DATE]",
      "All 8 security officers complete 2-hour override training and pass a short quiz before Phase 1 launch",
      "Establish on-call rotation: one security officer available 24/7 during tactical operations (coordinate with leadership for this resource commitment)",
      "Conduct a 2-week pilot with 1 wing (60 users) before full rollout to all 300 users. Monitor: override request volume, response time, user feedback.",
      "Post-pilot: review audit logs with security team. Identify any approval issues. Adjust training/criteria if needed before full rollout."
    ]
  }
}
```

## Condensed Usage Walkthrough

```
Inputs:
- 3 approaches: per-message classification, channel-only, hybrid
- IL5 environment, tactical ops (2Mbps network), 300 users, 8-week timeline
- AD integration blocked until April
- Known threats: misdirection, incomplete clearance data, misconfiguration, insider forward

Scoring (IL5 default weights per conventions.md §3; Σ = 9.25 → report normalized X.XX / 5.00):
- Weighted by: Compliance 2.00, Misconfiguration 1.75, Mobile 1.50, End-User Load 1.25, Admin Load 1.00, Extensibility 1.00, Engineering 0.75
- Approach A: 3.76 / 5.00 (best compliance, but AD delay + engineering complexity)
- Approach B: 3.24 / 5.00 (simplest UX, but misconfiguration risk)
- Approach C: 4.11 / 5.00 (balanced, no AD dependency, simplest UX for users)

Recommendation: Approach C
- BLUF: "Recommend Approach C because it best balances compliance (audit trail + AC-3), usability (simplest for pilots), and engineering feasibility (4-5 weeks, no AD delay). Security officers own classification decisions; pilots execute sends."
- Top 3 Risks: (1) Slow override response time, (2) Channel ACL misconfiguration, (3) Override logs not reviewed
- Mitigations: Override SLA, forced ACL config UI, weekly dual audit of logs
- Proceed: YES, with conditions (override criteria approved, security officer training, on-call rotation)
```

## Design Principles

1. **Trade-offs are explicit**: Every approach gains something and loses something. Make this visible.
2. **Constraints matter**: Engineering capacity, timeline, and technical blockers (AD delay) directly affect feasibility.
3. **Context is decisive**: The "best" approach for a startup differs from IL5 DoD. Weighting should reflect the specific context.
4. **Compliance is non-negotiable in DoD**: If an approach fails a critical control, it should not be recommended, regardless of score.
5. **Simple usually wins (tie-break)**: If two approaches are within 0.20 normalized, recommend the simpler one — the higher Engineering Complexity score (per conventions.md §3).

## Troubleshooting

**Problem**: "The three approaches have very similar scores. How do I choose?"
**Solution**: Apply the tie-break — within 0.20 normalized, recommend the simpler one (higher Engineering Complexity). If they are still close, look at residual risks: if Approach A scores 4.05 / 5.00 and Approach C 4.00 / 5.00 but A carries a P1 risk C doesn't, pick C and flag the anti-gaming rationale.

**Problem**: "My stakeholders disagree on what should be weighted higher."
**Solution**: This is a feature, not a bug. Use the matrix to surface the disagreement. Show that compliance-focused weighting favors A, while usability-focused weighting favors C. Let leadership decide the weighting, then the matrix resolves the recommendation.

**Problem**: "The recommended approach has an unacceptable risk."
**Solution**: Recommend "RECONSIDER" and escalate. Do not recommend an approach that creates unacceptable compliance or security risk, even if the matrix score is high. Your job is to flag this to decision-makers.
