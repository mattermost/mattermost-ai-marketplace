# teamimplement

Orchestrate phased software implementation using a team of engineers. Acts as a Senior Engineering Lead that delegates research, planning, implementation, code review, and QA validation to separate engineers following a pipeline defined in `.planning/PLAN.md`.

## Skills

| Skill | Description |
|-------|-------------|
| `teamimplement` | Orchestrate a multi-phase implementation plan with dedicated engineers at each stage |

## Usage

```
/teamimplement:teamimplement
```

### Prerequisites

Create a `.planning/PLAN.md` in your project with the phased implementation plan. The skill reads this as the source of truth for phase sequencing.

### Pipeline per Phase

1. **Research & Planning** -- an engineer researches and writes a prescriptive plan
2. **Implementation** -- a different engineer implements the plan and writes exhaustive tests
3. **Code Review** -- a third engineer reviews for plan adherence, concurrency, code quality, and test quality

After all phases pass, a QA validation loop deploys and tests end-to-end until zero issues remain.

## Author

Nick Misasi
