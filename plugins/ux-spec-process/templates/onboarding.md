# Onboarding — UX Spec Process

A gated, 8-phase pipeline that takes a UX problem from raw brain-dump to a publish-ready
specification for DoD / defense collaboration features. An orchestrator drives a phase state machine,
delegating each phase to a specialist agent that composes atomic skills. Every phase is a hard gate.

## The flow

1. `/ux-spec-process:spec-init <name>` — bootstrap a project folder under `specs/<slug>/`, a state
   object, and a brain-dump file.
2. Fill in `specs/<slug>/00-brain-dump.md`.
3. `/ux-spec-process:spec-run <slug>` — run Phases 1–7 with a checkpoint after each phase, or drive
   phases individually (`discover`, `research`, `prd`, `ideate`, `flow`, `prototype`, `spec`).
4. `/ux-spec-process:spec-status <slug>` — show current phase, gate status, artifacts.
5. `/ux-spec-process:spec-publish <slug>` — Phase 8: publish the spec to Confluence as a DRAFT
   (requires explicit confirmation).

The phases: **1 Discovery → 2 Research → 3 PRD → 4 Ideation → 5 UX Flows → 6 Prototype →
7 Spec Writing → 8 Maintenance/Publish.** Gate-4 records which solution directions carry forward
(`gates.phase_4.carried_forward[]`); that list drives one flow set (Phase 5) and one prototype option
(Phase 6) per direction, so decide it deliberately.

## Operating context

The persona, compliance scope, complexity tiers, interaction modes, gate/clarification rules, output
rules, and prompt-injection policy all live in the `defense-ux-context` skill
(`${CLAUDE_PLUGIN_ROOT}/skills/defense-ux-context/SKILL.md`). The orchestrator and every phase agent
read it first. You do not need a project `CLAUDE.md` for the pipeline to behave correctly.

## Prerequisites (both OPTIONAL)

- **Atlassian MCP (Confluence + Jira)** — optional, for the WHOLE pipeline. When connected, phases can
  READ requirements, epics, and source pages as input (Discovery, Research, PRD), and Phase 8 can
  WRITE the spec to Confluence (draft-only, gated behind explicit confirmation). When absent, the
  pipeline runs entirely on local/manual inputs and `spec-publish` is unavailable.
- **Prototype sandbox** — optional, for **Phase 6 only**. Phase 6 builds code prototypes in a
  component sandbox at the workspace-relative path `meta.prototype_root` (default
  `prototype-playground/mattermost-proto-playground/`). Point `meta.prototype_root` at your own
  prototyping sandbox if it lives elsewhere. Phases 1–5 and 7 run without it.

## State integrity

`specs/<slug>/spec-state.json` is orchestrator-managed. All writes go through the bundled
`${CLAUDE_PLUGIN_ROOT}/scripts/spec-state` CLI, which validates against the schema and stamps all
timestamps. A bundled PreToolUse hook blocks direct edits to the state file.
