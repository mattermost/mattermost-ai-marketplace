# FY26 Persona Catalog — UX Spec Pipeline

**Single source of truth** for the persona critics used by the optional persona review.

## Canonical layout

| What | Location | Notes |
|------|----------|-------|
| **Profile (canonical)** | `Personas/<Display Name>/<Display Name>.md` | Rich role-play brief — only copy per persona |
| **Claude Code agent** | `agents/persona-critic.md` (this plugin) | Generic loader; pass persona slug + artifact |

Do **not** create duplicate profiles under kebab-case paths. Agent slugs (`jake-reynolds`) are stable IDs; display-name folders hold the content.

## Persona types (deck taxonomy)

| Type | Goal |
|------|------|
| Operational Champion | Solve operational pains; drive mission outcomes |
| Economic Buyer | Strategic outcomes; minimize risk; justify investment |
| System Admin | Reliable, scaled, secure deployment |
| Risk Assessor | Legal, security, regulatory compliance |
| End User | Daily collaboration under operational stress |
| System Integrator / Extension Developer | Automate workflows; build integrations |

## Persona index — MissionOps

| Slug | Display name | Type | Profile path |
|------|--------------|------|--------------|
| `jake-reynolds` | Lt. Col. Jake Reynolds | Operational Champion | `Personas/Lt. Col. Jake Reynolds/Lt. Col. Jake Reynolds.md` |
| `regina-hayes` | Mrs. Regina Hayes | Economic Buyer | `Personas/Mrs. Regina Hayes/Mrs. Regina Hayes.md` |
| `chris-lawson` | Chris Lawson | System Admin | `Personas/Chris Lawson/Chris Lawson.md` |
| `sam-mitchell` | Sam Mitchell | Risk Assessor | `Personas/Sam Mitchell/Sam Mitchell.md` |
| `jake-carter` | Staff Sgt Jake Carter | End User | `Personas/Staff Sgt Jake Carter/Staff Sgt Jake Carter.md` |
| `paul-johnson` | Paul Johnson | System Integrator | `Personas/Paul Johnson/Paul Johnson.md` |

## Persona index — Cyber Defense

| Slug | Display name | Type | Profile path |
|------|--------------|------|--------------|
| `james-calderon` | James Calderon | Operational Champion | `Personas/James Calderon/James Calderon.md` |
| `brian-taylor` | Brian Taylor | Economic Buyer | `Personas/Brian Taylor/Brian Taylor.md` |
| `morgan-reese` | Morgan Reese | Risk Assessor | `Personas/Morgan Reese/Morgan Reese.md` |
| `sophia-martins` | Sophia Martins | End User | `Personas/Sophia Martins/Sophia Martins.md` |
| `ryan-holt` | Ryan Holt | Extension Developer | `Personas/Ryan Holt/Ryan Holt.md` |
| `jason-whitaker` | Jason Whitaker | System Admin | `Personas/Jason Whitaker/Jason Whitaker.md` |

## Persona index — DevSecOps

| Slug | Display name | Type | Profile path |
|------|--------------|------|--------------|
| `jordan-blake` | Jordan Blake | Operational Champion | `Personas/Jordan Blake/Jordan Blake.md` |
| `linda-harris` | Linda Harris | Economic Buyer | `Personas/Linda Harris/Linda Harris.md` |
| `alex-johnson` | Alex Johnson | System Admin | `Personas/Alex Johnson/Alex Johnson.md` |
| `victoria-clarke` | Victoria Clarke | Risk Assessor | `Personas/Victoria Clarke/Victoria Clarke.md` |
| `emily-warren` | Emily Warren | End User | `Personas/Emily Warren/Emily Warren.md` |
| `jacob-lee` | Jacob Lee | Extension Developer | `Personas/Jacob Lee/Jacob Lee.md` |

## Default panels (per persona-review run)

| Domain | Panel slugs |
|--------|-------------|
| **missionops** (IL4+ default) | `jake-reynolds`, `sam-mitchell`, `chris-lawson`, `jake-carter` (+ `regina-hayes` Phase 4+; + `paul-johnson` if integrations) |
| **cyber-defense** | `james-calderon`, `brian-taylor`, `morgan-reese`, `sophia-martins`, `ryan-holt` (+ `jason-whitaker` for deploy/SOC) |
| **devsecops** | `jordan-blake`, `alex-johnson`, `victoria-clarke`, `emily-warren`, `jacob-lee` (+ `linda-harris` Phase 4+) |

Pass `--persona-panel=domain` to use the feature's domain panel (IL4+ default: MissionOps), or
`--persona-panel=all` / `--persona-panel=<slugs>`.

## Invocation

Run via the plugin: `/prfaq-prototype:prototype <PRFAQ> --persona-review=prfaq|prototype|both`
(`--persona-panel=domain|all|<slugs>`) — the plugin flow runs the panel and synthesizes a prioritized
digest (via `feedback-synthesizer`) into `prototype-runs/<slug>/persona-reviews/`. Or invoke the
**read-only** `persona-critic` agent directly with a persona slug + an artifact path — it returns a single
in-character critique and does not write any files.

Persona review is OPTIONAL; if run, aim for zero unresolved P1 findings.
