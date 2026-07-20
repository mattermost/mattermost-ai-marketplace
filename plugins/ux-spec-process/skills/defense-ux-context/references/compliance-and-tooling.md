# Compliance & Tooling Reference (on-demand)

Companion to `SKILL.md`. Read this only when you need the framework detail or the full registry —
it is not required every turn.

## Compliance frameworks — where each applies

| Framework | Applies to |
|---|---|
| **NIST 800-53** | Security & privacy control baselines; map UI controls (audit, session, access) to control families |
| **NIST 800-207** | Zero Trust Architecture; per-request authorization, never implicit trust — drives friction-vs-assurance trade-offs |
| **NIST 800-162** | Attribute-Based Access Control (ABAC); attribute-driven visibility/permission surfaces at the UI layer |
| **DoD Zero Trust Reference Architecture** | Pillars (user, device, network, application, data); align UX to the target ZT maturity |
| **Section 508 / WCAG 2.1 AA** | Accessibility conformance for federal systems; manual checklist is mandatory (Tier 1–2) — no automated gate wired |
| **IL4 / IL5 / IL6** | DoD Impact Levels; classification handling, spillage guardrails, air-gapped/bandwidth-constrained behavior |
| **ACP 240** | Allied cross-domain / releasability handling for coalition contexts |
| **EO 14028** | "Improving the Nation's Cybersecurity"; Zero Trust + software supply-chain expectations |

Specs claim **"designed for conformance,"** never **"compliant."**

## System architecture (3 layers)

1. **Master orchestrator** — `spec-orchestrator`: drives the 8-phase state machine via the Spec State
   Object (`${CLAUDE_PLUGIN_ROOT}/templates/spec-state-object.json`); entry point for all new spec work.
2. **Phase agents** — one specialist per generative phase.
3. **Atomic skills** — composed by the agents.

"8-phase" = 7 generative gated phases (1–7) + 1 maintenance/publish step (Phase 8, skill-driven, no agent).

### Phase agents

| Phase | Agent | Output |
|---|---|---|
| 1 — Discovery | `discovery-agent` | Problem Statement |
| 2 — Research | `research-agent` | Research Brief (standards + competitive intel) |
| 3 — PRD | `prd-agent` | PRD + threat model + pre-flight review |
| 4 — Ideation | `ideation-agent` | Solution directions + scored evaluation matrix |
| 5 — UX Flows | `flow-agent` | Per-direction flow definitions + flow/security/nav audit + feedback disposition |
| 6 — Prototype | `prototype-agent` | One code prototype per carried-forward direction (built in the sandbox at `meta.prototype_root`) |
| 7 — Spec Writing | `spec-writer-agent` | UX spec draft (edge-case + traceability as internal validation) |
| 8 — Maintenance | `spec-updater` (skill) | Living-doc updates in Confluence |

Gate-4 approval records which directions carry forward (`gates.phase_4.carried_forward[]`); that list
drives both Phase 5 (flows per direction) and Phase 6 (one prototype per direction). Deciding it
deliberately at Gate 4 controls downstream build cost.

### Atomic skills (composed by the agents)

`problem-sharpener`, `assumption-extractor`, `interview-synthesizer`, `standards-mapper`,
`competitive-analyzer`, `prd-generator`, `threat-modeler`, `solution-scorer`,
`design-system-conflict-checker`, `flow-generator`, `flow-auditor`, `feedback-synthesizer`,
`prototype-scaffolder`, `component-composer`, `state-matrix-builder`, `option-builder`,
`option-presenter`, `section-writer`, `edge-case-hunter`, `traceability-checker`, `ux-copy-reviewer`,
`spec-updater`, `clarification-protocol`, `artifact-frontmatter`, `dedup`, `html-spec-renderer`,
`defense-ux-context` (this skill).

### Templates

- `${CLAUDE_PLUGIN_ROOT}/templates/ux-spec-template.md` — canonical spec template (a menu, not a checklist).
- `${CLAUDE_PLUGIN_ROOT}/templates/spec-state-object.json` — shared-memory schema across all phases.
- `${CLAUDE_PLUGIN_ROOT}/templates/gate-checklists.md` — gate validation criteria for all 7 phase gates.
- `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` — severity, glossing, and formatting conventions.
- `${CLAUDE_PLUGIN_ROOT}/templates/a11y-manual-checklist.md` — manual accessibility pass.

### Tool integrations

| Tool | Access | Behavior |
|---|---|---|
| **Confluence** | Read + Write (optional MCP) | Explicit confirmation required before any write; draft-only |
| **Jira** | Read + Write (optional MCP) | Link epics; create open questions as sub-tasks |
| **Web Search** | Read only | Compliance verification, competitive intel (research-agent only; verify via 2+ sources) |

The Phase 6 prototype sandbox is an **external prerequisite** (not bundled) — see the plugin README.
