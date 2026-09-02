# ux-spec-process

A gated, **8-phase UX specification pipeline** for DoD / defense collaboration features (IL4/IL5/IL6).
An orchestrator drives a phase state machine, delegating each phase to a specialist agent that composes
a library of atomic skills. It takes a UX problem from a raw brain-dump to a publish-ready spec, with a
hard human gate at every phase.

The persona (Principal UX Designer, defense), compliance scope, complexity tiers, gate rules, and output
rules travel *inside* the plugin (the `defense-ux-context` skill) — no project `CLAUDE.md` setup required.

## The 8 phases

| Phase | Agent | Output | Gate |
|---|---|---|---|
| 1 — Discovery | `discovery-agent` | Problem Statement | ✅ |
| 2 — Research | `research-agent` | Research Brief (standards + competitive intel) | ✅ |
| 3 — PRD | `prd-agent` | PRD + threat model + pre-flight review | ✅ |
| 4 — Ideation | `ideation-agent` | Solution directions + scored matrix (sets `carried_forward[]`) | ✅ |
| 5 — UX Flows | `flow-agent` | Per-direction flow definitions + adversarial audit | ✅ |
| 6 — Prototype | `prototype-agent` | One code prototype per carried-forward direction | ✅ |
| 7 — Spec Writing | `spec-writer-agent` | UX spec draft (edge-case + traceability validated) | ✅ |
| 8 — Maintenance | `spec-updater` (skill) | Publish/maintain in Confluence (draft-only) | — |

Every gate is a hard stop requiring explicit human approval. Gate-4 records which solution directions
carry forward; that list drives one flow set (Phase 5) and one prototype option (Phase 6) per direction,
so decide it deliberately — carrying more directions multiplies Phase-6 build cost.

## Install

```
/plugin marketplace add mattermost/mattermost-ai-marketplace
/plugin install ux-spec-process@mattermost-ai-marketplace
```

## Usage

```
/ux-spec-process:spec-init <name>      # bootstrap specs/<slug>/ + state object + brain-dump
# …fill in specs/<slug>/00-brain-dump.md…
/ux-spec-process:spec-run <slug>       # run Phases 1–7 with a checkpoint after each phase
/ux-spec-process:spec-status <slug>    # current phase, gate status, artifacts
/ux-spec-process:spec-publish <slug>   # Phase 8: publish to Confluence as a DRAFT (confirmation required)
```

Individual phases can also be driven directly: `discover`, `research`, `prd`, `ideate`, `flow`,
`prototype`, `spec`. Reset a project with `spec-clean`.

## Prerequisites (all OPTIONAL)

- **Atlassian MCP (Confluence + Jira)** — used across the WHOLE pipeline. When connected, phases can READ
  requirements/epics/source pages as input (Discovery, Research, PRD) and Phase 8 can WRITE the spec to
  Confluence (draft-only, gated behind explicit confirmation). When absent, the pipeline runs entirely on
  local/manual inputs and `spec-publish` is unavailable. The agents use whatever Atlassian MCP is
  connected — no tool names are hardcoded.
- **Prototype sandbox** — used for **Phase 6 only**. Prototypes are built in a component sandbox at the
  workspace-relative path `meta.prototype_root` (default `prototype-playground/mattermost-proto-playground/`).
  Point `meta.prototype_root` at your own prototyping sandbox if it lives elsewhere. Phases 1–5 and 7 run
  without it.
- **Mermaid CLI (`mmdc`, from `@mermaid-js/mermaid-cli`)** — used by `html-spec-renderer` to pre-render the
  Phase 5 flowchart (and any other Mermaid diagram in the HTML living surface) to inline SVG at generation
  time, which the air-gap/IL-honest rules require. When `mmdc` is unavailable, `html-spec-renderer`
  automatically falls back to a hand-authored inline-SVG pattern — no diagrams are skipped, but authoring
  them by hand is more effort than letting `mmdc` generate them from Mermaid source.

## How it's wired

- **Orchestrator** (`spec-orchestrator`) manages the phase state machine, enforces the two-stage
  clarification gate, blocks advancement until gates are approved, and maintains the audit trail. It does
  not write artifacts — the phase agents do.
- **State integrity** — each project keeps `specs/<slug>/spec-state.json`. All writes go through the
  bundled `scripts/spec-state` CLI (schema-validated, timestamps stamped by the CLI). A PreToolUse hook
  blocks direct edits to the state file.
- **Operating context** — `skills/defense-ux-context/SKILL.md` is loaded first by the orchestrator and
  every phase agent. It carries the persona, compliance frameworks, tiers, interaction modes, gate/output
  rules, and prompt-injection policy.

## Compliance honesty

Automated accessibility validation is not wired in; `templates/a11y-manual-checklist.md` is a mandatory
manual pass (Tier 1–2). Specs claim **"designed for conformance"** with NIST 800-53/207/162, DoD Zero
Trust, Section 508 / WCAG 2.1 AA, and IL4/5/6 requirements — **never "compliant."**
