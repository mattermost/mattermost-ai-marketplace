# Longshot

Autonomous development pipeline for features, bug triage, and ideation. Drives planning → implementation → testing → quality → review → ship → post-ship via specialist agents. Run the full cycle or any subset (`--skip-to`, `--only`).

## Usage

```
/longshot "Add drag-and-drop reordering to the pages sidebar"
/longshot "Fix pagination bug in channel search" --minimal
/longshot "Add OAuth2 with Google provider" --profile mm
/longshot "Refactor auth module" --dry-run
/longshot --continue                             # Resume where you left off
/longshot --skip-to implement                    # Resume from a specific phase
/longshot "Small fix" --solo --skip review,pr    # Quick serial mode, no PR
/longshot --status                               # Show current progress
/longshot --triage "pagination broken on channels page"
/longshot --ideate "what if we added real-time collaboration to the editor"
```

## Pipeline

| # | Phase | Activity |
|---|-------|----------|
| 0 | Setup | profile detection, branch, tracking file |
| 1 | Requirements | parse input, acceptance criteria, scope |
| 2 | Plan | research, consult agents, draft, review |
| 3 | Implement | TDD, auto-review (2 rounds max) |
| 4 | Test | unit + E2E + exploratory browser |
| 5 | Quality | lint, typecheck, i18n, auto-fix |
| 6 | Review | comprehensive multi-dimensional review (2 rounds max) |
| 7 | Ship | commit, confirm, push + PR |
| 8 | Post-Ship | Jira status, fix version, QA steps |

Each phase is a **gate** — failure stops with a report and `--skip-to` suggestion.

## Features

- **Three entry modes**: Standard (ticket/spec), Triage (live bug report), Ideation (brainstorm + MVF scoping)
- **Profile detection**: Auto-detects Mattermost server, mobile, plugin, playbooks, and generic project types (override with `--profile <name>`)
- **Scope-scaled gates**: XS/S auto-approve; M+ confirm plan; L/XL confirm before testing
- **Security-aware**: Detects security tickets, enforces sensitive-PR language/branch/test rules
- **Swarm mode**: Parallel agent teams when `TeamCreate` is available, serial fallback with `--solo`
- **Resumable**: `--continue`, `--skip-to <phase>`, `--only <phase>`, `--revert <phase>` via `state.json` + checkpoint commits
- **Reference-aware**: `--refs strict|create|update` for Jira Epic fields, Confluence, PRDs, and Technical Specs
- **Worktree-aware**: Works correctly in git worktrees
- **Flexible artifact storage**: `~/.longshot/` (local) → `.longshot/` (repo-relative) → PR-embedded (cloud)

## Prerequisites

- `git` (required)
- `gh` CLI (optional — for PR creation; without it use `--skip pr`)
- `acli` (optional — for Jira/Confluence integration)
- Profile-specific build tools: `make`, `npm`, `go` (optional — warns if missing)

## Recommended Companion Plugins

```bash
claude plugin install superpowers@superpowers
claude plugin install comprehensive-review@claude-code-workflows
claude plugin install agent-teams@claude-code-workflows
claude plugin install coderabbit@claude-code-workflows
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Core orchestrator — flags, pipeline, gates, output format |
| `rules.md` | Cross-cutting invariants — git safety, security handling, retry budgets, STOP protocol, swarm mode |
| `principles.md` | AI-Powered Development Process (from Mattermost Confluence) |
| `profiles.md` | Project profile definitions and build commands |
| `phase-0-setup.md` | Setup, state.json, toolchain probe, execution modes |
| `phase-1-requirements.md` | Triage, ideation, standard requirements, Epic/PRD checks |
| `phase-2-plan.md` | Plan drafting, test plan, domain consultation, review |
| `phase-3-implement.md` | TDD implementation, auto-review |
| `phase-4-test.md` | Unit, E2E, exploratory testing |
| `phase-5-quality.md` | Lint, security audit, i18n, API contracts, migration validation |
| `phase-6-review.md` | Comprehensive review — a11y, UX, concurrency, observability, security |
| `phase-7-ship.md` | Commit, PR creation, secret scan |
| `phase-8-post-ship.md` | Jira updates, release planning, backports |
