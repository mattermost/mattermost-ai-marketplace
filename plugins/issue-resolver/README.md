# issue-resolver

Autonomous issue resolution agent that investigates, plans, and fixes issues using sub-agents and browser-based validation without human intervention.

## Skills

| Skill | Description |
|-------|-------------|
| `issue-resolver` | Autonomously investigate, plan, fix, and validate issues end-to-end |

## Usage

```
/issue-resolver:issue-resolver
```

### How It Works

The agent orchestrates a four-phase pipeline, delegating all work to sub-agents:

1. **Parallel Investigation** — dedicated sub-agents reproduce each issue using browser tools, add debug instrumentation, and produce investigation reports
2. **Plan Synthesis** — a planning sub-agent groups related fixes into phased execution steps with acceptance criteria
3. **Phased Execution** — implementation sub-agents execute each phase, validate with browser tools, and iterate until acceptance criteria are met
4. **Final Validation** — a validation sub-agent performs full regression across all resolved issues

### Core Principles

- **Self-Verification**: Uses browser tools to validate — never asks the user to test
- **Delegation**: All investigation, implementation, and validation is performed by sub-agents
- **Persistence**: Iterates until issues are fully resolved, not just partially fixed
- **Observability**: Sub-agents add debug instrumentation to trace execution

## Author

Nick Misasi
