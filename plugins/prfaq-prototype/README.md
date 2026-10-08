# PRFAQ → Prototype (Claude plugin)

Turn a **PRFAQ** into **shareable, multi-option interactive prototypes** so teams align on pixels instead
of prose. A standalone fast-path — decoupled from any spec/gate machinery — that runs in three moves:

1. **Parse** the PRFAQ (any format; T3-aware) into a structured brief: surfaces, actors, states, rules,
   verbatim copy, a ranked scene inventory, real option-divergence axes, and an assumptions ledger.
   Customer names are scrubbed; in-document contradictions are surfaced, never silently resolved.
2. **Align** — one interactive, plain-language clarification round (surface-and-pause) where the human sets
   scope, the design directions, and personas. Nothing is built until you answer.
3. **Build** 2–3 genuinely distinct design options into your sandbox playground — composed from the app's
   **real component library** and mounted on the app's **real base layouts** (channel view, System Console,
   DM composer), validated with a clean build, plus an option comparison.

## Prerequisites

- **Node + npm** (the default playground pins its version in `.nvmrc`) and **git** with access to GitHub.
- A **prototype playground** inside your project. You don't need to set one up first: if it's missing, the
  command offers to clone [`mattermost-proto-playground`](https://github.com/mattermost/mattermost-proto-playground)
  into `prototype-playground/proto-playground` — plus [`compass-design`](https://github.com/mattermost/compass-design)
  next to it, which the playground needs — and run `npm install`. It asks before cloning. See **Configure
  your playground** below to use your own.
- To pull a PRFAQ from a link, the matching **connector** in your Claude session (GitHub, Google Drive,
  Confluence/Atlassian, Mattermost, …). If one isn't connected, the command tells you and offers to wait
  while you connect it, or to take an exported file or pasted text instead.

## Install

```bash
/plugin marketplace add mattermost/mattermost-ai-marketplace
/plugin install prfaq-prototype@mattermost-ai-marketplace
```

## Use

```
/prfaq-prototype:prototype <PRFAQ: file path, doc link, or title>
```

The PRFAQ can come from anywhere you can link to:

| You pass | What happens |
|---|---|
| A file in the project (`.md`, `.docx`, `.pdf`, …) | Used as is (non-markdown is converted to a copy under `PRFAQs/`). |
| A GitHub, Google Doc, or Confluence link | Pulled read-only through the matching connector and saved to `PRFAQs/<title>.md`. |
| A Mattermost thread permalink | The whole thread is pulled as context. If it links to the actual PRFAQ, you're asked whether to pull that too. |
| Any other doc link | Pulled through a matching connector, or fetched if it's public. |
| A title | Matched against files already in `PRFAQs/`. |

Only the exact link you pass is pulled — the plugin never searches for a PRFAQ, and never writes back to
the source. Each saved copy records where it came from on its first line, so a re-run reuses it instead of
re-fetching (and offers a refresh if the source changed).

Optional flags: `--option-count=2|3`, `--target=<profile key>`,
`--persona-review=prfaq|prototype|both`, `--persona-panel=domain|all|<slugs>`.

The command runs Stage 1 (analyst → interactive clarification round → **pause**), then Stage 2 (builder),
and reports the prototype route + local run command + flagged items.

## Configure your playground (swappable target)

The build target is defined in a **target profile**, resolved in this order:

1. `prototype-targets.json` in your project root
2. `.claude/prototype-targets.json` in your project
3. the **bundled default** at `config/prototype-targets.json` (inside the plugin)

To point at your own playground **without editing the installed plugin**, copy the bundled
`config/prototype-targets.json` into your project and edit `workspace_relative_root` (and, if different,
the folder/manifest/scene-API fields). Add a newer playground later by adding a profile entry and flipping
`active_default` — no agent or skill changes needed.

## What's bundled (self-contained)

- **Command:** `commands/prototype.md` → `/prfaq-prototype:prototype`
- **Agents:** `prfaq-analyst` (parse + align), `prototype-builder` (scaffold + compose + validate),
  `persona-critic` (in-character review)
- **Skills:** `prfaq-source-resolver` and `playground-bootstrap` (pre-flight), `prfaq-parser`,
  `scene-mapper`, `sandbox-scaffolder`, `sandbox-composer`, plus the bundled
  essentials `clarification-protocol`, `artifact-frontmatter`, `walkthrough-builder`, `feedback-synthesizer`
- **Config:** `config/prototype-targets.json` (bundled default target profile)
- **Personas:** `personas/` (FY26 persona catalog + profiles) for the optional persona review

State generation and the option-comparison matrix are done inline by the builder — this plugin does not
depend on external `state-matrix-builder` / `option-presenter` / `dedup` skills.

## Guardrails (built in)

- Surface-and-pause clarifications — never self-resolved.
- Mount on real app layouts; ask for a screenshot when none exists; freeform only as a flagged,
  non-blocking fallback.
- No customer names in any artifact; authored UI copy labeled `[AI DRAFT — COPY]`.
- Clean product frame (no reviewer annotations in the UI).
- Walkthrough only after narrowing to one direction; Vercel deploy only on explicit request; never builds
  into a production repo (an existing playground's git remote is checked before building).
- Sources are read-only and pulled only from the link you give; no tokens or passwords are ever requested.
- Clones and installs only after you say yes; never pulls, resets, or cleans an existing playground.

## Personas

The bundled `personas/` catalog is a set of **fictional** FY26 personas (no real customers or
individuals) used for the optional in-character persona review. To use your own instead, drop a
`personas/persona-catalog.md` in your project — the persona review prefers a project catalog and skips
cleanly if none exists.
