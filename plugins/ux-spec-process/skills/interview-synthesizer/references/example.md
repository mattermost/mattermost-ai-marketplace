# Interview Synthesizer — Worked Example & Team Notes

Companion to the lean SKILL.md. Full example input + synthesized output for a bulk-onboarding research round, plus consumer-team notes and common pitfalls. Schemas: [`schema.md`](schema.md).

## Example Input

```json
{
  "raw_notes": "Interview 1 (Team Admin, IL4 command center):\n- Frustrated with per-user invite flow; says 'I have 50 new people joining each month from rotation'\n- Mentioned LDAP is their 'source of truth' but doesn't understand why Mattermost doesn't auto-sync\n- Security officer sits next to her; clarified that clearance is manually verified before LDAP groups are created\n- Quote: 'I need confidence that only cleared people are added. I can't afford a mistake.'\n- Observation: She spends ~15min per user invite, but stops to check org chart. Mental model: Mattermost should know org structure.\n\nInterview 2 (Team Admin, IL2 unclassified support unit):\n- Manages channel access by hand; keeps a side spreadsheet of who should be where\n- Quote: 'If a rule could just add the right people automatically, I'd use it every day'\n- Lower classification posture; operates with a more implicit trust model\n\nInterview 3 (Security Officer, IL4):\n- Concerned about audit trail for bulk operations\n- Mentioned incident: 'Someone added a contractor to a classified channel and we didn't catch it until audit'\n- Wants explicit record of WHO added WHOM, not just 'bulk add'\n- Quote: 'Every invite needs to be a record we can trace back'\n\nInterview 4 (End-user, IL4):\n- Doesn't care about how admins add people; just wants to know when new team members arrive\n- Observation: No expectation of control over who can join",
  "interview_count": 4,
  "participant_roles": ["team-admin", "security-officer", "end-user"],
  "research_questions": [
    "How do admins currently manage large user onboarding cohorts?",
    "What are the security/audit concerns around bulk operations?",
    "Do users want visibility into team membership changes?"
  ],
  "mission_context": "IL4"
}
```

## Example Synthesis Output

Based on the example input above.

### 1. TOP 5 NEEDS

1. **Bulk User Onboarding**
   - Finding: Admins regularly onboard large cohorts (10–100+ users/month) and need to add them faster than the current one-at-a-time invite flow allows.
   - Evidence: Two team admins explicitly stated this need. One quoted: "I have 50 new people joining each month from rotation" and "If a rule could just add the right people automatically, I'd use it every day." The other mentioned spending ~15min per user.
   - Urgency: CRITICAL
   - Operational Impact: Admins currently lose 7–12 hours/month to invites. They risk adding people to wrong teams or missing new hires during busy rotations.

2. **LDAP Sync Confidence**
   - Finding: Admins want LDAP to be the "source of truth" for user directories but lack confidence that it's fully integrated. They need assurance that Mattermost can automatically sync users without manual verification.
   - Evidence: One team admin mentioned "LDAP is their source of truth but doesn't understand why Mattermost doesn't auto-sync." This suggests mental model mismatch but also an implicit need: reduce manual verification burden.
   - Urgency: HIGH
   - Operational Impact: Loss of admin time on manual verification; risk of out-of-sync state causing confusion or unauthorized access.

3. **Clearance Verification Before Access**
   - Finding: Security officers need confidence that only cleared users are added to sensitive channels/teams. This is often a manual verification step currently.
   - Evidence: Security officer quoted: "I need confidence that only cleared people are added. I can't afford a mistake." Another mentioned an incident: "Someone added a contractor to a classified channel and we didn't catch it until audit."
   - Urgency: CRITICAL
   - Operational Impact: Compliance gap; risk of unauthorized access to classified information; ATO findings.

4. **Granular Audit Trails for Bulk Operations**
   - Finding: Security officers need to audit who added which users and when, with the ability to trace back bulk operations to individual adds.
   - Evidence: Security officer stated: "Every invite needs to be a record we can trace back." Mentioned incident where bulk add wasn't logged clearly enough.
   - Urgency: HIGH
   - Operational Impact: Compliance gap; inability to perform incident response or forensics on unauthorized access.

### 2. TOP 5 PAIN POINTS

1. **Manual Per-User Invite Flow at Scale**
   - Finding: Admins spend 15+ minutes per user on invites when onboarding cohorts of 50+ people. This is the single biggest friction point.
   - Evidence: Observed with two team admins. One paused frequently to check org chart before inviting, indicating extra cognitive load. Explicit statement: "I spend ~15min per user invite."
   - Severity: CRITICAL
   - Operational Consequence: 7–12 hours/month of admin time lost. Risk of errors during bulk onboarding (adding to wrong team, forgetting new hires).
   - Current Workaround: One admin uses a spreadsheet; manually invites from there. (This workaround still requires ~15min per user.)

2. **LDAP Configuration Complexity / Misalignment**
   - Finding: Admins don't fully understand LDAP sync behavior (e.g., whether it's real-time or batched) and aren't confident in its reliability.
   - Evidence: Admin stated: "I thought LDAP was real-time." Security officer clarified: "We batch-sync daily." This indicates a mental model gap.
   - Severity: HIGH
   - Operational Consequence: Loss of trust in automation; admins may manually verify after sync (adding time back) or incorrectly use LDAP thinking it's real-time.
   - Current Workaround: Manual verification after sync; checking org charts independently.

3. **Clearance Verification Overhead**
   - Finding: Security officers manually verify clearance before LDAP groups are created or before admins perform bulk adds. This is a gatekeeping step that adds time.
   - Evidence: Implied in security officer workflow (clearance verified before LDAP group creation). Concern: "I need confidence only cleared people are added."
   - Severity: HIGH
   - Operational Consequence: Friction in onboarding pipeline; delays for new users; risk that busy admins skip verification step and proceed anyway.
   - Current Workaround: Manual security officer sign-off on each bulk add request.

4. **Lack of Audit Trail Granularity**
   - Finding: Bulk operations aren't logged at the individual-add level; the system doesn't provide a granular trail of who was added by whom and when.
   - Evidence: Security officer mentioned incident: "Someone added a contractor to a classified channel and we didn't catch it until audit." Implies the audit trail was insufficient to catch the error early.
   - Severity: HIGH
   - Operational Consequence: Compliance gap; slower incident response; inability to perform forensics on unauthorized access.
   - Current Workaround: Manual incident review; post-hoc investigation of who might have added the contractor.

### 3. CONFLICTING MENTAL MODELS

1. **LDAP Sync Timing: Real-Time vs. Batched**
   - Conflict: [Team Admin expects] LDAP sync is real-time / automatic → new users appear in Mattermost instantly
   vs. [Security Officer reality] LDAP sync is batched (e.g., daily) and requires manual clearance verification before creating the LDAP group
   - Why It Matters: If the admin believes sync is real-time but it's actually batched, they may proceed as if users are already added when they aren't, creating a timing gap and compliance risk.
   - Which Roles Disagree: Team admin vs. security officer
   - Design Implication: The design must make sync timing explicit. Either (a) show a "sync queue" and estimated completion time, or (b) redesign to make sync truly real-time if feasible.

2. **Control Over Membership: Admin Autonomy vs. Verification Gate**
   - Conflict: [Team Admin expects] bulk-add capability; they can invite users independently
   vs. [Security Officer requires] clearance verification before any bulk add; security officer is the gate
   - Why It Matters: If the design enables admins to bulk-add without a verification step, security officers cannot gate access, creating an ATO finding.
   - Which Roles Disagree: Team admin vs. security officer
   - Design Implication: The design must include an explicit verification/approval step before bulk-add is executed. This may be a dialog ("These users have ≥ IL4 clearance: [list]") or a pre-sync validation gate.

3. **Responsibility for Clearance Checking: LDAP vs. Manual**
   - Conflict: [Team Admin implies] LDAP groups are the source of truth → if someone is in an LDAP group, they're cleared
   vs. [Security Officer knows] LDAP groups don't inherently encode clearance; clearance is verified separately before the group is created
   - Why It Matters: This is the most critical conflict. If admins believe LDAP groups = cleared users, they may skip manual verification, creating a security vulnerability.
   - Which Roles Disagree: Team admin vs. security officer
   - Design Implication: The design must make the clearance verification step explicit and non-bypassable. Options: (a) Require security officer approval before sync, (b) Display clearance status next to each user in bulk-add preview, (c) Require explicit confirmation of clearance for each user.

### 4. ZERO TRUST / CLASSIFICATION CONCERNS

1. **Unauthorized Access Risk in Bulk Operations**
   - Concern: Users can be added to sensitive channels/teams without proper clearance verification, creating a compliance gap.
   - Evidence: Security officer mentioned incident: "Someone added a contractor to a classified channel and we didn't catch it until audit." Also stated: "I need confidence that only cleared people are added. I can't afford a mistake."
   - Compliance Risk: Controls AC-2 (Access Control), AC-3 (Enforcement), AU-2 (Audit Events), SI-4 (Monitoring), IA-2 (Authentication), IA-4 (Identifier Management)
   - Design Implication: Bulk-add must include pre-execution verification of clearance. Options: (a) Require clearance status to be displayed/confirmed, (b) Integrate with a clearance database or service, (c) Require explicit security officer approval per bulk-add batch.

2. **Inadequate Audit Trail for Access Grants**
   - Concern: Bulk operations create a single audit event (e.g., "bulk-add 50 users") rather than granular entries per user, making incident forensics difficult.
   - Evidence: Security officer stated: "Every invite needs to be a record we can trace back." Mentioned incident where bulk add wasn't logged granularly.
   - Compliance Risk: Controls AU-2 (Audit Events), AU-6 (Audit Monitoring), AU-12 (Audit Generation)
   - Design Implication: Each user added (even in a bulk operation) must generate an individual audit log entry including: who added them, when, which team/channel, any clearance verification that occurred, and admin role/identity.

3. **Contractor / Temporary User Access Tracking**
   - Concern: There's no explicit mechanism to mark users as "contractors" or "temporary" and to restrict their access accordingly.
   - Evidence: Security officer incident: "Someone added a contractor to a classified channel." Implies contractor access wasn't distinguished from regular employee access.
   - Compliance Risk: Controls AC-2 (Access Control), CA-8 (Personnel Security Background Investigations)
   - Design Implication: Design should support contractor/temporary user labels and associated access restrictions. Alternatively, require explicit role-based clearance verification for non-employee types.

### 5. UNEXPECTED FINDINGS

1. **End-User Indifference to Membership Control**
   - Observation: End-users don't expect or want to control who can join their team. They only care about being notified when new arrivals occur.
   - Evidence: One end-user stated: "I don't care how admins add people; I just want to know when new team members arrive."
   - Why It's Unexpected: Commercial UX intuition would suggest users want membership control (e.g., "approve new members"). In this defense context, hierarchy and admin delegation are expected.
   - Potential Design Impact: The design can simplify end-user controls; instead of "approve membership," just show "new team member arrival notifications." This aligns with defense organizational culture.

2. **Mental Model: Org Chart as Source of Truth**
   - Observation: Admins instinctively check org charts during the invite process, suggesting they expect the system to "know" org structure and use it to guide invites.
   - Evidence: Observation: "She spends ~15min per user invite, but stops to check org chart frequently. Mental model: Mattermost should know org structure."
   - Why It's Unexpected: This suggests an opportunity for a deeper integration between Mattermost and HR/LDAP systems (beyond just user sync).
   - Potential Design Impact: Instead of building a bulk-invite text entry, consider building a "team builder" interface that pulls from org chart, letting admins click to add people by role/org unit.

### 6. RESEARCH GAPS

1. **Clearance Database Integration**
   - Question: Is there a single source of truth for user clearance levels (e.g., a cleared personnel database) that Mattermost can query before allowing access?
   - Why It Matters: Without this integration, clearance verification remains manual and doesn't scale. This is critical to the design.
   - Severity: CRITICAL
   - Recommended Resolution: Technical spike with security team to identify clearance data sources; follow-up interview with security officer on clearance workflow.

2. **Bulk-Add Volume & Frequency Across Roles**
   - Question: Do all team admins bulk-add 50+ users monthly, or is this specific to military rotation contexts? (i.e., how frequently does bulk-add happen, and in what contexts?)
   - Why It Matters: Affects priority; if 90% of admins do 2–5 user invites per month, bulk-add is a nice-to-have, not critical.
   - Severity: IMPORTANT
   - Recommended Resolution: Follow-up interview with 5–8 additional team admins across different org types and mission contexts.

3. **Current Bulk-Add Process (If It Exists)**
   - Question: Do admins currently have any bulk-add capability (e.g., in an admin API or legacy system) that we should preserve or replace?
   - Why It Matters: Understanding the current tool landscape helps design for consistency and migration path.
   - Severity: IMPORTANT
   - Recommended Resolution: Audit current tools and workflows with IT support and admin team.

4. **Mobile / Non-Desktop Workflow**
   - Question: Do any admins perform user invites on mobile, or is this exclusively a desktop task?
   - Why It Matters: Affects responsive design scope; if mobile is out of scope, the design can optimize for desktop.
   - Severity: NICE-TO-HAVE
   - Recommended Resolution: Observation/interview follow-up with a few admins on their typical environment.

5. **Notification Preferences for New Team Member Arrivals**
   - Question: How do users prefer to be notified of new team member arrivals (Mattermost in-app notification, email, Slack, etc.)? What information should the notification include?
   - Why It Matters: Affects the design of the team membership change notification feature (found under UNEXPECTED FINDINGS).
   - Severity: IMPORTANT
   - Recommended Resolution: Design spike with prototyping; low-fidelity testing with end-users.

## Notes for Consumer Teams

**Common Pitfalls:**

1. **Confusing Synthesis with Summarization** — Don't just restate the notes in bullet format. Synthesis means finding patterns across interviews, identifying conflicts, and surfacing insights that weren't explicit. If an admin mentioned "I check org chart before inviting" and another admin paused and checked an org chart during the interview, that's a pattern worth synthesizing: "Admins expect the system to know org structure."

2. **Over-Interpreting Single Mentions** — If one participant mentioned something once, it's a research gap, not a finding. A finding should appear across 2+ participants or be so consequential that even one mention is critical.

3. **Forgetting the "Why It Matters" Step** — Every finding should answer: "So what? How does this affect the design or the business?" If you can't answer that, it's not a finding yet.

4. **Missing Security Insights in Lower-Tier Systems** — Even IL2/IL3 systems have security concerns. Don't skip the SECURITY CONCERNS section. Users might not use the word "clearance," but they may talk about "contractors," "external partners," or "sensitive projects."

5. **Conflating All-Role Findings with Conflicts** — If all roles mention the same pain point (e.g., "the system is slow"), that's a shared need, not a conflict. A conflict requires incompatible expectations or responsibilities.

**For Researchers:**
- Before running the synthesis, read through your raw notes and mark each mention with a category tag (NEED, PAIN_POINT, SECURITY, etc.). This makes synthesis faster and more structured.
- Document the number of participants per role. If you interviewed 12 people but only 2 team admins, note that admin findings may not generalize.
- If you conducted multiple rounds of research, run synthesis after each round. Track how findings evolve.

**For Product Managers:**
Use the synthesized findings to build a requirements list. Each NEED and PAIN POINT should map to a requirement or a design principle. Each CONFLICTING MENTAL MODEL should map to a design challenge or UX pattern that resolves the conflict.

**For Designers:**
Use the findings to anchor your design decisions. When you make a major design decision, trace it back to a research finding. If your design doesn't address a CRITICAL finding, it's incomplete.

**For Security/Compliance:**
Review the SECURITY CONCERNS and RESEARCH GAPS sections. Flag any compliance gaps that need follow-up research before design review.
