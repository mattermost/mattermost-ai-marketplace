# Interview Synthesizer — Input & Output Schemas

Full JSON schemas for `interview-synthesizer`. `mission_context` uses the classification enum in [`${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §2](../../../templates/conventions.md). The urgency/severity labels (CRITICAL/HIGH/MEDIUM) rank research findings; when these feed a gate finding, translate to the P1/P2/P3 scale in conventions §1.

## Input Schema

```json
{
  "raw_notes": {
    "type": "string",
    "description": "Concatenated interview/observation notes. Can include timestamps, researcher observations, direct quotes, and research question markers.",
    "minLength": 500,
    "maxLength": 50000
  },
  "interview_count": {
    "type": "integer",
    "description": "Total number of interviews/sessions included in raw_notes",
    "minimum": 1,
    "maximum": 100
  },
  "participant_roles": {
    "type": "array",
    "items": {"type": "string"},
    "description": "User roles represented in the research (e.g., ['team-admin', 'security-officer', 'end-user', 'it-support'])",
    "minItems": 1,
    "maxItems": 20
  },
  "research_questions": {
    "type": "array",
    "items": {"type": "string"},
    "description": "The framing questions the research was designed to answer (optional; helps prioritize findings)",
    "maxItems": 10
  },
  "mission_context": {
    "type": "string",
    "enum": ["IL2", "IL4", "IL5", "IL6", "UNCLASSIFIED", "MIXED"],
    "description": "Classification / mission context; helps filter which findings are high-priority. Canonical enum per ${CLAUDE_PLUGIN_ROOT}/templates/conventions.md §2; default IL5. (Use UNCLASSIFIED for non-classified research populations.)",
    "default": "IL5"
  }
}
```

## Output Schema

```json
{
  "top_5_needs": {
    "type": "array",
    "maxItems": 5,
    "items": {
      "type": "object",
      "properties": {
        "rank": {"type": "integer"},
        "title": {"type": "string"},
        "finding": {"type": "string"},
        "evidence": {
          "type": "object",
          "properties": {
            "roles_mentioned": {"type": "array", "items": {"type": "string"}},
            "frequency": {"type": "string", "enum": ["once", "2-3 times", "multiple", "unanimous"]},
            "quotes": {"type": "array", "items": {"type": "string"}}
          },
          "required": ["roles_mentioned", "frequency", "quotes"]
        },
        "urgency": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM"]},
        "operational_impact": {"type": "string"}
      },
      "required": ["rank", "title", "finding", "evidence", "urgency", "operational_impact"]
    }
  },
  "top_5_pain_points": {
    "type": "array",
    "maxItems": 5,
    "items": {
      "type": "object",
      "properties": {
        "rank": {"type": "integer"},
        "title": {"type": "string"},
        "finding": {"type": "string"},
        "evidence": {
          "type": "object",
          "properties": {
            "roles_mentioned": {"type": "array", "items": {"type": "string"}},
            "frequency": {"type": "string", "enum": ["once", "2-3 times", "multiple", "unanimous"]},
            "quotes": {"type": "array", "items": {"type": "string"}}
          },
          "required": ["roles_mentioned", "frequency", "quotes"]
        },
        "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]},
        "operational_consequence": {"type": "string"},
        "current_workaround": {"type": "string"}
      },
      "required": ["rank", "title", "finding", "evidence", "severity", "operational_consequence"]
    }
  },
  "conflicting_mental_models": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "conflict_statement": {"type": "string"},
        "roles_involved": {"type": "array", "items": {"type": "string"}},
        "why_it_matters": {"type": "string"},
        "design_implication": {"type": "string"}
      },
      "required": ["title", "conflict_statement", "roles_involved", "why_it_matters", "design_implication"]
    }
  },
  "security_concerns": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "concern": {"type": "string"},
        "evidence": {"type": "object"},
        "compliance_controls_at_risk": {"type": "array", "items": {"type": "string"}},
        "design_implication": {"type": "string"}
      },
      "required": ["title", "concern", "evidence", "compliance_controls_at_risk", "design_implication"]
    }
  },
  "unexpected_findings": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "observation": {"type": "string"},
        "evidence": {"type": "object"},
        "why_unexpected": {"type": "string"},
        "potential_design_impact": {"type": "string"}
      },
      "required": ["title", "observation", "evidence", "why_unexpected", "potential_design_impact"]
    }
  },
  "research_gaps": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "question": {"type": "string"},
        "why_it_matters": {"type": "string"},
        "severity": {"type": "string", "enum": ["CRITICAL", "IMPORTANT", "NICE-TO-HAVE"]},
        "recommended_resolution": {"type": "string"}
      },
      "required": ["title", "question", "why_it_matters", "severity", "recommended_resolution"]
    }
  }
}
```
