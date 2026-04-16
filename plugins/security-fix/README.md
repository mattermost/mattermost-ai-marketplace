# security-fix

Orchestrates test-driven fixes for Mattermost security tickets. The main agent acts as a Staff Security Engineer orchestrator and delegates every substantive step to sub agents: failing secure-behavior tests first, then implementation, then an edge-case hardening loop, then a review-ready PR whose public description does not leak exploit detail.

## Skills

| Skill | Description |
|-------|-------------|
| `security-fix` | TDD-driven security fix workflow: reproduce → fix → harden → PR |

## Usage

```
/security-fix:security-fix https://mattermost.atlassian.net/browse/MM-68140
```

Provide a `mattermost.atlassian.net/browse/<KEY>` URL. The orchestrator parses the issue key and fetches ticket details (title, description, acceptance criteria, suggested remediation, severity) via the Atlassian MCP or configured Jira integration.

### Workflow

1. **Phase 1 — Reproduction test only.** A sub agent adds tests that encode the expected secure behavior and must fail for the right reason against the current vulnerable code.
2. **Phase 2 — Fix to green.** A separate sub agent implements the fix (preferring the ticket's suggested remediation, or a safer/simpler alternative) until all Phase 1 tests pass.
3. **Phase 3 — Security review and edge cases.** A third sub agent explores adjacent handlers, shared helpers, and alternate roles/resources, adding failing tests for any gaps. If new failures surface, the orchestrator re-runs Phase 2, then Phase 3 again.
4. **Pull request.** The orchestrator opens a non-draft PR following `.github/PULL_REQUEST_TEMPLATE.md` when present, with a vague public description (area changed, not the exploit). Detailed context stays in Jira.

### Core Principles

- **Orchestration only** — the main agent never writes app code or tests directly.
- **TDD discipline** — red tests first, then fix, then harden.
- **Defense in depth** — Phase 3 extends coverage beyond the ticket's narrow repro.
- **Responsible disclosure** — public PR text avoids severity, exploit recipes, and precise vulnerable behavior.

## Author

Nick Misasi
