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

- A local **prototype playground** (a React/Vite sandbox with a Compass-style component library). The
  bundled default profile targets `proto-playground` (`@mattermost/compass-ui`, `src/pages/prototypes/<slug>/`,
  `SceneSwitcher` scene API). See **Configure your playground** below.
- Node + npm to build/preview the playground.

## Install

```bash
/plugin marketplace add mattermost/mattermost-ai-marketplace
/plugin install prfaq-prototype@mattermost-ai-marketplace
```

## Use

```
/prfaq-prototype:prototype <path to a PRFAQ .md>
```

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
- **Skills:** `prfaq-parser`, `scene-mapper`, `sandbox-scaffolder`, `sandbox-composer`, plus the bundled
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
  into a production repo.

## Personas

The bundled `personas/` catalog is a set of **fictional** FY26 personas (no real customers or
individuals) used for the optional in-character persona review. To use your own instead, drop a
`personas/persona-catalog.md` in your project — the persona review prefers a project catalog and skips
cleanly if none exists.
