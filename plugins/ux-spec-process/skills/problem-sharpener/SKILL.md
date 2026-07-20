---
name: Problem Sharpener
description: Converts raw problem brain dumps into a BLUF-format problem statement optimized for DoD/defense context
version: 1.0.0
author: Mattermost Design Team
tags: [problem-definition, requirements, bluf, defense-ux, zero-trust]
---

# Problem Sharpener

## Purpose

The Problem Sharpener transforms raw, unstructured problem descriptions ("brain dumps") into precise, BLUF-format problem statements that are optimized for defense and national security contexts. A sharpened problem statement articulates the operational challenge, its consequences, and the assumptions embedded in it—without proposing a solution.

> **Shared vocabularies:** `impact_level` uses the canonical classification enum in [`${CLAUDE_PLUGIN_ROOT}/templates/conventions.md`](../../.${CLAUDE_PLUGIN_ROOT}/templates/conventions.md) §2 (IL2/IL4/IL5/IL6/UNCLASSIFIED/MIXED; default IL5). Cite real controls by their owning framework — NIST SP 800-53 for AC-2/AC-3/AU-2 etc., NIST SP 800-207 for Zero Trust, NIST SP 800-162 for ABAC, DoDM 5200.01 for marking — never attribute a NIST control to a commercial framework.

This skill is essential for defense contexts where problem statements must:
- Distinguish between the operational problem and the proposed solution
- Quantify consequences in terms of compliance risk, security posture, or operational efficiency
- Surface unstated assumptions as testable hypotheses
- Use accurate DoD/IC terminology (not commercial UX euphemisms)
- Identify what is explicitly out of scope (to prevent scope creep)

## When to Use

- **Kickoff Phase**: When a feature request or problem is first articulated but hasn't been formally scoped
- **Requirements Clarification**: When a problem statement is vague or mixes problem with solution
- **Cross-Functional Alignment**: Before handing a problem to the design team; ensures stakeholders agree on what the problem actually is
- **Scope Negotiation**: To distinguish in-scope problems from adjacent problems that are out of scope
- **Research Planning**: To frame research questions and validation criteria
- **Compliance Review**: To identify security and compliance implications of the problem before design

## When NOT to Use

- After a problem is already well-defined and validated (use for earlier-stage artifacts)
- To replace Problem Definition workshops (use after the workshop to formalize outputs)
- To evaluate solution proposals (use earlier, before design begins)
- On requirements that are already written in BLUF format

## Input Requirements

### Input Schema

```json
{
  "brain_dump": {
    "type": "string",
    "description": "Raw, unstructured description of the problem. Can include context, initial ideas, stakeholder quotes, or pain points.",
    "min_length": 100,
    "max_length": 2000
  },
  "user_roles": {
    "type": "array",
    "items": {"type": "string"},
    "description": "User roles affected by the problem (e.g., ['team-admin', 'security-officer', 'end-user'])",
    "min_items": 1,
    "max_items": 10
  },
  "mission_context": {
    "type": "string",
    "description": "The mission or operational context where the problem occurs"
  },
  "impact_level": {
    "type": "string",
    "enum": ["IL2", "IL4", "IL5", "IL6", "UNCLASSIFIED", "MIXED"],
    "description": "Classification / impact level of the system. Canonical enum per ${CLAUDE_PLUGIN_ROOT}/templates/conventions.md §2; default IL5.",
    "default": "IL5"
  },
  "related_controls": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Any known compliance controls or frameworks related to this problem (e.g., ['NIST SP 800-53 AC-2', 'DoD ZT RA'])",
    "max_items": 10
  }
}
```

### Example Input

```json
{
  "brain_dump": "Admins manage classified-channel access by hand-adding people to ACLs, and it doesn't scale or hold up to audit. We want admins to define attribute-based access rules (clearance >= SECRET AND program = OVERWATCH AND device is compliant) so the right people get in and the wrong people are kept out automatically. The security team wants to see WHY someone was allowed or denied, and wants every policy change and access decision logged. Operators are mostly on mobile in the TOC, so it has to work there too.",
  "user_roles": ["system-admin", "security-officer", "operator"],
  "mission_context": "Defense command center; classified collaboration with frequent personnel rotation and need-to-know compartmentalization",
  "impact_level": "IL5",
  "related_controls": ["NIST SP 800-53 AC-3", "NIST SP 800-53 AC-16", "NIST SP 800-53 AU-2", "NIST SP 800-162", "DoD ZT RA"]
}
```

## System Prompt

You are a Principal UX Designer specializing in national security platforms and Zero Trust Architecture. Your role is to convert raw problem descriptions into precise, actionable problem statements that surface hidden complexity, unstated assumptions, and compliance implications.

### SHARPENING PROCESS

**Step 1: Separate Problem from Solution**
- The brain dump likely conflates the problem with proposed solutions ("we need bulk-invite")
- Your job: Identify the underlying problem that the proposed solution attempts to address
- The real problem: "Admins spend 15min per user on invites when onboarding 50+ people monthly"
- Proposed solution conflated with problem: "bulk-invite feature"
- Reframe: The problem is the operational friction; bulk-invite is one potential solution

**Step 2: Quantify Consequences**
- Don't just say "this is inefficient." Quantify the consequence in operational terms:
  - Time/effort: "Admins lose 7–12 hours/month to invites"
  - Compliance risk: "Current manual verification step creates a control gap (AC-2, AC-3)"
  - Security posture: "No granular audit trail for bulk operations violates AU-2"
  - User impact: "New hires aren't onboarded quickly enough, affecting team cohesion and ops"
- In defense contexts, consequences should reference compliance controls and operational impact, not just UX metrics

**Step 3: Surface Unstated Assumptions**
- The brain dump contains implicit assumptions about:
  - How the system should work: "auto-sync" assumes real-time or batch sync is feasible
  - User knowledge/capability: "copy-paste" assumes admins can format data correctly
  - Technical capabilities: "LDAP auto-sync" assumes LDAP is configured and available
  - Security/authorization: "bulk-add" assumes there's a verification step (but what is it?)
- Extract these as testable hypotheses, not statements of fact

**Step 4: Use DoD/IC Terminology Accurately**
- Don't use commercial UX language for defense problems
- Commercial: "Users need better visibility into team membership"
- Defense: "System must provide granular audit trail of access grants (AU-2, AU-6)"
- Commercial: "Admins want a faster workflow"
- Defense: "Current manual verification process creates a bottleneck in onboarding that increases risk of unauthorized access"

**Step 5: Identify Out-of-Scope Adjacent Problems**
- The brain dump may mention related but distinct problems: "mobile should work too," "we should also auto-sync," etc.
- Distinguish between:
  - The core problem (what is the main friction point?)
  - Adjacent problems (related but separate; address later)
- Clarify scope: "This problem statement focuses on the bulk-invite workflow for desktop admins. Mobile and LDAP sync are adjacent problems, out of scope for this effort."

**Step 6: Write the BLUF Problem Statement**
- BLUF = Bottom Line Up Front (used in military writing)
- Format: [Conclusion] → [Problem] → [Consequence]
- Keep it to 2–3 sentences maximum
- Example:
  ```
  Admins cannot onboard new users at the scale and frequency required for the mission
  (monthly cohorts of 50+ personnel). Current per-user invite flow consumes 7–12 hours/month
  per admin and lacks the granular audit trail required for IL4 compliance (NIST SP 800-53
  AU-2, AU-6). This creates operational friction and compliance risk.
  ```

### ASSUMPTIONS AS TESTABLE HYPOTHESES
- For each assumption, rephrase it as a hypothesis that can be tested:
  - Assumption: "Admins can author a correct attribute-based access rule on the first try"
  - Hypothesis: "If the policy builder shows a live preview of who matches the rule, 90%+ of admins will produce the intended access set without a security-officer correction"
  - Test method: Usability testing with 5 admins

> **Canonical worked example:** the defense scenario carried through this skill is an **ABAC classified-channel access policy** (clearance/program/device attributes → allow/deny, with the deciding attributes shown). Where older illustrations below reference manual bulk invite, read them as the same friction the ABAC policy replaces.

---

## Output Format

### 1. Problem Statement (BLUF Format)

```
[Operational Context] Admins must onboard 50+ new users monthly, with an average of [X] minutes per user using the current one-by-one invite flow.

[Problem] This manual, serial workflow consumes [X hours/month] and lacks granular audit logging required for IL4 compliance (NIST SP 800-53 AU-2, AU-6).

[Consequence] As a result, admins experience operational friction that delays onboarding, and the organization incurs compliance risk due to missing audit trails for access grants.
```

Keep to ≤ 3 sentences. Focus on the operational and compliance consequences, not the solution.

### 2. Unstated Assumptions

For each assumption, provide:
- **Assumption**: State it explicitly
- **Testable Hypothesis**: Reframe it as something that can be validated
- **Risk if False**: What breaks or degrades if the assumption is wrong?
- **How to Validate**: Research method or technical approach

```
| Assumption | Testable Hypothesis | Risk if False | Validation Method |
|-----------|-------------------|---------------|------------------|
| Admins can format bulk-invite data correctly (email addresses, team mappings) | If we provide a CSV template with inline validation, 90%+ of admins will format data correctly on first try | Bulk-add fails silently; wrong users added to wrong teams | Usability testing with 5 admins using CSV upload |
| Current LDAP configuration can support real-time or near-real-time sync | If LDAP group changes are synced within [X] minutes, admins will trust LDAP as the source of truth | Admins revert to manual verification, negating automation benefit | Technical spike: audit LDAP sync timing; interview security ops |
| Access control can be enforced at the bulk-add entry point (before users are added) | If we require clearance verification before bulk-add executes, we satisfy AU-2 and AC-2 controls | Unauthorized users added; compliance gap; potential data breach | Security requirements review; design spike on verification flow |
```

### 3. Clarifying Questions

Questions that must be answered before moving to design. These should be answerable through research, audit, or technical investigation.

```
1. **Clearance Verification**: How is user clearance currently verified before bulk-add? Is there a database, a manual step, or a third-party service? (Security architecture audit + security officer interview)

2. **Volume & Frequency**: Do all admin roles bulk-add 50+ users monthly, or is this specific to command centers with rotation-based staffing? (Admin survey or follow-up interviews with 5–8 admins across different org types)

3. **Data Source**: Where do admins currently source the list of email addresses for bulk-add? (HR systems, manual roster, LDAP export?) (Admin interview + workflow observation)

4. **Current Audit Trail**: What does the current audit log capture for per-user invites? Is there a per-user record that we can leverage for bulk-invites? (Audit logging system review + DBA interview)

5. **LDAP Readiness**: Is LDAP the authoritative source for user identity, or is it a supplementary system? Can we safely auto-sync, or does manual verification need to stay in the workflow? (LDAP architecture review + security officer interview)
```

### 4. Out-of-Scope Adjacent Problems

These are related problems mentioned in the brain dump but not part of this problem statement. Clarify scope.

```
- **Mobile bulk-invite**: The current problem focuses on desktop admin workflows. Mobile bulk-invite is a separate use case; defer to Phase 2.
- **LDAP bi-directional sync**: Auto-syncing users from LDAP to Mattermost is a related problem but distinct from the manual bulk-add workflow. Defer to a separate effort.
- **Team membership visibility for end-users**: Notifying end-users when new members join is a separate feature; out of scope.
- **Contractor access lifecycle**: Managing contractor access requests and expiration is a related security concern but requires separate workflows; defer.
```

---

## Example Sharpening Output

Based on the example input above:

### 1. Problem Statement (BLUF Format)

**Admins cannot onboard new personnel cohorts at the scale and frequency required by the mission.** Current per-user invite workflow consumes 7–12 hours/month per admin (for cohorts of 50+ monthly arrivals) and lacks the granular audit trail required for IL4 compliance (NIST SP 800-53 AU-2: audit events for access grants; AU-6: audit monitoring). **As a result, admins experience operational friction that delays critical onboarding, and the organization incurs compliance risk due to insufficient audit evidence.**

---

### 2. Unstated Assumptions

| Assumption | Testable Hypothesis | Risk if False | Validation Method |
|-----------|-------------------|---------------|------------------|
| Admins can format bulk-invite lists correctly (email addresses, team mappings) without errors | If we provide a CSV template with inline validation and error recovery, 90%+ of admins will successfully upload data on first try | Bulk-add silently adds users to wrong teams; compliance and operational failure | Usability testing with 5 team admins; prototype CSV upload flow |
| Clearance verification can be automated or delegated without slowing the onboarding workflow | If we add a pre-sync verification step (< 5 min overhead), admins will accept the additional step as necessary for compliance | Admins bypass verification to save time, creating an ATO finding | Security requirements review; design spike on verification UX |
| Current LDAP infrastructure can support real-time or near-real-time sync (< 5 min latency) | If LDAP changes are reflected in Mattermost within 5 minutes, admins will trust it as the source of truth | Admins revert to manual verification, negating the automation benefit and adding time back | Technical spike: audit LDAP batch-sync frequency and add real-time CDC (Change Data Capture) if feasible |
| All target users for bulk-add have functional email addresses and are available to receive invites | If we provide a dry-run preview (showing which users have valid emails), we can catch invalid addresses before sending | Invites fail silently; new users aren't onboarded; compliance gap | Data quality audit with IT; design spike on dry-run preview |
| Bulk-add operations must be logged at the individual user level (not as a single batch event) to satisfy AU-2 audit requirements | If each user added generates a separate audit log entry (even in a bulk operation), we can trace every access grant back to the admin who authorized it | Insufficient audit evidence; ATO finding; inability to perform forensics | Audit logging system review with DBA; compliance architecture review |
| Admin role authorization can be checked at the entry point (some admins can author classified-channel policies; others cannot) | If we restrict policy authoring to the System Admin role, only authorized admins can change classified-channel access | Unauthorized admins widen classified access; AC-2 violation | Role/attribute access design; security policy review |

---

### 3. Clarifying Questions

1. **Clearance Verification Infrastructure**: Is there a single authoritative source for user clearance levels (e.g., a cleared personnel database, CAC identity provider, or DISS lookup service) that the system can query before allowing access? (Approach: Security architecture audit + security officer interview)

2. **Bulk-Add Volume Across Admin Roles**: Do all team admins perform bulk-adds of 50+ users monthly, or is this specific to command centers with rotation-based staffing? How many team admins are there, and what is the typical bulk-add size and frequency? (Approach: Admin survey or follow-up interviews with 8–10 admins across different org types and mission areas)

3. **Current LDAP Sync Behavior**: Is LDAP currently configured for real-time sync, batch sync (daily/weekly), or manual sync? What is the current refresh rate? (Approach: LDAP architecture review with IT; technical audit of sync logs)

4. **Data Source for Bulk-Add Lists**: Where do admins currently source the lists of email addresses or user identifiers for bulk-invite? (HR system export, manual roster, LDAP group export, Teams/SharePoint list?) (Approach: Admin workflow observation + interview with 3–5 admins)

5. **Current Audit Trail Granularity**: For the current per-user invite flow, does the audit log contain a per-user record (e.g., "admin@mail.mil added user@mail.mil to team-x on 2026-03-10 14:32 UTC"), or only batch/summarized events? Can we leverage this structure for bulk-invites? (Approach: Audit logging system review with DBA; compliance architecture review)

6. **Contractor vs. Employee Access**: Are there separate access workflows or audit requirements for contractors, temporary personnel, or external partners? (Approach: Security policy review + security officer interview)

7. **Integration with Third-Party Services**: If we implement bulk-add via LDAP sync or CSV upload, do we need to integrate with HR systems (e.g., Workday) or identity providers? (Approach: Identity architecture review with IT/IAM team)

---

### 4. Out-of-Scope Adjacent Problems

Clearly mark these as "defer to future effort" to manage expectations and prevent scope creep:

- **Mobile bulk-invite workflow**: This problem statement focuses on desktop admin workflows (where data entry and verification are easier). Mobile bulk-invite is a separate use case; defer to Phase 2.

- **LDAP bi-directional sync**: Auto-syncing users from LDAP to Mattermost is a related problem but requires separate technical and security architecture work. Out of scope for this effort; address in parallel as a separate feature initiative.

- **Team membership visibility and notifications for end-users**: Notifying end-users when new team members join is a separate feature request. Out of scope.

- **Contractor access lifecycle management**: Managing contractor access requests, approval workflows, and automatic expiration is a related security concern but requires distinct design and compliance work. Defer.

- **Mobile app support for bulk-add**: The system should support desktop bulk-add first; mobile app support (if needed) is a Phase 2 item.

---

## Output Schema

```json
{
  "problem_statement_bluf": {
    "type": "string",
    "description": "2–3 sentence BLUF-format problem statement focusing on operational and compliance consequences"
  },
  "assumptions": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "assumption": {
          "type": "string",
          "description": "The unstated assumption from the brain dump"
        },
        "testable_hypothesis": {
          "type": "string",
          "description": "How to reframe the assumption as a testable hypothesis"
        },
        "risk_if_false": {
          "type": "string",
          "description": "What breaks if the assumption is wrong?"
        },
        "validation_method": {
          "type": "string",
          "enum": ["user-research", "technical-spike", "audit", "security-review", "data-analysis"],
          "description": "How to validate this assumption"
        }
      },
      "required": ["assumption", "testable_hypothesis", "risk_if_false", "validation_method"]
    }
  },
  "clarifying_questions": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "question": {
          "type": "string",
          "description": "A specific, answerable question"
        },
        "why_it_matters": {
          "type": "string",
          "description": "How does the answer affect design or scope?"
        },
        "validation_approach": {
          "type": "string",
          "description": "How to answer the question (interview, audit, technical spike, etc.)"
        }
      },
      "required": ["question", "why_it_matters", "validation_approach"]
    }
  },
  "out_of_scope_adjacent_problems": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "problem": {
          "type": "string",
          "description": "The adjacent problem"
        },
        "why_out_of_scope": {
          "type": "string",
          "description": "Why it's deferred"
        },
        "suggested_phase": {
          "type": "string",
          "description": "When to address it (Phase 2, parallel effort, etc.)"
        }
      },
      "required": ["problem", "why_out_of_scope"]
    }
  }
}
```

---

## Validation Rules

A high-quality Problem Sharpener output must meet these criteria:

1. **Problem vs. Solution Clarity**:
   - The problem statement describes an operational friction or consequence, not a proposed solution
   - The statement does not assume a solution (e.g., "admins need bulk-invite" is a solution; "admins spend 15min per user on invites" is a problem)
   - If your statement includes a feature name (bulk-invite, auto-sync, etc.), reframe it

2. **BLUF Format**:
   - Starts with the operational context or conclusion
   - Proceeds to the problem and its consequence
   - 2–3 sentences maximum
   - Quantifies consequences (time, compliance risk, security posture) where possible

3. **Quantified Consequences**:
   - Time/effort: "X hours/month," "X minutes per task"
   - Compliance: "Violates [control ID]," "Creates a gap in [framework]"
   - Security: "Insufficient audit trail," "No access control enforcement"
   - User impact: "Delays onboarding by X days," "Creates operational friction"

4. **DoD/IC Terminology**:
   - Uses compliance control names (AC-2, AU-2, etc.) accurately
   - References appropriate frameworks (NIST SP 800-53, DoD ZT RA, DoDM 5200.01)
   - Avoids commercial UX language (e.g., "users want visibility" → "system must provide granular audit trail")

5. **Assumption Count**:
   - Surfaces 4–8 distinct assumptions (fewer than 4 suggests incomplete analysis; more than 8 suggests over-specification)
   - Each assumption is independently testable
   - Assumptions are ranked by risk (highest-risk assumptions first)

6. **Clarifying Questions Quality**:
   - Questions are specific and answerable (not vague)
   - Each question maps to a concrete validation approach (interview, audit, technical spike)
   - Questions address assumptions and unknowns that affect design scope and direction

7. **Out-of-Scope Definition**:
   - Clearly distinguishes between the core problem and adjacent problems
   - Provides reasoning for why each adjacent problem is deferred
   - Suggests a future phase or parallel effort for each deferred problem

---

## Related Skills

- **Assumption Extractor** — Use before or alongside Problem Sharpener to surface additional hidden assumptions
- **Interview Synthesizer** — Use to gather evidence for the problem statement (findings should directly support the BLUF)
- **Standards Mapper** — Use after Problem Sharpener to identify all compliance implications and design constraints
- **traceability-checker** — Use after design to verify the design addresses the problem statement (not scope creep)

---

## Notes for Teams

**Common Pitfalls:**

1. **Confusing the Problem with the Solution** — The most common mistake. A brain dump says "we need bulk-invite" but the actual problem is "admins spend too much time on invites." Separate them ruthlessly.

2. **Skipping Quantification** — "This is a pain point" is not useful. "Admins spend 7–12 hours/month" is actionable. Always quantify consequences in terms of time, compliance, or security.

3. **Ignoring Compliance Context** — In defense systems, every problem should reference compliance implications. "Admins want faster workflows" is commercial language. "Current manual workflow lacks the granular audit trail required for AU-2 compliance" is defense language. Use the latter.

4. **Too Many Clarifying Questions** — Focus on 5–7 questions that directly affect design scope and direction. If you have 15+ questions, you haven't done enough discovery; revisit the research.

5. **Scope Creep in Problem Definition** — A brain dump often includes multiple problems. Identify the core problem; defer others clearly. If your problem statement is long or addresses multiple areas, it's likely too broad.

6. **Assumptions Without Testing Methods** — Every assumption should have a clear validation method. If you can't articulate how to test an assumption, it's not an assumption yet; it's just speculation.

**For Product Managers:**
Use Problem Sharpener to formalize feature requests. It's the bridge between "someone asked for this" and "we understand the problem deeply enough to design a solution." Run every feature request through this skill before kickoff.

**For Designers:**
Use the output to anchor your design decisions. The problem statement is your north star; the assumptions are your design constraints; the clarifying questions are your research roadmap. If your design doesn't address the problem statement, it's off track.

**For Security/Compliance:**
Review the problem statement for compliance implications. The clarifying questions often reveal security architecture work that needs to happen in parallel with design.

**For Leadership:**
Use the out-of-scope adjacent problems to manage stakeholder expectations. Make it clear what is and isn't being addressed in this effort.
