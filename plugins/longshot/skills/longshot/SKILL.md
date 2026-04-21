---
name: Longshot
description: Autonomous development pipeline for features, bug triage, and ideation. Drives planning, implementation, testing, quality, review, shipping, and post-ship via specialist agents. Runs end-to-end or resumes from any phase.
version: 4.6.0
tags:
  - planning
  - implementation
  - testing
  - code-review
  - shipping
  - orchestration
user_invocable: true
---

# Longshot

Autonomous development pipeline — covers feature work, bug triage, and ideation. Drives planning → implementation → testing → quality → review → ship → post-ship via specialist agents. Run the full cycle or any subset (`--skip-to`, `--only`).

### Reference Files

- [rules.md](rules.md) — cross-cutting invariants, git/security/retry/STOP protocols
- [principles.md](principles.md) — AI-Powered Development Process (the *why*)
- [profiles.md](profiles.md) — per-project build commands, layers, agent routing
- Phase files: [phase-0](phase-0-setup.md), [phase-1](phase-1-requirements.md), [phase-2](phase-2-plan.md), [phase-3](phase-3-implement.md), [phase-4](phase-4-test.md), [phase-5](phase-5-quality.md), [phase-6](phase-6-review.md), [phase-7](phase-7-ship.md), [phase-8](phase-8-post-ship.md)

## Usage

```
/longshot "Add drag-and-drop reordering to the pages sidebar"
/longshot "Fix pagination bug in channel search" --minimal
/longshot "Add OAuth2 with Google provider" --profile mm
/longshot "Refactor auth module" --dry-run
/longshot --continue                             # Resume where you left off
/longshot --skip-to implement                    # Resume from a specific phase
/longshot "Small fix" --solo --skip review,pr  # Quick serial mode, no PR
/longshot --status                               # Show current progress
/longshot --validate                             # Verify state consistency
/longshot --revert implement                     # Revert implementation phase
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
| 6 | Review | `/comprehensive-review:full-review` (2 rounds max) |
| 7 | Ship | commit, confirm, push + PR |
| 8 | Post-Ship | Jira status, fix version, QA steps |

Each phase is a **gate** — failure stops with a report and `--skip-to` suggestion.

### Flow (ingress / egress)

```
INGRESS                PIPELINE                    EGRESS
───────                ────────                    ──────

/longshot "desc" ───►  0: Setup
                       1: Requirements  ◄── --triage / --ideate
                       2: Plan          ──X gate fail ─────►  STOP
                       3: Implement     ──X retries  ──────►  STOP
                       4: Test          ──X retries  ──────►  STOP
                       5: Quality
                       6: Review        ──X MUST_FIX ──────►  STOP
                       7: Ship          ──[--skip pr]──────►  Local commit
                       8: Post-Ship ────────────────────────► Complete

RESUMPTION
──────────
--continue     ►  minimal P0  ►  current_phase   ►  normal flow
--skip-to <N>  ►  minimal P0  ►  phase N         ►  normal flow
--only <N>     ►  minimal P0  ►  phase N         ►  exit after

SKIP PATHS
──────────
--skip review     bypasses Phase 6 (5 → 7)
--skip pr         local commit only, no push/PR
--skip post-ship  stops after Phase 7

STOP TRIGGERS
─────────────
Phase 2  3+ MUST_FIX after 2 review rounds
Phase 3  review MUST_FIX after 2 rounds (warn on non-security; STOP on security)
Phase 4  same error signature fails 3 times
Phase 6  MUST_FIX remains (security never escapes; non-security warns)
any      --abort, context limit, irrecoverable error
```

## Flags

### Execution control

| Flag | Effect |
|------|--------|
| `--profile <name>` | Force a profile (bypass auto-detection). Accepts: `mattermost` (alias `mm`), `mattermost-mobile` (alias `mm-mobile`), `mattermost-plugin` (alias `mm-plugin`), `mattermost-plugin-playbooks` (alias `mm-playbooks`), `generic`. |
| `--minimal` | Lighter depth within phases (abbreviated plan, skip domain consultation) — phases themselves still run |
| `--solo` | Disable swarm mode — run serial subagent calls instead of agent teams |
| `--branch <name>` | Use specific branch name (overrides auto-generated, e.g. `MM-1234-the-thing`) |
| `--dry-run` | Show phase plan without executing |
| `--force` | Override concurrent run guard (proceed even if state.json shows an active run) |

### Phase control

| Flag | Effect |
|------|--------|
| `--continue` | Resume the most recent in-progress run (reads state.json, picks up at `current_phase`). Alias: `--resume` |
| `--skip-to <phase>` | Resume from a specific phase: `requirements`, `plan`, `implement`, `test`, `quality`, `review`, `ship`, `post-ship` |
| `--only <phase>` | Run only the specified phase without downstream phases (e.g., `--only quality` to re-run lint). A **minimal Phase 0** runs first to resolve `artifact_dir` — see [phase-0-setup.md § Minimal Phase 0 for `--only`](phase-0-setup.md#minimal-phase-0-for---only). |
| `--skip <phase>[,<phase>...]` | Skip phases or sub-steps. Tokens: phase names above + `pr` (skip push+PR within ship, keep local commit). Examples: `--skip review`, `--skip review,pr`. |
| `--revert <phase>` | Semantically revert a phase using recorded commit SHAs (git revert, not reset) |

### Phase 1 mode

| Flag | Effect |
|------|--------|
| `--triage` | Force triage mode (investigate a live-reported issue with minimal input) |
| `--ideate` | Force ideation mode (brainstorm and MVF-scope a new idea) |
| `--refs <token>[,<token>...]` | Reference-artifact handling across Jira, Confluence, PRDs, Feature/Technical Specs. Tokens: `strict` (treat missing refs or Epic fields as blocking gates — default is advisory); `create` (draft missing refs and prompt for confirmation before creating them); `update` (refresh incomplete/stale existing refs with drafted content, prompt before writing). Combine: `--refs strict,create,update`. |

### Run management

| Flag | Effect |
|------|--------|
| `--status` | Show current pipeline progress from state.json |
| `--list` | List all longshot runs in `~/.longshot/` with their status |
| `--validate` | Run validator agent to check state.json and artifact consistency |
| `--abort` | Mark the current run as aborted in state.json (does not revert code; use `--revert`) |
| `--clean` | Remove artifact directory for the current feature after `--abort` or manual cleanup |

### Quick Reference

| Scenario | Flags |
|----------|-------|
| Quick fix, no fuss | `--solo --minimal` |
| See the plan before executing | `--dry-run` |
| Resume where you left off | `--continue` |
| Resume from a specific phase | `--skip-to <phase>` |
| Re-run just one phase | `--only <phase>` |
| Skip PR creation | `--skip pr` |
| Skip Phase 6 review | `--skip review` |
| Force a profile | `--profile <name>` |
| Undo a phase | `--revert <phase>` |
| Check all active runs | `--list` |
| Abort and clean up | `--abort` then `--clean` |
| Triage a live-reported bug | `--triage` |
| Brainstorm and scope a new idea | `--ideate` |
| Create missing Jira/Confluence/PRD refs | `--refs create` |
| Update existing incomplete refs | `--refs update` |
| Block on missing refs | `--refs strict` |

## Profiles

See [profiles.md](profiles.md) for full profile definitions.

| Profile | Detection | Template |
|---------|-----------|----------|
| `mattermost` | `server/channels/` + `webapp/channels/` | MM Layer (Model→Store→App→API→Webapp) |
| `mattermost-mobile` | `android/` + `ios/` + `app/` + `@mattermost/react-native` | Mobile Feature template |
| `mattermost-plugin` | `plugin.json` + `server/` + `webapp/` | Plugin Feature template |
| `mattermost-plugin-playbooks` | `go.mod` mentions playbooks | Extends mattermost-plugin + GraphQL/i18n |
| `generic` | Fallback | Generic |

## Dependencies

All external skills, CLIs, MCPs, and domain agents are optional — pipeline degrades gracefully. Only `git` is required.

| Category | Items | Fallback |
|----------|-------|----------|
| CLIs | `git` (required), `gh`, `acli`, `make`, `npm`, `go` | `--skip pr`, manual Jira prompts, profile-specific warnings |
| MCP | Playwright, Figma, Atlassian | Manual checklist, skip design context, fall back to `acli` |
| Skills | `conductor:track-management`, `superpowers:writing-plans`, `comprehensive-review:full-review`, `coderabbit:review`, `figma:implement-design`, `accessibility-compliance:wcag-audit-patterns` | Inline templates, built-in agents |
| Domain agents | `simplicity-reviewer`, `api-reviewer`, etc. (soft references) | Skip that dimension |

### Recommended Plugin Repositories

- [claude-code-workflows](https://github.com/wshobson/agents) — domain agents and workflow skills
- [superpowers](https://github.com/obra/superpowers) — brainstorming, planning, debugging, TDD, worktrees

Install via your platform's plugin/skill mechanism. Claude Code example:

```bash
claude plugin marketplace add wshobson/agents
claude plugin marketplace add obra/superpowers
claude plugin install superpowers@superpowers
claude plugin install comprehensive-review@claude-code-workflows
claude plugin install agent-teams@claude-code-workflows
claude plugin install coderabbit@claude-code-workflows
```

Other platforms (Cursor, Copilot CLI, Codex, Gemini CLI, etc.) should install the equivalent skills/agents per their own tooling — the pipeline degrades gracefully when specific skills are absent.

---

## Gates

| After Phase | Gate | Behavior |
|-------------|------|----------|
| 2 (Plan) | Hard (M+) / Auto (XS/S) | M+: user confirms "Plan READY. Approve?"; XS/S: auto-proceed |
| 3 (Implement) | Soft (M) / Hard (L/XL) | L/XL: user confirms before testing |
| 4 (Test) | Soft | Auto-proceed after summary |
| 6 (Review) | Hard | User confirms "Review READY. Approve to ship?" |

Each gate creates a checkpoint commit recorded in `state.json.checkpoints[]` — these are the restore points for `--revert <phase>` (uses `git revert`, never `reset --hard`).

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Phase gate fails after max retries | Stop, print status summary, suggest `--skip-to <next-phase>` |
| Context approaching limit | Checkpoint to tracking file, suggest: "Run `/longshot --continue` in a new session" |
| Tests won't pass (3 fix attempts) | Stop, report failing tests, suggest manual intervention |
| Review won't reach READY (2 rounds) | Warn user, report remaining MUST_FIX, offer to proceed anyway |
| Agent/team spawn fails | Fall back to leader-only execution for that phase |
| Profile detection wrong | User can re-run with `--profile <name>` override |

Standard STOP message format and state.json transitions are defined in [rules.md §6](rules.md#6-stop-protocol).

---

## Output Format

At completion (or stop), print:

```markdown
## Longshot Summary: <feature-name>

### Pipeline Status
| Phase | Status | Duration |
|-------|--------|----------|
| Setup | COMPLETE | 2s |
| Requirements | COMPLETE | 15s |
| Plan | COMPLETE | 2m |
| Implement | COMPLETE | 5m |
| Test | COMPLETE | 1m |
| Quality | COMPLETE | 30s |
| Review | COMPLETE (1 SHOULD_FIX noted) | 2m |
| Ship | COMPLETE | 10s |
| Post-Ship | COMPLETE | 5s |

### Artifacts
- Plan: `<artifact_dir>/plan.md`
- Spec: `<artifact_dir>/spec.md`
- Branch: `MM-1234-<name>` (or prefixed by work type: `feat/…`, `fix/…`, `poc/…`, etc. if no ticket)
- PR: <url> (or "local commit only" if --skip pr)
- State: `<artifact_dir>/state.json`
- Findings: `<artifact_dir>/findings/phase6/review-report.md` (PR-ready summary) + `phase6/synthesis.md` (raw)

### Files Changed
| File | +/- |
|------|-----|

### Review Notes
- SHOULD_FIX items (deferred): [list if any]
- Warnings: [list if any]
```

---

