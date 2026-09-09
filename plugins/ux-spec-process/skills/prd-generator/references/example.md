# PRD Generator — Worked Example

Full input + partial output for the canonical classified-message-composition PRD (IL5). Schemas: [`schema.md`](schema.md).

## Input Example

```json
{
  "problem_statement": "Fighter pilots and mission coordinators are currently sending classified mission updates via email and unclassified Mattermost channels due to lack of classified messaging capability in Mattermost. This creates compliance violations (classified data on unencrypted email servers) and operational risk (information reaching unvetted recipients). In the past 6 months, we have identified 12 classified message incidents in email, each requiring remediation and formal incident reporting. The feature must enable secure classified messaging with automatic spillage prevention.",
  "research_brief": "User research with 8 fighter pilots and 4 mission coordinators revealed: (1) They understand classification levels and actively try to avoid spillage, but current tools force them into unclassified channels or email. (2) They need visual confirmation of classification level BEFORE sending (not after). (3) They need to see recipient clearance levels to verify message safety. (4) Mobile is the primary interface in tactical operations centers. (5) Competitive analysis shows Slack/Teams lack message-level classification; all have high spillage risk. (6) Threat model identified: message sent to wrong channel is #1 vector. Pre-send verification is essential. (7) Clearance data exists in Active Directory; integration is feasible per Infosec.",
  "user_roles": [
    {
      "role_name": "Fighter Pilot",
      "population_size": 240,
      "primary_context": "Tactical operations center, synchronous, mobile primary, time-critical decisions"
    },
    {
      "role_name": "Mission Coordinator",
      "population_size": 60,
      "primary_context": "Command center, mixed sync/async, desktop + mobile, planning and deconfliction"
    },
    {
      "role_name": "Wing Security Officer",
      "population_size": 8,
      "primary_context": "Administrative, monitoring compliance, audit trail review"
    }
  ],
  "mission_tier": "IL5",
  "compliance_frameworks": ["NIST_800-53", "NIST_800-207", "DISA_STIGs"],
  "timeline": "Phase_1_MVP",
  "success_metrics_baseline": {
    "current_incident_rate": "2 classified message incidents per month",
    "current_task_time": "Composing classified message takes ~45 seconds (users must send via email instead)",
    "current_error_rate": "12 spillage incidents in 6 months = ~2%"
  },
  "known_constraints": [
    "CAC integration work is blocked until Infosec provides OAuth2 API (ETA April 2026)",
    "Mobile team has only 2 engineers; prefer UI-first solutions",
    "Offline capability deferred to Phase 2",
    "Cannot modify Active Directory schema; read-only access only"
  ]
}
```

## Output Example (Partial)

```json
{
  "prd_metadata": {
    "title": "Classified Message Composition with Spillage Prevention (Phase 1)",
    "date_generated": "2026-03-10T14:45:00Z",
    "version": "1.0.0",
    "mission_tier": "IL5",
    "compliance_frameworks": ["NIST_800-53", "NIST_800-207", "DISA_STIGs"],
    "document_classification": "Controlled Unclassified Information (CUI)"
  },
  "executive_summary": {
    "bluf": "Fighter pilots and mission coordinators are sending classified updates via insecure email channels due to lack of classified messaging in Mattermost. This feature adds message-level classification with pre-send recipient verification, eliminating the #1 spillage vector. Target: reduce incidents from 2/month to <0.15/month within 90 days of deployment.",
    "problem_context": "In the past 6 months, 12 classified message incidents were identified, each requiring DoD incident reporting and remediation. Root cause: tools lack message-level classification and pre-send clearance verification. Users are making rational choices (email is clearer about confidentiality) but those choices violate NIST SP 800-53 SC-7 / AC-3 controls and DoDM 5200.01 marking requirements.",
    "proposed_solution_summary": "Add message-level classification marker in Mattermost that: (1) displays classification level on every message before send, (2) shows recipient clearance levels to prevent misdirection, (3) blocks send to channels with lower classification, (4) logs all classification decisions for audit trail.",
    "success_definition": "Classified message composition time is within 5% of unclassified (target: 42 seconds vs. current 45 seconds for unclassified). Spillage incidents drop to <0.15 per month. Audit logs capture all classification events with 100% accuracy. Mobile UX is not a friction point (measured via usage log analysis)."
  },
  "user_stories": [
    {
      "story_id": "US-1.1",
      "role": "Fighter Pilot",
      "narrative": "As a fighter pilot, I need to send a CLASSIFIED message to my wingman and see his clearance level before I hit Send, so that I can be confident the message reaches only someone authorized to receive it.",
      "acceptance_criteria": [
        {
          "criterion_id": "AC-1.1.1",
          "given": "A fighter pilot is composing a message in a classified channel on mobile",
          "when": "He types a message and pauses to select a recipient",
          "then": "The UI shows a dropdown with available recipients. Each recipient name has a clearance level badge: [SECRET] or [TOP SECRET] or [INSUFFICIENT CLEARANCE]. A recipient with insufficient clearance appears grayed out or unavailable."
        },
        {
          "criterion_id": "AC-1.1.2",
          "given": "A pilot has typed a message in a CLASSIFIED channel",
          "when": "He taps 'Send'",
          "then": "A confirmation modal appears showing: (1) Channel name and [CLASSIFIED] badge, (2) 'Message will be sent to: [recipient names + clearance levels]', (3) 'This message is classified [LEVEL]', (4) A large 'Confirm Send' button and a 'Cancel' button."
        }
      ]
    },
    {
      "story_id": "US-2.1",
      "role": "Mission Coordinator",
      "narrative": "As a mission coordinator, I need to send a message that mixes classified and unclassified information, and I need to override the channel's default classification to mark just this message as CLASSIFIED, so that I can control the sensitivity of individual communications.",
      "acceptance_criteria": [
        {
          "criterion_id": "AC-2.1.1",
          "given": "A coordinator is in an unclassified channel",
          "when": "He composes a message containing information that is classified, he should be able to add a classification marker",
          "then": "In the message composer, a dropdown allows selecting message classification: [UNCLASSIFIED | CONFIDENTIAL | SECRET | TOP SECRET]. When he selects a classified level (e.g., [SECRET]), the composer shows a large colored badge and says 'This message will be classified. Recipients must have clearance.'"
        }
      ]
    }
  ],
  "functional_requirements": [
    {
      "req_id": "FR-1.1",
      "category": "Message Composition",
      "role_affected": "Fighter Pilot, Mission Coordinator",
      "requirement": "The system SHALL display the classification level of the channel on the message composer header at all times, including mobile, with minimum font size 12pt and a color-coded badge (e.g., red for SECRET, blue for TOP SECRET).",
      "traces_to_story": "US-1.1",
      "rationale": "Users are composing under time pressure and high cognitive load in tactical operations. A persistent, large, color-coded affordance is necessary to prevent classification mismatches.",
      "acceptance_test": "QA composes a message in a [SECRET] channel on mobile. Channel classification badge is visible at top of composer. Badge remains visible during message typing and does not scroll away on small screens."
    },
    {
      "req_id": "FR-1.2",
      "category": "Message Composition",
      "role_affected": "Fighter Pilot, Mission Coordinator",
      "requirement": "When a user in an IL5 environment sends a message to a channel, the system SHALL display a pre-send confirmation modal showing: (1) Channel name and classification level, (2) List of recipients with their clearance level (retrieved from Active Directory), (3) Message classification level, (4) A 'Confirm Send' button and a 'Cancel' button. Send SHALL NOT be triggered without explicit user confirmation.",
      "traces_to_story": "US-1.1",
      "rationale": "This is the primary control to prevent misdirection. User research showed pilots want confirmation before send, especially for classified messages. Threat model identified message misdirection as the #1 spillage vector.",
      "acceptance_test": "Pilot in classified channel types a message. Hits Send. Confirmation modal appears with recipients and clearance levels. Modal blocks further action until Confirm is clicked. If pilot clicks Cancel, message is not sent but is not lost (remains in composer)."
    },
    {
      "req_id": "FR-1.3",
      "category": "Recipient Verification",
      "role_affected": "Fighter Pilot, Mission Coordinator",
      "requirement": "The system SHALL retrieve clearance level data from Active Directory and display it on all recipient-selection UIs (message composer dropdown, @mention autocomplete, group creator). If clearance level cannot be determined for a user, the system SHALL display [CLEARANCE UNKNOWN] and block selection in classified contexts.",
      "traces_to_story": "US-1.1",
      "rationale": "Users must verify clearance before deciding to message. Without this data, pre-send confirmation modal is ineffective.",
      "acceptance_test": "In message composer, user types '@' to start mention. Autocomplete shows list of users with clearance levels next to names. User can see [SECRET] or [TOP SECRET] or [CLEARANCE UNKNOWN]. If message is classified and user has CLEARANCE UNKNOWN, @mention is grayed out and unselectable."
    },
    {
      "req_id": "FR-1.4",
      "category": "Classification Management",
      "role_affected": "Mission Coordinator",
      "requirement": "The system SHALL allow a user to mark an individual message with a classification level that differs from the channel's default, via a dropdown in the message composer labeled 'Mark this message as: [UNCLASSIFIED | CONFIDENTIAL | SECRET | TOP SECRET]', but SHALL NOT permit the selected level to exceed the channel's configured `max_classification` field (default: equal to the channel's own classification level; raising it requires a separate, explicit, audited admin action per the channel-configuration mitigation in the threat model). If the user selects a level above `max_classification`, the system SHALL block the send and display: 'This channel does not permit [LEVEL] messages. Contact your admin to raise the channel's maximum classification.' The selected classification SHALL be displayed on the message after send.",
      "traces_to_story": "US-2.1",
      "rationale": "Mixed-classification conversations are common in DoD environments. A single channel may contain both classified planning (pre-op) and unclassified results (post-op). Message-level classification is necessary for compliance — but allowing it unconditionally lets a message reach recipients whose clearance was only vetted against the channel's lower default level (T-3.1). The `max_classification` gate keeps the override capability while removing that spillage path.",
      "acceptance_test": "Coordinator in an [UNCLASSIFIED] channel with `max_classification = UNCLASSIFIED` attempts to change message classification to [SECRET]. Send is blocked with the error above; message remains in composer. After an admin explicitly raises the channel's `max_classification` to [SECRET], the same action succeeds: message displays [SECRET] badge in the timeline, recipient sees [SECRET] badge, and audit log captures the classification-raise action."
    },
    {
      "req_id": "FR-2.1",
      "category": "Audit",
      "role_affected": "Wing Security Officer",
      "requirement": "The system SHALL log all classification-related actions with the following information: (1) User ID, (2) Timestamp (UTC), (3) Action (message sent to classified channel | message marked classified | message classification overridden | clearance verification performed), (4) Message ID or conversation ID, (5) Result (success | user cancelled | system blocked). Logs SHALL be immutable and retained for minimum 7 years per NIST SP 800-53 AU-2.",
      "traces_to_story": "All stories",
      "rationale": "DoD compliance requires audit trails for all information security events. Security officers must be able to investigate incidents.",
      "acceptance_test": "Security officer uses audit log viewer to search for all messages sent to [TOP SECRET] channels by a specific user in the past month. Results show user ID, timestamp, message ID, channel, recipient clearance verification results."
    }
  ],
  "non_functional_requirements": {
    "security": [
      {
        "req_id": "NFR-S-1",
        "requirement": "All clearance level data retrieved from Active Directory SHALL be transmitted over TLS 1.2+ (encrypted in transit) and SHALL not be cached longer than 5 minutes on client devices (to prevent stale clearance data).",
        "compliance_control": "NIST SP 800-53 SC-7 (Boundary Protection), SC-8 (Transmission Confidentiality)",
        "verification_method": "Network traffic capture and analysis; cache TTL verification in code review"
      },
      {
        "req_id": "NFR-S-2",
        "requirement": "Message classification level SHALL be encrypted at rest in the database using AES-256-GCM.",
        "compliance_control": "NIST SP 800-53 SC-28 (Protection of Information at Rest), SC-13 (Cryptographic Protection)",
        "verification_method": "Cryptographic audit; database schema review"
      }
    ],
    "performance": [
      {
        "req_id": "NFR-P-1",
        "requirement": "The pre-send confirmation modal (clearance lookup + recipient display) SHALL render within 3 seconds of the user tapping Send, in tactical networks with 2Mbps bandwidth. This is a system-latency budget, distinct from SM-2's end-to-end task-time metric (which includes user compose time and is not a system NFR).",
        "threshold": "<3 seconds at 2Mbps, measured from Send tap to modal fully rendered",
        "test_scenario": "Send a classified message from a mobile device on a throttled 2Mbps connection. Measure latency from tapping Send to the confirmation modal — with clearance levels populated via the AD query — being fully rendered."
      },
      {
        "req_id": "NFR-P-2",
        "requirement": "Clearance level lookup for autocomplete SHALL return results in <500ms even when AD has 10,000+ users.",
        "threshold": "<500ms",
        "test_scenario": "In large organization deployment, use autocomplete to search for recipients. Verify dropdown appears within 500ms."
      }
    ],
    "accessibility": [
      {
        "req_id": "NFR-A-1",
        "requirement": "Classification badges (color-coded indicators) SHALL have a text label in addition to color, and SHALL meet WCAG 2.1 AA contrast ratio of 4.5:1 minimum for both color and text.",
        "wcag_criterion": "WCAG 2.1 1.4.3 (Contrast Minimum), 1.4.11 (Non-text Contrast)",
        "verification_method": "Automated accessibility scanning (Axe, WAVE); manual color contrast check with WebAIM tool"
      },
      {
        "req_id": "NFR-A-2",
        "requirement": "Pre-send confirmation modal SHALL be keyboard navigable (Tab key moves between 'Confirm' and 'Cancel' buttons), and focus state SHALL be clearly visible. Screen reader SHALL announce modal title and all content.",
        "wcag_criterion": "WCAG 2.1 2.1.1 (Keyboard), 4.1.2 (Name, Role, Value)",
        "verification_method": "Manual keyboard navigation test; screen reader test with NVDA or JAWS"
      }
    ],
    "mobile": [
      {
        "req_id": "NFR-M-1",
        "requirement": "Classification badges on mobile SHALL be minimum 44x44pt (touch target size per Apple/Google guidelines) and SHALL NOT be smaller than desktop equivalents. Pre-send confirmation modal SHALL be optimized for 4.5-inch screens (entire modal visible without scroll if possible).",
        "rationale": "Fighter pilots are primarily using mobile in tactical operations. Mobile is NOT a secondary interface; it is the primary one. UI must not be degraded on mobile."
      },
      {
        "req_id": "NFR-M-2",
        "requirement": "Message composer on mobile SHALL display classification level persistently at the top (not hidden in a collapsed header). Recipient verification dropdown SHALL be accessible without leaving the message composer.",
        "rationale": "Mobile screens have limited space. Users must not lose sight of classification level or struggle to access clearance info."
      }
    ]
  },
  "success_metrics": [
    {
      "metric_id": "SM-1",
      "metric_name": "Reduction in classified message spillage incidents",
      "baseline": "2 incidents per month (12 in 6 months)",
      "target": "<0.15 incidents per month",
      "measurement_method": "Audit log review + incident report tracking. Count messages sent to wrong channel or to users without clearance, detected by manual review or automated scanning.",
      "owner": "Wing Security Officer"
    },
    {
      "metric_id": "SM-2",
      "metric_name": "Classified message composition time parity with unclassified",
      "baseline": "45 seconds to compose unclassified message (current); classified messages sent via email at average 120 seconds (routing to email client, risk of sending in email instead)",
      "target": "42 seconds (within 5% of unclassified)",
      "measurement_method": "Instrumentation in message composer: log timestamp at 'compose start' and 'send confirmed'. Aggregate by message classification level.",
      "owner": "Product Manager"
    },
    {
      "metric_id": "SM-3",
      "metric_name": "Audit log accuracy for classification events",
      "baseline": "N/A (new feature)",
      "target": "100% of classification-related actions logged with user, timestamp, action, message ID, result",
      "measurement_method": "Compare audit log entries to actual message sends (via database query). Verify no classification events are missed.",
      "owner": "Security Engineer"
    }
  ],
  "out_of_scope": [
    {
      "feature_name": "Offline message composition with classification",
      "reason": "Deferred to Phase 2. Requires local caching of clearance data and conflict resolution when device comes online. Phase 1 assumes network connectivity."
    },
    {
      "feature_name": "Automatic classification downgrading at time T",
      "reason": "Out of scope pending legal/JAG review of classification policy authority. Who can downgrade? When? This is a policy decision, not a UX one. Will be addressed in compliance scoping with legal team."
    },
    {
      "feature_name": "Integration with CAC reader for biometric confirmation",
      "reason": "Blocked: awaits Infosec OAuth2 API implementation (ETA April 2026). Will be Phase 1.5 enhancement if CAC integration completes on schedule."
    },
    {
      "feature_name": "Cross-organization classified messaging",
      "reason": "Out of scope. Classified conversations are assumed to stay within a single DoD organization. Multi-org classified messaging requires trust/federation agreements not in place."
    }
  ],
  "dependencies": [
    {
      "dependency_id": "D-1",
      "type": "External System",
      "description": "Active Directory API for clearance level lookups. Mattermost must query AD for user clearance level (clearance_level attribute) on every pre-send verification.",
      "owner": "Infosec Team",
      "impact_if_delayed": "Cannot verify recipient clearance. Pre-send modal will be missing critical info. Feature is not releasable without this.",
      "eta": "Q2 2026 (in progress)"
    },
    {
      "dependency_id": "D-2",
      "type": "Mattermost Feature",
      "description": "Message metadata API. Messages must store and retrieve classification level as a custom field/attribute. Requires backend changes to message schema.",
      "owner": "Backend Team",
      "impact_if_delayed": "Cannot persist message classification. Feature is not viable.",
      "eta": "Q1 2026"
    },
    {
      "dependency_id": "D-3",
      "type": "Design System",
      "description": "Classification badge component (icon + color + text, responsive). Must be available in Mattermost design system (Compass) before UI implementation.",
      "owner": "Design System Team",
      "impact_if_delayed": "Designers will create ad-hoc classification badges, leading to inconsistency. Slows UI implementation.",
      "eta": "Q1 2026"
    }
  ],
  "risk_assessment": [
    {
      "risk": "Active Directory clearance data is incomplete or inaccurate",
      "probability": "Medium",
      "impact": "Users may receive incorrect clearance level info, leading to either over-blocking (usability) or under-blocking (security). Either is bad.",
      "mitigation": "Require Infosec to validate AD data completeness before release. Have security team spot-check clearance levels for 50 users. Add manual clearance verification option for security officers (override capability) with full audit logging."
    },
    {
      "risk": "Pre-send modal creates bottleneck in time-critical operations",
      "probability": "Low",
      "impact": "Pilots perceive confirmation modal as friction and disable feature or work around it (negating security benefit).",
      "mitigation": "User test with actual tactical users under time pressure. Optimize modal to <500ms display latency. Consider keyboard shortcut to bypass modal for power users (with audit flag). Have security team weigh UX friction vs. security risk."
    },
    {
      "risk": "Audit log grows too large and degrades system performance",
      "probability": "Low",
      "impact": "After 6 months of heavy usage (1000+ pilots), audit logs may consume significant storage/query time, slowing Mattermost.",
      "mitigation": "Set up database partitioning on audit log table by date. Implement TTL (keep 7 years, then archive). Monitor log growth in beta deployment and adjust if needed."
    }
  ],
  "verification_with_pm": [
    {
      "question": "Should message-level classification override be available to all users, or only to certain roles (e.g., message originator cannot downgrade, only security officers can)?",
      "context": "Legal/policy guidance on who has authority to classify information is unclear. This affects FR-1.4 (message classification dropdown)."
    },
    {
      "question": "If a user tries to send a message to a channel with lower classification than the message itself, should we: (A) Block the send entirely, or (B) Allow send but emit a warning and log the override?",
      "context": "This affects validation logic in FR-1.2. Answer depends on operational need (is it ever legitimate to send a SECRET message to an unclassified channel? Policy team needs to decide.)"
    }
  ]
}
```

## Condensed Usage Walkthrough

```
Input:
- Problem: "Fighter pilots sending classified data via email due to lack of classified messaging in Mattermost"
- Research: "8 pilot interviews + competitive analysis of Slack/Teams showed all platforms lack message-level classification and spillage prevention"
- Roles: Fighter Pilot, Mission Coordinator, Security Officer
- Tier: IL5
- Frameworks: NIST SP 800-53, NIST SP 800-207, DISA STIGs
- Baseline: 2 spillage incidents/month

Output:
- Executive summary with operational impact
- 12+ user stories organized by role
- 15+ functional requirements with acceptance tests
- NFRs covering security (NIST SC-7, SC-8), performance (2Mbps network), accessibility (WCAG), and mobile UX
- Success metrics tied to incident reduction and composition time
- 4 out-of-scope items with reasoning
- 3 dependencies with blockers
- 3 risks with mitigations
- 2 verify-with-PM questions for legal clarity
```

## Design Principles

1. **Compliance is not negotiable**: Every requirement should tie back to compliance necessity, user necessity, or risk mitigation. "Nice-to-have" has no place in DoD specs.
2. **Operational tempo matters**: Tactical users under time pressure need different UX than planning-phase teams. User role and context must inform requirements.
3. **Mobile is not a phase 2 effort**: If field users are in scope, mobile UX is as critical as desktop. Design and test mobile first.
4. **Audit trails are mandatory**: Every compliance-critical action must be logged with user, timestamp, and result.
5. **Verification gates are required**: Ask the PM to clarify ambiguous requirements. Don't assume policy.

## Troubleshooting

**Problem**: "Too many requirements. This is overwhelming."
**Solution**: Prioritize by asking: "Without this requirement, does the feature fail to solve the problem or violate compliance?" If no, move to out-of-scope.

**Problem**: "I don't know how to measure success for this feature."
**Solution**: Success metrics should answer: "How do we know we fixed the operational problem?" If the problem was "pilots are sending classified data via email," the metric is "pilots are now sending via Mattermost" and "spillage incidents drop."

**Problem**: "The PRD references compliance controls I don't understand (NIST SP 800-53 SC-7, AC-3)."
**Solution**: This PRD generator assumes familiarity with DoD compliance. If you don't have the framework docs, escalate to Compliance team before finalizing.
