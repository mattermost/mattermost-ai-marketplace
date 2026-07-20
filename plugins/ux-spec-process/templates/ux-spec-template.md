# UX Spec: [Feature Name]

<!-- WRITING STYLE GUIDANCE:
- Write for engineers building the feature, not auditors reviewing it
- Describe behavior and outcomes, not click-by-click procedures
- Let mockups carry the visual specification; text annotates decisions, constraints, and non-obvious behavior
- State information once in the most natural location; don't repeat across sections
- Skip sections marked INCLUDE WHEN NEEDED if they carry no decisions or non-obvious information for this spec (mark as "N/A" or omit entirely)
- Document exceptions and edge cases, not standard interaction patterns (hover states, focus rings, keyboard nav)
- Use prose and bullets for behavior; reserve tables for structured data (settings, permissions) where they genuinely aid scanning
- Scale detail to complexity: a simple toggle needs 2 sentences, not a 12-row property table
- Compliance and accessibility are important inputs but should not dominate the spec's tone
-->

<!-- SECTION CLASSIFICATION:
REQUIRED — must appear in every spec:
  1.1 Problem Statement, 1.2 Feature Summary, 1.3 User Roles, 1.4 Scope
  3. Admin/Configuration UX (if feature has settings)
  4. End-User UX Flows
  9. Licensing & SKU

INCLUDE WHEN NEEDED — include only when they add value for this feature:
  1.5 Goals/Metrics — only for Tier 1 or when PM requests specific tracking
  2. Terminology — only when feature introduces genuinely new concepts not obvious from context
  5. UI Component Specs — only for novel components not in the design system
  6. Edge Cases — only for non-obvious scenarios; skip standard error handling
  7. Roles & Permissions — only when the permission model is genuinely complex
  8. Accessibility — only when feature introduces non-standard interaction patterns
  10. Analytics & Telemetry — only when PM requests specific event tracking

ALWAYS AVAILABLE AS SUB-PAGES (not in spec body by default):
  11. Open Questions
  12. Future Considerations
  13. Deprecated Explorations
  Appendix A — Compliance Reference (internal validation; attach as sub-page if requested)
  Appendix B — Revision History
-->

> **Status:** Draft | In Review | Approved
> **Last Updated:** YYYY-MM-DD
> **Author:** [Designer Name]

---

## Links

| Resource | Link |
|---|---|
| Figma Design File | [Link] *(optional read-only reference, if one exists)* |
| Code Prototype (Selected Option) | [Link to selected option route] |
| All Prototype Options | [Link to options index page] |
| PRD / Jira Epic | [MM-XXXXX](link) |
| Related Specs | [Spec Name](link) |
| Confluence Page | [Link] |

---

## Hero Image

> *Insert the primary screenshot from the selected prototype option. Browser screenshots of the running prototype are the default.*

![Hero Image](figma-frame-url)

---

## 1. Overview

### 1.1 Problem Statement

> *BLUF format: conclusion first, then the problem, then the consequence.*

[Problem statement from Phase 1 — ≤ 3 sentences]

### 1.2 Feature Summary

> *One paragraph. What does this feature do? How does it solve the problem? What is the user's mental model?*

[Feature summary]

### 1.3 User Roles

> *List only roles affected by this feature. Keep descriptions brief — one line per role.*

| Role | Relevant Actions |
|---|---|
| [Role] | [What they can do with this feature] |

### 1.4 Scope

**In Scope (This Phase):**
- [Requirement 1]
- [Requirement 2]

**Explicitly Out of Scope:**
- [Item 1] — *Reason: [why excluded]*
- [Item 2] — *Reason: [why excluded]*

**Deferred to Phase N:**
- [Item 1] — *Rationale: [why deferred, when expected]*

### 1.5 Goals *(INCLUDE WHEN NEEDED — Tier 1 specs or when PM requests specific tracking)*

> *Include only when meaningful baselines exist. Omit speculative metrics.*

| Goal | Success Metric |
|---|---|
| [Goal] | [Measurable metric with baseline] |

---

## 2. Terminology & Key Concepts *(INCLUDE WHEN NEEDED)*

> *Include only when the feature introduces genuinely new concepts that could be misinterpreted. Omit for features using established Mattermost terminology.*

| Term | Definition |
|---|---|
| [Term] | [Definition] |

---

## 3. Admin / Configuration UX

> *Describe each setting surface with enough detail to implement. Use a property table for settings with many fields; use prose for simple toggles. Reference mockups for visual layout.*

### 3.1 System Console Settings

**Setting Surface:** System Console > [Section] > [Subsection]

![Settings mockup](figma-frame-url)

[Describe settings behavior in prose. For each setting, note: label, default value, and what changes when toggled/modified. Only use a property table if the setting has complex options or validation rules that benefit from structured format.]

### 3.2 Team/Channel-Level Settings

*[If applicable — same approach: prose first, tables only when they aid scanning]*

---

## 4. End-User UX Flows

> *Describe what happens and why, not click-by-click procedures. Let mockups show the UI; text annotates decisions, constraints, and non-obvious behavior. Note error handling only when non-standard.*

### 4.1 [Flow Name]

![Flow mockup](figma-frame-url)

[Describe the behavior in 1-3 paragraphs. Cover: what triggers it, who sees it, what happens, and any non-obvious constraints. Reference the mockup for visual details.]

[Note non-standard error handling or edge cases if any.]

### 4.2 [Flow Name]

*[Repeat for each distinct flow]*

### Mobile

*Behavior is identical to web except: [list specific differences, or state "No differences."]*

---

## 5. Detailed UI Component Specifications *(INCLUDE WHEN NEEDED — novel components only)*

> *Include only for new components not already in the Mattermost design system. For standard components (buttons, modals, dropdowns), reference the design system and note only deviations. Let Figma carry visual specs.*

### Component: [Component Name]

[Describe the component's purpose, behavior, and any non-standard interaction patterns in prose. Reference the Figma component for visual details. Only include a property table if the component has genuinely complex configuration.]

---

## 6. Edge Cases & Special Scenarios *(INCLUDE WHEN NEEDED)*

> *Document only non-obvious scenarios that would surprise an experienced engineer. Skip standard error handling (network errors, loading states) unless the feature handles them in a non-standard way.*

| Scenario | Expected Behavior |
|---|---|
| [Non-obvious scenario] | [What happens] |

---

## 7. Roles & Permissions *(INCLUDE WHEN NEEDED — complex permission models only)*

> *Include a permissions matrix only when the feature has a genuinely complex permission model (multiple roles with different capabilities). For simple features, note permissions contextually in the flow descriptions (e.g., "visible to Channel Admins").*

| Action | [Role 1] | [Role 2] | [Role 3] |
|---|---|---|---|
| [Action] | Yes/No | Yes/No | Yes/No |

---

## 8. Accessibility Considerations *(INCLUDE WHEN NEEDED — non-standard interactions only)*

> *Section 508 / WCAG 2.1 AA compliance is mandatory for DoD deployments. Include this section only when the feature introduces non-standard interaction patterns. Standard components (buttons, modals, inputs) inherit accessibility from the design system — don't re-document ARIA labels, keyboard nav, or contrast ratios for standard patterns.*

[Document only accessibility considerations specific to this feature's non-standard interactions. E.g., custom drag-and-drop, novel keyboard shortcuts, complex focus management.]

---

## 9. Licensing & SKU

| Property | Value |
|---|---|
| **Feature Available In** | [Free / Professional / Enterprise / Enterprise with add-on] |
| **Upsell Trigger** | [What action surfaces the upsell] |
| **Upsell Message** | "[Exact upsell text]" |
| **Behavior Below Tier** | [What users see if they don't have the license] |

---

## 10. Analytics & Telemetry *(INCLUDE WHEN NEEDED — only when PM requests specific tracking)*

> *Include only events PM has specifically requested. Don't speculatively define analytics events.*

| Event Name | Trigger | Purpose |
|---|---|---|
| [event_name] | [When fired] | [Why we track it] |

---

## 11. Open Questions

> *All questions must have an owner and target resolution date.*

| # | Question | Owner | Target Date | Resolution |
|---|---|---|---|---|
| OQ-1 | [Question] | [Name] | [Date] | Pending / [Resolution] |

---

## 12. Future Considerations

> *Decisions explicitly deferred to future phases. Include enough context that a future designer can pick these up without re-discovering the reasoning.*

| # | Consideration | Deferred To | Rationale |
|---|---|---|---|
| FC-1 | [Item] | Phase N / TBD | [Why deferred] |

---

## 13. Deprecated Explorations

> *Approaches that were considered and rejected. Preserve with ~~strikethrough~~ to prevent re-litigation. Never delete — future team members need to know why these were abandoned.*

### ~~Approach: [Name]~~

~~[Description of the approach]~~

**Reason for deprecation:** [Why this was rejected]

**Decided by:** [Name, Role] | **Date:** [Date]

---

## Appendix A — Compliance Reference *(INCLUDE WHEN NEEDED — Tier 1 or access-control features; attach as sub-page)*

> *Internal validation artifact. Map design decisions to compliance controls only when the feature directly touches access control, classification, or audit logging. Attach as a Confluence sub-page, not in the spec body, unless explicitly requested.*

---

## Appendix B — Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | [Date] | [Author] | Initial draft |

---

**Spec ends.**
