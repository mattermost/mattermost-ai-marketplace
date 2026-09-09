# Solution Scorer — Input & Output Schemas

Full JSON schemas for `solution-scorer`. The lean SKILL.md carries the procedure and output contract; this file is the canonical shape reference. The scoring block is the canonical `evaluation_matrix` object — the SAME shape is written to `solution_direction.evaluation_matrix` by ideation-agent (Phase 4) and emitted by option-presenter (Phase 6), so Phase-4 directions and Phase-6 options stay directly comparable.

## Input Schema

```json
{
  "prd_summary": {
    "type": "string",
    "description": "High-level summary of the PRD/problem being solved (1-2 paragraphs). Include: what problem, for whom, key requirements.",
    "minLength": 100,
    "maxLength": 500,
    "required": true
  },
  "approaches": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Name of the approach (e.g., 'Approach A: Message-Level Classification Markers')"
        },
        "description": {
          "type": "string",
          "description": "Detailed description of how this approach works, including technical/UX details (200-500 words)"
        },
        "assumptions": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Key assumptions this approach makes (e.g., 'Assumes Active Directory is accessible', 'Assumes users have reliable network')"
        }
      },
      "required": ["name", "description"]
    },
    "minItems": 3,
    "maxItems": 5,
    "required": true
  },
  "constraints": {
    "type": "object",
    "properties": {
      "mission_tier": {
        "type": "string",
        "enum": ["IL2", "IL3", "IL4", "IL5", "SAP"],
        "description": "Classification tier / assurance level"
      },
      "bandwidth_context": {
        "type": "string",
        "enum": ["broadband", "standard_network", "limited_bandwidth", "tactical_ops_2Mbps", "offline_capable"],
        "description": "Expected network conditions"
      },
      "user_population_size": {
        "type": "integer",
        "description": "Total users (affects scalability assessment)"
      },
      "phase_timeline": {
        "type": "string",
        "description": "When must this be ready? (e.g., 'Q2 2026 for Phase 1 MVP')"
      },
      "engineering_resources": {
        "type": "string",
        "description": "How many engineers can work on this? (e.g., '2 full-time for 8 weeks', 'part-time from existing team')"
      },
      "critical_blockers": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Known constraints that could affect feasibility (e.g., 'CAC integration not available until April', 'mobile team at capacity')"
      }
    }
  },
  "known_threats": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "threat_name": {"type": "string"},
        "severity": {"type": "string", "enum": ["P1", "P2", "P3"]},
        "relevant_approaches": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Which approaches does this threat affect?"
        }
      }
    },
    "description": "Threats from threat modeling (if available). Used to assess how well each approach mitigates risks.",
    "minItems": 0
  },
  "weighting_guidance": {
    "type": "object",
    "description": "Optional: how should criteria be weighted for this decision?",
    "properties": {
      "prioritize_compliance": {"type": "boolean"},
      "prioritize_simplicity": {"type": "boolean"},
      "prioritize_mobile": {"type": "boolean"},
      "prioritize_extensibility": {"type": "boolean"},
      "notes": {"type": "string"}
    }
  }
}
```

## Output Schema

```json
{
  "scoring_metadata": {
    "analysis_timestamp": "ISO 8601 datetime",
    "approaches_evaluated": "integer (3-5)",
    "mission_tier": "string (drives the default weight table)",
    "timeline": "string"
  },
  "evaluation_matrix": {
    "rubric_source": "${CLAUDE_PLUGIN_ROOT}/templates/conventions.md §3",
    "phase": "string (\"phase_4\" here; option-presenter writes \"phase_6\")",
    "mission_tier": "string",
    "criteria": [
      "Compliance Coverage",
      "Admin Cognitive Load",
      "End-User Cognitive Load",
      "Misconfiguration Risk",
      "Engineering Complexity",
      "Extensibility",
      "Mobile / Field Usability"
    ],
    "weights": {
      "Compliance Coverage": "float",
      "Admin Cognitive Load": "float",
      "End-User Cognitive Load": "float",
      "Misconfiguration Risk": "float",
      "Engineering Complexity": "float",
      "Extensibility": "float",
      "Mobile / Field Usability": "float"
    },
    "weights_rationale": "string (\"default IL5/IL6 table\" or the stated reason for any override)",
    "sum_weights": "float (Σ of the weights above; 9.25 for IL5/IL6, 8.25 for IL4/UNCLASSIFIED by default)",
    "scores": {
      "<approach_id_or_name>": {
        "Compliance Coverage": { "score": "integer (1-5)", "justification": "string (cites a PRD req, control, or threat)" },
        "Admin Cognitive Load": { "score": "integer (1-5)", "justification": "string" },
        "End-User Cognitive Load": { "score": "integer (1-5)", "justification": "string" },
        "Misconfiguration Risk": { "score": "integer (1-5)", "justification": "string" },
        "Engineering Complexity": { "score": "integer (1-5)", "justification": "string" },
        "Extensibility": { "score": "integer (1-5)", "justification": "string" },
        "Mobile / Field Usability": { "score": "integer (1-5)", "justification": "string" },
        "weighted": "float (Σ score×weight)",
        "normalized": "string (weighted ÷ sum_weights, rendered \"X.XX / 5.00\")"
      }
    },
    "recommended": "string (approach id/name with the best normalized score, subject to anti-gaming + tie-break)",
    "tie_break_applied": "boolean (true if winner chosen via the within-0.20 simpler-wins rule)",
    "anti_gaming_flag": "string|null (set when a high scorer carries a P1 compliance/security failure that forces RECONSIDER)"
  },
  "recommendation": {
    "recommended_approach": "string (name of approach)",
    "bluf": "string (2-3 sentence recommendation in BLUF format)",
    "primary_reason": "string (why this approach is best)",
    "key_advantages": [
      "string (advantage vs. other approaches)"
    ],
    "trade_offs": [
      {
        "trade_off": "string (what are we giving up?)",
        "rationale": "string (why is this trade-off acceptable for THIS situation?)"
      }
    ]
  },
  "risk_analysis": {
    "top_3_risks": [
      {
        "risk_rank": "integer (1-3)",
        "risk_name": "string",
        "description": "string (what could go wrong?)",
        "likelihood": "string (Low | Medium | High)",
        "impact": "string (what happens if this risk materializes?)",
        "mitigation": "string (specific action to reduce or detect this risk)"
      }
    ],
    "threat_model_coverage": "string (how well does this approach mitigate known threats from threat modeling?)",
    "unmitigated_threats": [
      {
        "threat_name": "string",
        "severity": "string (P1 | P2 | P3)",
        "why_unmitigated": "string (which approach would be needed to address this?)"
      }
    ]
  },
  "stakeholder_impact": {
    "for_engineering": "string (how much work is required? any concerns?)",
    "for_security": "string (does this approach adequately address compliance/threat concerns?)",
    "for_operations": "string (how easy is this to monitor/maintain?)",
    "for_end_users": "string (usability impact?)"
  },
  "scenario_testing": [
    {
      "scenario": "string (e.g., 'AD is down for 2 hours')",
      "impact_on_recommendation": "string (does the recommendation still hold?)",
      "mitigation_if_needed": "string"
    }
  ],
  "go_no_go_assessment": {
    "recommendation": "string (PROCEED | PROCEED WITH CONDITIONS | DO NOT PROCEED | RECONSIDER)",
    "reasoning": "string",
    "conditions_if_conditional": [
      "string (what must be true to proceed?)"
    ]
  }
}
```
