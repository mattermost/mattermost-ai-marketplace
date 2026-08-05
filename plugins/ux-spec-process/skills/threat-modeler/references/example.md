# Threat Modeler — Category Checklists & Worked Example

Companion to the lean SKILL.md. Contains the full per-category probe lists (the System Prompt names the four categories and a few probes each; the exhaustive lists live here), a complete worked example, design principles, and troubleshooting. Schemas: [`schema.md`](schema.md). Severity is the canonical P1/P2/P3 scale in [`${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §1](../../../.${CLAUDE_PLUGIN_ROOT}/templates/conventions.md).

## Full category probe lists

For each path/probe below: identify the UI element or flow that enables it, assess severity (P1/P2/P3), and recommend a specific mitigation.

### 1. DATA SPILLAGE PATHS (how could a user accidentally expose classified information?)
- Message misdirection: sent to wrong channel, wrong recipient, wrong classification level
- Copy/paste + upload: user copies classified text but pastes it in unclassified document
- Screenshot + share: user takes screenshot of classified info, shares via insecure channel
- Forwarding/sharing across boundaries: message forwarded to user without clearance
- Download + store: user downloads classified content to insecure device or cloud storage
- Search + disclosure: search results showing classified information to users without clearance
- Mobile + home network: classified content synced to unencrypted home wifi
- Audit log exposure: logs containing classified data are readable by unauthorized users

### 2. IMPLICIT TRUST (where does the UI create false confidence in security?)
- Color-coded badges that the user trusts but are not enforced by backend
- "Secure" or "Encrypted" labels that are not actually cryptographically verified by the user
- Read receipts implying the message reached the intended recipient (it might have been forwarded)
- Presence indicators suggesting a user is "active" and therefore will see a message (they might be AFK)
- Desktop notifications showing classified content in plaintext (if device is unlocked, anyone can read it)
- Channel names implying classification level but no actual enforcement ("classified-channel" is just a name)
- Sensitivity labels on Teams/Slack that are enforced only at admin level, not at message level
- Admin consent for sharing (user assumes admin vetted the request, but admin might not understand security implications)

For each: explain what the user assumes (incorrectly) and what the backend actually does (or doesn't do).

### 3. MISCONFIGURATION RISK (what can an admin accidentally do that reduces security?)
- Create a channel with a permissive name but forget to set access controls (e.g., "classified-planning" is discoverable by all)
- Grant someone temporary access without a TTL (access is never revoked)
- Set a default classification level on a channel but forget that individual messages can override it
- Enable a plugin without realizing it logs sensitive data
- Create a shared folder without restricting who can export/download files
- Set retention policies that keep classified data longer than compliance allows
- Export/backup user data for archival without encrypting the export

For each: identify the UI that leads to this misconfiguration and recommend a control (confirmation dialog, default to safer setting, warnings).

### 4. INSIDER THREAT (how could a malicious user exploit the UI?)
- Add self to sensitive channels via discoverable group
- Export large datasets of messages (if export is available)
- Privilege escalation via impersonation (if display names are not verified)
- Social engineering via fake "system" messages (if message source is not clear)
- Exfiltration via DM to external account (if DMs can be hidden or forwarded quietly)
- Bulk @mention to notify large groups without visibility (if @all has no warnings)
- Create false channels to trick others into sharing classified info
- Modify shared documents to introduce false/malicious information (if version control is not visible)

For each: identify the UX affordance that enables this and recommend a mitigation.

## Severity mapping (per conventions.md §1, applied to UI-layer threats)

- **P1 (Blocker / MUST-FIX):** Threat allows direct spillage of classified information with no effective recovery, OR has no effective mitigation, OR violates a DoD control. Must be resolved/mitigated before the gate passes.
- **P2 (Should-fix):** Threat enables spillage but requires the user to ignore warnings or misconfigure; mitigations exist but are not foolproof. Resolve, or explicitly defer with recorded rationale.
- **P3 (Nice-to-have):** Threat is possible only with a specific circumstance + user error, and recovery is feasible. Track; non-blocking.

Map any "Critical/High/Medium/Low" or P0 inputs onto P1/P2/P3 — never introduce a parallel scale.

## Input Example

```json
{
  "artifact_to_review": "FR-1.2: When a user in an IL5 environment sends a message to a channel, the system SHALL display a pre-send confirmation modal showing: (1) Channel name and classification level, (2) List of recipients with their clearance level (retrieved from Active Directory), (3) Message classification level, (4) A 'Confirm Send' button and a 'Cancel' button. Send SHALL NOT be triggered without explicit user confirmation.\n\nFR-1.3: The system SHALL retrieve clearance level data from Active Directory and display it on all recipient-selection UIs (message composer dropdown, @mention autocomplete, group creator). If clearance level cannot be determined for a user, the system SHALL display [CLEARANCE UNKNOWN] and block selection in classified contexts.\n\nUI Flow: Pilot composes message in [SECRET] channel. Before send, modal appears showing: Channel [SECRET], Recipients [Pilot A: SECRET, Pilot B: CLEARANCE UNKNOWN], Message [SECRET]. Pilot sees CLEARANCE UNKNOWN next to Pilot B and decides not to send to them.",
  "artifact_type": "spec",
  "mission_tier": "IL5",
  "focus_areas": ["data_spillage", "implicit_trust", "misconfiguration", "insider_threat"],
  "user_population": "tactical_ops",
  "known_admin_capabilities": [
    "create channels",
    "set channel classification level",
    "add users to channels",
    "export messages",
    "modify channel access control lists",
    "view audit logs"
  ],
  "previous_incidents": [
    "Pilot sent classified message to wrong channel (2 incidents in 6 months)",
    "Admin accidentally created public channel with 'classified' in name but no access controls"
  ]
}
```

## Output Example (Partial)

```json
{
  "threat_model_metadata": {
    "document_reviewed": "Classified Message Composition PRD, Phase 1",
    "analysis_timestamp": "2026-03-10T15:30:00Z",
    "mission_tier": "IL5",
    "total_threats_identified": 8,
    "p1_count": 3,
    "p2_count": 4,
    "p3_count": 1
  },
  "executive_summary": {
    "key_findings": [
      "Pre-send confirmation modal is strong control, but does not prevent copy/paste spillage of classified content from the message itself",
      "CLEARANCE UNKNOWN state creates implicit assumption that if you cannot select someone, they lack clearance. But AD might be incomplete, leading to over-blocking or misplaced trust.",
      "Mobile UI will have reduced threat visibility due to space constraints. Confirmation modal might be dismissible too easily on phone.",
      "Admin misconfiguration risk: admin can set channel classification but cannot enforce that ALL messages in channel have >= that classification. Hybrid conversations are possible.",
      "Insider threat: no audit trail of WHO removed themselves from a sensitive channel, or WHO forwarded a message. Audit logs are reactive, not preventive."
    ],
    "overall_risk_posture": "ACCEPTABLE WITH MITIGATIONS. The design is significantly stronger than current state (email). But 2 P1 threats must be addressed before release.",
    "recommendation": "Proceed to design phase, but incorporate mitigations for P1 threats. Conduct design review and mobile UX testing with actual tactical users before implementation. Escalate CLEARANCE UNKNOWN policy question to Infosec before finalizing."
  },
  "threats": [
    {
      "threat_id": "T-1.1",
      "threat_name": "Copy/Paste Spillage of Classified Content",
      "threat_category": "data_spillage",
      "ui_element": "Message composer textarea (user can select and copy any classified text before send)",
      "threat_description": "User composes a classified message but then copy/pastes the content into an unclassified document, email, or chat. The pre-send modal does not prevent this because the user has already created the classified content in memory.",
      "likelihood": "Medium",
      "impact": "Classified content exposed to unclassified medium (e.g., email, shared document, public chat). This violates NIST SP 800-53 AC-4 (information flow), SC-7 (boundary protection) and DoDM 5200.01 marking/handling.",
      "recoverability": "Low - once content is in unclassified document, exposure has occurred. Recovery requires identifying the document and potentially incident reporting.",
      "severity": "P2",
      "affected_users": "All users composing classified messages",
      "root_cause": "The design focuses on preventing message send to wrong destination, but does not control what happens to the content AFTER composition. Copy/paste is a fundamental OS capability that the UI cannot directly prevent.",
      "example_scenario": "Pilot composes a classified message in Mattermost. He decides not to send it to Pilot B (because B lacks clearance). But he's in a hurry, so he copy/pastes the message text into an email to send to a different recipient. The message content is now in email (unencrypted, unaudited).",
      "recommended_mitigation": "OPTION 1 (Strong): Implement 'Copy Disabled' mode for classified message composers. User cannot select/copy text while composing a classified message. Must paste content fresh if needed. OPTION 2 (Medium): Add a visual warning above the message composer: 'Do not copy/paste this content outside Mattermost. Use only within classified channels.' OPTION 3 (Weak): Log clipboard access events and alert if classified text is copied (detection, not prevention). Recommend OPTION 1 + OPTION 2.",
      "mitigation_effectiveness": "OPTION 1 would eliminate the threat. OPTION 2 + detection would reduce likelihood (user might remember warning and think twice).",
      "residual_risk": "Even with mitigation, a determined insider could re-type classified content or take screenshots. Cannot be fully eliminated, only reduced.",
      "implementation_notes": "OPTION 1 (Copy Disabled) requires OS-level APIs (contenteditable element with copy preventDefault handler). This is feasible on desktop but may not work on all mobile browsers. Test on iPhone/Android. OPTION 2 is easy to implement."
    },
    {
      "threat_id": "T-1.2",
      "threat_name": "Incomplete Active Directory Clearance Data Leads to Over-Trust",
      "threat_category": "implicit_trust",
      "ui_element": "Pre-send confirmation modal showing recipient clearance levels",
      "threat_description": "The modal displays clearance levels from Active Directory. If AD is incomplete or not updated, the user might see [CLEARANCE UNKNOWN] for a user who actually has clearance. User might assume the person is unvetted and exclude them. Conversely, if a clearance is erroneously missing from AD, user sees adequate clearance when they shouldn't. Either case is bad: first reduces usability (false blocks), second creates spillage (false permits).",
      "likelihood": "Medium",
      "impact": "False blocks reduce usability and drive users to workarounds (email). False permits enable spillage. Both are problematic.",
      "recoverability": "Medium - the modal makes the error visible, so user can catch and NOT send. But if user trusts the data and sends anyway, spillage occurs.",
      "severity": "P1",
      "affected_users": "All users. But highest impact on admins who add new users (clearance not yet in AD) and users receiving new clearances (AD not yet updated).",
      "root_cause": "Design assumes Active Directory is the source of truth and is always up-to-date. In reality, AD is a business process system that lags reality. New employees might not have clearances entered for weeks. Clearance upgrades might take months to propagate.",
      "example_scenario": "New pilot joins the squadron. Clearance is SECRET. But it takes 3 weeks for Infosec to enter the clearance in AD. In the meantime, other pilots try to message the new pilot about classified planning and see [CLEARANCE UNKNOWN]. They either exclude the new pilot (usability failure) or guess (security failure).",
      "recommended_mitigation": "REQUIREMENT: Before deployment, Infosec MUST audit AD for completeness and establish an SLA for clearance updates (e.g., 'new clearances entered within 2 business days'). UI MITIGATION: When [CLEARANCE UNKNOWN] is shown, add explanatory text: 'Clearance not found in directory. Contact [security officer] to verify clearance status.' This shifts responsibility back to human verification. DESIGN MITIGATION: Provide security officers with a manual override button in the modal: 'I have verified this user has [LEVEL] clearance. Override and send.' This creates an audit trail of manual verification.",
      "mitigation_effectiveness": "Mitigations reduce but do not eliminate risk. Requires process discipline (AD SLA) + UI support (override + audit trail). Without SLA enforcement, risk remains.",
      "residual_risk": "Even with mitigations, users might click 'Override' without actually verifying, or might trust a false [CLEARANCE UNKNOWN] state. Residual risk is Medium.",
      "implementation_notes": "Override button is critical for Phase 1. Must log: user who overrode, who they were sending to, what they overrode, timestamp. This log is reviewed by security officers weekly."
    },
    {
      "threat_id": "T-2.1",
      "threat_name": "Confirmation Modal is Dismissible Too Easily on Mobile",
      "threat_category": "data_spillage",
      "ui_element": "Pre-send confirmation modal on mobile",
      "threat_description": "On a small mobile screen (4.5 inches), the confirmation modal takes up most of the space. A user under time pressure might quickly scan it and tap 'Send' without reading the recipient list. The modal might also be dismissible by tapping outside of it (common mobile pattern), allowing user to accidentally cancel instead of confirming.",
      "likelihood": "High",
      "impact": "User sends message to wrong recipient or channel without realizing. Classified spillage.",
      "recoverability": "Low - message is sent before user realizes.",
      "severity": "P1",
      "affected_users": "Tactical pilots and coordinators using mobile (primary use case)",
      "root_cause": "Mobile UX requires different interaction patterns due to screen size. A confirmation modal that works on desktop (user reads, clicks) becomes a liability on mobile (user skims, taps incorrectly).",
      "example_scenario": "Pilot is in tactical operations center, receiving orders over radio. She composes a classified message to her wingman while simultaneously listening to orders. She hits Send. Mobile confirmation modal appears, covering most of the screen. She quickly taps what she thinks is 'Send' but is actually tapping slightly off-center and dismisses the modal. Message is not sent. She tries again. Second attempt is sent to wrong recipient because she was distracted by the radio.",
      "recommended_mitigation": "DESIGN CHANGES: (1) Modal should NOT be dismissible by tapping outside. Only 'Confirm Send' and 'Cancel' buttons should close it. (2) Modal should display recipient list in a scrollable area with LARGE, high-contrast 'Confirm' button (minimum 44x44pt). (3) Consider requiring a HOLD gesture (press and hold for 2 seconds) to send, instead of a simple tap. This prevents accidental sends. (4) Add a visual/haptic confirmation: phone vibrates when Send is confirmed, giving the user sensory feedback that action was received.",
      "mitigation_effectiveness": "HOLD gesture + haptic feedback would greatly reduce accidental sends. Requires user education.",
      "residual_risk": "Even with these mitigations, a user in high stress might not read the modal. But the friction would force them to slow down and verify. Residual risk would be Low.",
      "implementation_notes": "HOLD gesture requires testing with actual users. Some might find it cumbersome. Haptic feedback requires secure protocol (don't vibrate on plaintext messages). Test on iPhone + Android."
    },
    {
      "threat_id": "T-3.1",
      "threat_name": "Admin Misconfigures Channel as Mixed-Classification",
      "threat_category": "misconfiguration",
      "ui_element": "Channel creation/settings UI (not shown in PRD; assumed to exist)",
      "threat_description": "Admin creates a channel and sets its classification level to [CONFIDENTIAL]. But the PRD allows message-level classification overrides, so users in that channel can send [SECRET] or [TOP SECRET] messages. If the channel ACL (access control list) is not properly enforced, users with [CONFIDENTIAL] clearance might be able to join the channel and see [SECRET] messages, violating information handling rules.",
      "likelihood": "Medium",
      "impact": "User with lower clearance sees classified information they're not cleared for. Compliance violation and security incident.",
      "recoverability": "Medium - the message remains in the channel, so the exposure is detected if audit logs are reviewed. But immediate recovery (removing user access) might be missed.",
      "severity": "P2",
      "affected_users": "All users in the channel + admins who did not properly configure ACLs",
      "root_cause": "Design allows message-level classification to differ from channel-level. This flexibility is useful for mixed conversations but creates a misconfiguration risk: admin might set channel to one level without realizing it will contain higher-level messages.",
      "example_scenario": "Admin creates a channel called 'mission-planning' and sets it to [CONFIDENTIAL] because most planning is unclassified but some details are sensitive. Admin does not realize that pilots will override messages to [SECRET] for specific tactical details. A contractor with [CONFIDENTIAL] clearance joins the channel and reads [SECRET] messages they're not cleared for.",
      "recommended_mitigation": "REQUIRED MITIGATION (normative, not advisory): Implement a `max_classification` field on channels, defaulting to the channel's own classification level. The message composer's classification-override dropdown (FR-1.4) SHALL reject any selection above `max_classification` — this is a blocking control, not a warning. Raising `max_classification` requires an explicit, separate admin action (not a checkbox in the same flow as message send) and is itself an audited event. AUDIT MITIGATION (defense-in-depth, not primary): additionally log every message classified at the channel's max level for periodic security-officer review.",
      "mitigation_effectiveness": "Blocking at max_classification removes the spillage path entirely rather than relying on admin follow-through on a warning; audit logging catches any residual misconfiguration in the admin-raise flow itself.",
      "residual_risk": "An admin who explicitly raises max_classification without verifying channel membership clearance still creates exposure — this is now a deliberate, audited admin action rather than an unnoticed default, so residual risk is Low.",
      "implementation_notes": "Max_classification field is a schema change. Coordinate with backend team. Default to channel classification level (no override allowed) unless admin explicitly enables higher classification."
    },
    {
      "threat_id": "T-4.1",
      "threat_name": "Insider Threat: User Silently Forwards Classified Message to External Account",
      "threat_category": "insider_threat",
      "ui_element": "Message context menu (assumed to have 'forward' option)",
      "threat_description": "A user with access to a classified channel could forward a message to a personal email account or external Slack workspace. If forwarding is not restricted or audited, this could be a silent exfiltration vector. The classification level on the message itself does not prevent forwarding.",
      "likelihood": "Low (requires motivated insider)",
      "impact": "Classified message exfiltrated to external account. Complete loss of control over information.",
      "recoverability": "Very Low - once forwarded externally, recovery is impossible.",
      "severity": "P1",
      "affected_users": "All users (insider threat)",
      "root_cause": "If forward/share functionality exists, it might not be restricted by classification level. Even if restricted, a user could use screenshot/copy-paste as alternative exfiltration method.",
      "example_scenario": "Disgruntled contractor with SECRET clearance forwards a message containing DoD project details to their personal Gmail account. They plan to sell the information to a foreign entity. The message is forwarded silently. Audit logs might not show the forward action if forwarding is not implemented as a logged action.",
      "recommended_mitigation": "DESIGN MITIGATION: Classified messages MUST NOT have a 'Forward' or 'Export' option in their context menu. If forwarding is essential, it should only be available within Mattermost to verified recipients (no external forwarding). AUDIT MITIGATION: Every message access (view, copy, forward, download) must be logged with user and timestamp. Security team reviews access logs weekly for suspicious patterns (user viewing many classified messages they don't need, then leaving organization).",
      "mitigation_effectiveness": "Removing forward option would eliminate this specific vector. But insider could use screenshot as alternative. Audit logging enables detection after the fact.",
      "residual_risk": "Screenshots and re-typing are harder to prevent. Insider could use screenshot. But audit logs of message viewing + subsequent absence of that user would be a red flag. Residual risk is Medium.",
      "implementation_notes": "Audit logs must track message access (view events) separately from sends/receives. This requires instrumentation in the message display component. Do not log classified message CONTENT; only log 'user viewed message in channel X', not the message text."
    }
  ],
  "risk_matrix": {
    "p1_threats": [
      {
        "threat_id": "T-1.2",
        "threat_name": "Incomplete Active Directory Clearance Data Leads to Over-Trust",
        "ui_element": "Pre-send confirmation modal clearance display",
        "recommended_mitigation": "Implement AD SLA + manual override button with audit trail + explanatory text for [CLEARANCE UNKNOWN]"
      },
      {
        "threat_id": "T-2.1",
        "threat_name": "Confirmation Modal is Dismissible Too Easily on Mobile",
        "ui_element": "Mobile pre-send confirmation modal",
        "recommended_mitigation": "Non-dismissible modal + HOLD gesture to send + haptic feedback + large buttons (44x44pt minimum)"
      },
      {
        "threat_id": "T-4.1",
        "threat_name": "Insider Threat: User Silently Forwards Classified Message to External Account",
        "ui_element": "Message context menu (forward option, if it exists)",
        "recommended_mitigation": "Remove forward option for classified messages; implement comprehensive message access audit logging"
      }
    ],
    "p2_threats": [
      {
        "threat_id": "T-1.1",
        "threat_name": "Copy/Paste Spillage of Classified Content",
        "ui_element": "Message composer textarea",
        "recommended_mitigation": "Copy-disabled mode for classified composers + visual warning"
      },
      {
        "threat_id": "T-3.1",
        "threat_name": "Admin Misconfigures Channel as Mixed-Classification",
        "ui_element": "Channel settings UI",
        "recommended_mitigation": "Max_classification field + admin warning modal + audit logging of over-level messages"
      },
      {
        "threat_id": "T-3.2",
        "threat_name": "Admin Accidentally Leaves a Channel Public",
        "ui_element": "Channel visibility setting",
        "recommended_mitigation": "[See full report for details]"
      },
      {
        "threat_id": "T-4.2",
        "threat_name": "Insider Threat: Social Engineering via Fake System Messages",
        "ui_element": "Message display (no clear indication of message source/authenticity)",
        "recommended_mitigation": "[See full report for details]"
      }
    ],
    "p3_threats": [
      {
        "threat_id": "T-3.3",
        "threat_name": "Desktop Notification Shows Classified Content in Plaintext",
        "ui_element": "Desktop notification popup",
        "recommended_mitigation": "[See full report for details]"
      }
    ]
  },
  "by_threat_category": {
    "data_spillage": [
      {
        "threat_id": "T-1.1",
        "threat_name": "Copy/Paste Spillage of Classified Content",
        "severity": "P2",
        "recommended_mitigation": "Copy-disabled mode + warning"
      },
      {
        "threat_id": "T-2.1",
        "threat_name": "Confirmation Modal is Dismissible Too Easily on Mobile",
        "severity": "P1",
        "recommended_mitigation": "Non-dismissible modal + HOLD gesture + haptic feedback"
      },
      {
        "threat_id": "T-3.3",
        "threat_name": "Desktop Notification Shows Classified Content in Plaintext",
        "severity": "P3",
        "recommended_mitigation": "Notifications must not include message content; show only sender + channel name"
      }
    ],
    "implicit_trust": [
      {
        "threat_id": "T-1.2",
        "threat_name": "Incomplete Active Directory Clearance Data Leads to Over-Trust",
        "severity": "P1",
        "recommended_mitigation": "AD SLA + manual override + explanatory text"
      }
    ],
    "misconfiguration": [
      {
        "threat_id": "T-3.1",
        "threat_name": "Admin Misconfigures Channel as Mixed-Classification",
        "severity": "P2",
        "recommended_mitigation": "Max_classification field + admin warning + audit logs"
      },
      {
        "threat_id": "T-3.2",
        "threat_name": "Admin Accidentally Leaves a Channel Public",
        "severity": "P2",
        "recommended_mitigation": "Visibility setting defaults to private; public requires explicit confirmation"
      }
    ],
    "insider_threat": [
      {
        "threat_id": "T-4.1",
        "threat_name": "Insider Threat: User Silently Forwards Classified Message to External Account",
        "severity": "P1",
        "recommended_mitigation": "Remove forward option; implement comprehensive access logging"
      },
      {
        "threat_id": "T-4.2",
        "threat_name": "Insider Threat: Social Engineering via Fake System Messages",
        "severity": "P2",
        "recommended_mitigation": "System messages visually distinct (different color, badge, or design)"
      }
    ]
  },
  "design_recommendations": [
    {
      "area": "Pre-Send Verification Modal",
      "principle": "Make it impossible for a user to send without explicitly confirming recipient list and classification level.",
      "specific_changes": [
        "Modal should NOT be dismissible by tapping outside or pressing Escape",
        "Recipient list should be prominent and scrollable (not hidden)",
        "Confirmation button should be large (44x44pt minimum) and require a HOLD gesture (2 seconds) instead of simple tap",
        "Add haptic feedback (vibration) on successful send confirmation",
        "On mobile, modal should be sized to fit screen without scrolling if possible; if scrolling is needed, recipient list is scrollable but buttons stay fixed at bottom"
      ],
      "priority": "P1"
    },
    {
      "area": "Clearance Verification",
      "principle": "Make clearance state visible and actionable. Provide escape hatch for incomplete AD data.",
      "specific_changes": [
        "When [CLEARANCE UNKNOWN] is displayed, add explanatory text: 'Clearance not found in directory. Contact [security officer] to verify.'",
        "Provide a manual override button for security officers: 'I have verified this user's clearance.' This logs the override action.",
        "Consider visual distinction for verified vs. unverified clearances (e.g., check mark for verified, question mark for unverified)"
      ],
      "priority": "P1"
    },
    {
      "area": "Message Composition UX",
      "principle": "Prevent accidental content spillage through copy/paste.",
      "specific_changes": [
        "For classified message composers, disable text selection/copy. User must paste content into Mattermost (cannot copy out).",
        "Display a persistent visual warning above classified composers: 'Do not copy/paste this content outside Mattermost.'",
        "Consider implementing a 'Compose in Draft' mode: classified messages are drafted but not sent until pre-send confirmation, reducing the window for accidental copying"
      ],
      "priority": "P2"
    },
    {
      "area": "Channel Configuration",
      "principle": "Prevent admin misconfiguration that mixes classification levels.",
      "specific_changes": [
        "Add a 'Maximum Message Classification' field to channel settings. Default to the channel's classification level (no overrides).",
        "When admin enables overrides (e.g., allows SECRET messages in a CONFIDENTIAL channel), show a warning: 'Users in this channel may post [SECRET] messages. Ensure ACL restricts membership to users with SECRET+ clearance.'",
        "Log all messages that are classified HIGHER than the channel's default. Security officers review these logs weekly."
      ],
      "priority": "P2"
    },
    {
      "area": "Message Access & Forwarding",
      "principle": "Prevent classified content exfiltration by insider threat.",
      "specific_changes": [
        "Remove 'Forward to External' option for classified messages. Forward to internal Mattermost recipients only (if forward is implemented at all).",
        "Implement comprehensive audit logging: track every user access to a classified message (view, copy, forward, download). Include timestamp and user ID.",
        "Security team reviews access logs weekly for patterns (user accessing many sensitive messages, then leaving org)."
      ],
      "priority": "P1"
    }
  ],
  "questions_for_product_team": [
    {
      "question": "What happens if a message is sent to a user who subsequently loses clearance (e.g., security incident, terminated employment)? Should that message be auto-redacted or logged as a compliance event?",
      "context": "This affects whether clearance verification is point-in-time (only at send) or ongoing (message periodically re-checked). Point-in-time is easier to implement but less secure."
    },
    {
      "question": "Should classified messages support forwarding at all, even within Mattermost? Or should they be view-only (no forward, no export)?",
      "context": "Forwarding is a convenience but creates exfiltration risk. Consider whether the use case (need to share a message with someone else) can be satisfied differently (e.g., grant access to the original channel instead)."
    },
    {
      "question": "Who is the 'security officer' mentioned in the UI (e.g., for manual clearance override)? Should this be a specific role, or can any admin do it? Should there be different overrides for different classification levels?",
      "context": "This affects RBAC (role-based access control) design and audit trail interpretation."
    }
  ]
}
```

## Condensed Usage Walkthrough

```
Input:
- Artifact: Complete PRD for message composition with pre-send verification
- Type: PRD
- Tier: IL5
- Focus: All (data_spillage, implicit_trust, misconfiguration, insider_threat)
- User population: tactical_ops
- Previous incidents: 2 message misdirection incidents, 1 admin misconfiguration

Analysis identifies:
- 8 threats (3 P1, 4 P2, 1 P3)
- P1: Incomplete AD clearance data, Mobile modal too dismissible
- P1: Insider forwarding exfiltration
- P2: Copy/paste spillage, Admin misconfiguration of mixed-classification channels, Admin accidentally leaves a channel public, Social engineering via fake system messages
- P3: Desktop notifications showing classified content
- Key mitigations: AD SLA + manual override, non-dismissible mobile modal + HOLD gesture, disable forward for classified messages, copy-disabled composer mode

Output: Design recommendations for Phase 1 before engineering starts.
```

## Design Principles

1. **The UI is a security control**: Backend encryption is necessary but not sufficient. If the UI enables user error, the system fails.
2. **Assume high cognitive load**: Tactical users are under time pressure. The UI must protect them, not require perfect judgment.
3. **Insider threat is real**: Do not assume all users are benign. Malicious insiders are often more dangerous than external attackers.
4. **Completeness of data matters**: If clearance data is incomplete, the verification control is broken. Address data integrity, not just UI.
5. **Recovery is a design requirement**: If a threat cannot be fully prevented, design detection and recovery mechanisms (audit logging, etc.).

## Troubleshooting

**Problem**: "Most of the threats are P3. This doesn't seem that risky."
**Solution**: You might be in a low-threat environment (IL2 office environment) vs. high-threat (IL5 classified). Re-assess likelihood given operational context. If users are truly low-stress and not under time pressure, P3 might be appropriate.

**Problem**: "Some of my mitigations require policy changes, not just UX design."
**Solution**: That's correct. Threat modeling often reveals that design alone cannot solve the problem. Flag policy dependencies explicitly (AD SLA, clearance data quality, admin training requirements) and escalate to leadership.

**Problem**: "The product team is pushing back on a P1 mitigation because it impacts UX."
**Solution**: Use the threat model output to quantify the risk. Show the example scenario and explain the operational/compliance consequence. Let the team make an informed decision about risk acceptance.
