# Threat Modeler — Input & Output Schemas

Full JSON schemas for `threat-modeler`. Severity is the canonical P1/P2/P3 scale ([`${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §1](../../../.${CLAUDE_PLUGIN_ROOT}/templates/conventions.md)); `mission_tier` is the classification enum (§2). The `likelihood`/`impact`/`recoverability` fields are the qualitative *inputs* you weigh to land a severity — the published rating is always P1/P2/P3.

## Input Schema

```json
{
  "artifact_to_review": {
    "type": "string",
    "description": "The full text of the PRD, specification, or UI design document to threat model. Include user stories, requirements, UI flows, and acceptance criteria.",
    "minLength": 500,
    "maxLength": 20000,
    "required": true
  },
  "artifact_type": {
    "type": "string",
    "enum": ["PRD", "spec", "design_brief", "user_story_set", "ui_flow_description"],
    "description": "Type of artifact (affects analysis focus)",
    "required": true
  },
  "mission_tier": {
    "type": "string",
    "enum": ["IL2", "IL4", "IL5", "IL6", "UNCLASSIFIED", "MIXED"],
    "description": "Classification / impact level. Canonical enum per ${CLAUDE_PLUGIN_ROOT}/templates/conventions.md §2; default IL5.",
    "default": "IL5",
    "required": true
  },
  "focus_areas": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": ["data_spillage", "implicit_trust", "misconfiguration", "insider_threat", "all"]
    },
    "description": "Which threat categories to emphasize. Default: all",
    "default": ["data_spillage", "implicit_trust", "misconfiguration", "insider_threat"]
  },
  "user_population": {
    "type": "string",
    "enum": ["tactical_ops", "planning_team", "mixed", "administrators", "all_users"],
    "description": "Primary user context (affects threat likelihood assessment)",
    "default": "all_users"
  },
  "known_admin_capabilities": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "description": "What admins can do (e.g., 'export messages', 'create channels', 'modify access levels', 'see all private messages')",
    "minItems": 0
  },
  "previous_incidents": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "description": "Any known prior security incidents in this domain (e.g., 'user sent classified message to wrong channel', 'admin accidentally left channel public')",
    "minItems": 0
  }
}
```

## Output Schema

```json
{
  "threat_model_metadata": {
    "document_reviewed": "string (title of artifact)",
    "analysis_timestamp": "ISO 8601 datetime",
    "mission_tier": "string (echoed from input)",
    "total_threats_identified": "integer",
    "p1_count": "integer (P1 = blocker / MUST-FIX, per conventions §1)",
    "p2_count": "integer (P2 = should-fix)",
    "p3_count": "integer (P3 = nice-to-have)"
  },
  "executive_summary": {
    "key_findings": [
      "string (summary of most critical risks)"
    ],
    "overall_risk_posture": "string (e.g., 'ACCEPTABLE WITH MITIGATIONS', 'HIGH RISK, REQUIRES DESIGN CHANGES', 'CRITICAL: DO NOT RELEASE')",
    "recommendation": "string (proceed to design | request design changes | threat model again after changes | escalate to security team)"
  },
  "threats": [
    {
      "threat_id": "T-1.1",
      "threat_name": "string (e.g., 'Message Misdirection to Lower-Classification Channel')",
      "threat_category": "string (data_spillage | implicit_trust | misconfiguration | insider_threat)",
      "ui_element": "string (what part of the UI creates this risk?)",
      "threat_description": "string (detailed explanation of how threat manifests)",
      "likelihood": "string (Low | Medium | High | Very High - how likely is this to happen?)",
      "impact": "string (how severe is the consequence? classified data exposed, compliance violation, etc.)",
      "recoverability": "string (Low | Medium | High - can the damage be undone or detected quickly?)",
      "severity": "string (P1 | P2 | P3 - overall severity rating)",
      "affected_users": "string (who is at risk? pilots, admins, all users?)",
      "root_cause": "string (why does the UI enable this threat?)",
      "example_scenario": "string (concrete example of how threat could manifest)",
      "recommended_mitigation": "string (specific design change to reduce/eliminate risk)",
      "mitigation_effectiveness": "string (would mitigation eliminate or just reduce risk?)",
      "residual_risk": "string (what risk remains after mitigation?)",
      "implementation_notes": "string (any technical considerations for implementing mitigation?)"
    }
  ],
  "risk_matrix": {
    "description": "Summary table of all threats by severity",
    "p1_threats": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "ui_element": "string",
        "recommended_mitigation": "string"
      }
    ],
    "p2_threats": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "ui_element": "string",
        "recommended_mitigation": "string"
      }
    ],
    "p3_threats": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "ui_element": "string",
        "recommended_mitigation": "string"
      }
    ]
  },
  "by_threat_category": {
    "data_spillage": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "severity": "string",
        "recommended_mitigation": "string"
      }
    ],
    "implicit_trust": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "severity": "string",
        "recommended_mitigation": "string"
      }
    ],
    "misconfiguration": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "severity": "string",
        "recommended_mitigation": "string"
      }
    ],
    "insider_threat": [
      {
        "threat_id": "string",
        "threat_name": "string",
        "severity": "string",
        "recommended_mitigation": "string"
      }
    ]
  },
  "design_recommendations": [
    {
      "area": "string (e.g., 'Pre-Send Verification')",
      "principle": "string (design principle to apply)",
      "specific_changes": [
        "string (specific UX change)"
      ],
      "priority": "string (P1 | P2 | P3 - implement before release?)"
    }
  ],
  "questions_for_product_team": [
    {
      "question": "string",
      "context": "string (why this question matters for threat mitigation)"
    }
  ]
}
```
