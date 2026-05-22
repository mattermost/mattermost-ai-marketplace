# qa-analysis

Analyze a GitHub pull request for risk level and generate concrete QA recommendations.

Given a PR URL, this skill fetches the diff via `gh` CLI, computes blast radius across six dimensions (blast radius, complexity, regression surface, data integrity, security surface, infra/config), and returns a structured JSON risk assessment with prioritized QA recommendations.

## Usage

```text
/qa-analysis:qa-analysis https://github.com/owner/repo/pull/123
/qa-analysis:qa-analysis owner/repo#123
```

## Output

Returns a JSON object with:

- `risk_level` — LOW / MEDIUM / HIGH
- `risk_score` — numeric score 0.0–10.0
- `dimensions` — per-dimension scores (blast_radius, complexity, regression_surface, data_integrity, security_surface, infra_config)
- `risk_reason` — specific explanation referencing actual diff changes
- `areas_affected` — logical system areas touched
- `qa_recommendations` — up to 3 concrete, prioritized things to manually verify

## Requirements

- `gh` CLI installed and authenticated
- Read access to the target repository
