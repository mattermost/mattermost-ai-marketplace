# PRD Generator — Input & Output Schemas

Full JSON schemas for `prd-generator`. `mission_tier` uses the classification enum in [`${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §2](../../../.${CLAUDE_PLUGIN_ROOT}/templates/conventions.md); finding/risk severity uses the P1/P2/P3 scale (§1). The `risk_assessment.probability`/`impact` fields describe likelihood and consequence (not severity) and may stay qualitative.

## Input Schema

```json
{
  "problem_statement": {
    "type": "string",
    "description": "The business/operational problem this feature solves. Should include: what is broken, who is affected, what is the impact (operational/compliance/security)",
    "minLength": 100,
    "maxLength": 1000
  },
  "research_brief": {
    "type": "string",
    "description": "Summary of research findings that inform the PRD (user interviews, competitive analysis, threat model findings, etc.). Should include key insights about user workflows, pain points, and constraints.",
    "minLength": 200,
    "maxLength": 2000
  },
  "user_roles": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "role_name": {
          "type": "string",
          "description": "e.g., 'Fighter Pilot', 'Mission Coordinator', 'Security Administrator'"
        },
        "population_size": {
          "type": "integer",
          "description": "Estimated number of users in this role"
        },
        "primary_context": {
          "type": "string",
          "description": "Where/when they use Mattermost (e.g., 'tactical operations center, synchronous', 'distributed teams, asynchronous')"
        }
      },
      "required": ["role_name"]
    },
    "minItems": 1
  },
  "mission_tier": {
    "type": "string",
    "enum": ["IL2", "IL4", "IL5", "IL6", "UNCLASSIFIED", "MIXED"],
    "description": "Classification / impact level this feature must support. Canonical enum per ${CLAUDE_PLUGIN_ROOT}/templates/conventions.md §2; default IL5. MIXED = spans multiple impact levels (cross-domain).",
    "default": "IL5"
  },
  "compliance_frameworks": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": ["NIST_800-53", "NIST_800-207", "NIST_800-162", "DoD_ZT_RA", "DoDM_5200.01", "DISA_STIGs", "Section_508", "WCAG_2.1_AA", "Custom"]
    },
    "description": "Which compliance frameworks must this feature satisfy (defense scope per parent CLAUDE.md). If Custom, include in research_brief.",
    "minItems": 1
  },
  "timeline": {
    "type": "string",
    "enum": ["Phase_1_MVP", "Phase_2", "Phase_3_Plus", "TBD"],
    "description": "Which product phase is this feature targeted for? Affects scope and prioritization.",
    "default": "Phase_1_MVP"
  },
  "success_metrics_baseline": {
    "type": "object",
    "description": "Current state metrics (if available) to establish baseline for success criteria",
    "properties": {
      "current_incident_rate": {"type": "string"},
      "current_task_time": {"type": "string"},
      "current_error_rate": {"type": "string"}
    }
  },
  "known_constraints": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "description": "Known technical/organizational constraints (e.g., 'cannot modify CAC reader integration until Q4', 'mobile team has 2 engineers', 'no offline capability in Phase 1')",
    "minItems": 0
  },
  "required": ["problem_statement", "research_brief", "user_roles", "mission_tier", "compliance_frameworks"]
}
```

## Output Schema

```json
{
  "prd_metadata": {
    "title": "string (descriptive PRD title)",
    "date_generated": "ISO 8601 datetime",
    "version": "1.0.0",
    "mission_tier": "string (echoed from input)",
    "compliance_frameworks": ["array of frameworks"],
    "document_classification": "string (typically: 'For Official Use Only' or higher per mission tier)"
  },
  "executive_summary": {
    "bluf": "string (first 2-3 sentences answering: what problem, for whom, impact)",
    "problem_context": "string (background on why this is urgent now)",
    "proposed_solution_summary": "string (high-level description of the feature, not detailed)",
    "success_definition": "string (how we know this succeeded, in operational terms)"
  },
  "user_stories": [
    {
      "story_id": "US-1.1",
      "role": "string (Fighter Pilot | Mission Coordinator | Wing Security Officer)",
      "narrative": "As a [role], I need to [action] so that [outcome]",
      "acceptance_criteria": [
        {
          "criterion_id": "AC-1.1.1",
          "given": "string (context)",
          "when": "string (user action)",
          "then": "string (observable result)"
        }
      ]
    }
  ],
  "functional_requirements": [
    {
      "req_id": "FR-1.1",
      "category": "string (Message Composition | Classification Management | Recipient Verification | Audit | Mobile UX | etc.)",
      "role_affected": "string",
      "requirement": "string (SHALL/MUST/MUST NOT format)",
      "traces_to_story": "string (US-X.X reference)",
      "rationale": "string (why this is necessary, operational or compliance basis)",
      "acceptance_test": "string (how QA verifies this is met)"
    }
  ],
  "non_functional_requirements": {
    "security": [
      {
        "req_id": "NFR-S-1",
        "requirement": "string (SHALL format)",
        "compliance_control": "string (e.g., NIST SP 800-53 SC-7 / IA-2 / AU-2; DoDM 5200.01)",
        "verification_method": "string (penetration test | threat model review | code audit | etc.)"
      }
    ],
    "performance": [
      {
        "req_id": "NFR-P-1",
        "requirement": "string",
        "threshold": "string (measurable: e.g., <2 seconds latency @ 2Mbps)",
        "test_scenario": "string"
      }
    ],
    "accessibility": [
      {
        "req_id": "NFR-A-1",
        "requirement": "string",
        "wcag_criterion": "string (e.g., WCAG 2.1 1.4.3 Contrast (Minimum))",
        "verification_method": "string"
      }
    ],
    "mobile": [
      {
        "req_id": "NFR-M-1",
        "requirement": "string",
        "rationale": "string (why mobile is critical for this user population)"
      }
    ]
  },
  "success_metrics": [
    {
      "metric_id": "SM-1",
      "metric_name": "string",
      "baseline": "string (current state if known)",
      "target": "string (quantified goal)",
      "measurement_method": "string (how is this measured operationally?)",
      "owner": "string (who is responsible for tracking this?)"
    }
  ],
  "out_of_scope": [
    {
      "feature_name": "string (e.g., 'Scheduled Message Delivery')",
      "reason": "string (why it is deferred or excluded)"
    }
  ],
  "dependencies": [
    {
      "dependency_id": "D-1",
      "type": "string (External System | Mattermost Feature | Design System | Third Party | Blocker)",
      "description": "string",
      "owner": "string (team responsible for delivering)",
      "impact_if_delayed": "string (how does a delay affect this feature?)",
      "eta": "string (expected completion date or 'TBD')"
    }
  ],
  "risk_assessment": [
    {
      "risk": "string (identified risk)",
      "probability": "string (Low | Medium | High)",
      "impact": "string (if this goes wrong, what happens?)",
      "mitigation": "string (how do we prevent or recover from this?)"
    }
  ],
  "verification_with_pm": [
    {
      "question": "string",
      "context": "string (why this is uncertain)"
    }
  ]
}
```
