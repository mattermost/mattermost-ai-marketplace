# test-evaluator

Reviews existing tests for efficacy, correctness, and coverage gaps. Evaluates whether tests actually test what they claim to, prioritizing real interactions over mocking and simulation. Produces a detailed report with verdicts and coverage gap analysis.

## Skills

| Skill | Description |
|-------|-------------|
| `test-quality-reviewer` | Evaluate test quality, efficacy, mock abuse, and coverage gaps |

## Usage

```
/test-evaluator:test-quality-reviewer
```

Point it at test files and it will read both the tests and the source code under test, then produce a detailed evaluation report.

## Author

Nick Misasi
