---
description: Fast-path — turn a PRFAQ into shareable, multi-option interactive prototypes for faster alignment
argument-hint: "<PRFAQ file path or run slug> [--persona-review=prfaq|prototype|both] [--persona-panel=domain|all|<slugs>] [--option-count=2|3] [--target=<key>]"
---

Resolve `$ARGUMENTS` to a source PRFAQ: an exact path under `PRFAQs/`, then a fuzzy title match, then an
existing run slug under `prototype-runs/`. If nothing resolves, **ask the user for the PRFAQ** — do not go
hunting Confluence/Jira/web for it.

This is the standalone `/prfaq-prototype:prototype` fast-path pipeline (installed as a Claude plugin). It
is **decoupled from any spec-state / gate machinery**: no `spec-state.json`, no gates, no orchestrator
state machine. Working dir is `prototype-runs/<slug>/` in the consumer project. Two stages with a mandatory
human checkpoint between them.

## Config resolution (target playground)

Resolve the target profile in this order: (1) `prototype-targets.json` in the project root, (2)
`.claude/prototype-targets.json` in the project, (3) the bundled default
`${CLAUDE_PLUGIN_ROOT}/config/prototype-targets.json`. Use the `active_default` target unless
`--target=<key>` overrides it. To point at your own playground, copy the bundled config into your project
and edit `workspace_relative_root` — you never edit files inside the installed plugin.

## Preconditions

- The source PRFAQ markdown exists (or the user provides it).
- **Input path containment (security):** canonicalize the resolved `prfaq_path`; require it to stay inside
  the project workspace (prefer the `PRFAQs/` root) and reject absolute paths or `..` traversal that
  escapes the workspace — before Stage 1 parses it.
- The resolved target playground exists at its `workspace_relative_root`. If missing, abort and tell the
  user to clone/point at their playground (or copy the bundled config into the project and set the path).
- **Path containment (security):** canonicalize `workspace_relative_root` and require it to stay **inside
  the project workspace** — a real sandbox playground, never a production repo. Reject `..` traversal or
  absolute paths that escape the workspace. Re-verify this containment immediately before Stage 2 scaffolds,
  composes, or runs `npm run build`, so a misconfigured or malicious value cannot redirect writes/builds
  into `mattermost` or anywhere outside the sandbox.

If preconditions fail, abort with the specific reason.

## Stage 1 — Analyst (analysis + human checkpoint)

Invoke the `prfaq-analyst` agent. Pass: the PRFAQ path, the slug, the active target profile, and any run
flags. It parses the PRFAQ (T3-aware), maps scenes + option axes + assumptions, writes the brief, and
returns a clarification round.

**Surface the clarification round INTERACTIVELY and PAUSE.** Per the analyst's SURFACING RULES and project
guidance: present questions as discrete, selectable choices (≤4 per interactive round, run a second short
round if needed) — never a wall of markdown with a `1: B, 2: A` reply line. Use **plain language**, and
make every question and option **self-contained** (restate what each screen/direction means in plain words
— never a bare `S1`/`AX2` code the user would have to look up). Do not proceed to Stage 2 until the user
answers. Record answers in `prototype-runs/<slug>/03-clarifications.md`.

## Stage 2 — Builder (build + validate)

After the checkpoint, invoke the `prototype-builder` agent with the brief, scene plan, clarifications, and
target profile. It reuse-checks, scaffolds, composes from the real component library, generates the
approved states, runs `npm run build` until clean, and writes the option comparison.

The builder will:
- Build ONE prototype slug with the chosen options as switchable scene-sets (option toggle + `SceneSwitcher`),
  per the target profile's `multi_option_convention` — not a hardcoded structure.
- **Mount each scene on the real app surface**: reuse an existing prototype's shell or the target's layout
  components (channel view, System Console, DM composer) rather than hand-rolling a frame. If a needed
  surface has no base layout in the playground, the analyst offers (non-blocking) to let you drop a
  screenshot in `prototype-runs/<slug>/reference/` to build on top of; if you don't, it builds freeform and
  flags `[FREEFORM — NO BASE LAYOUT]`. It never blocks waiting for a screenshot.
- Compose only from the runtime-enumerated component library; flag `COMPONENT_GAP`s, never phantom-import.
- Label every authored UI string `[AI DRAFT — COPY]` (the PRFAQ rarely supplies copy) and surface it.
- Keep the product frame clean — no reviewer aids/annotations rendered into the UI.

## Optional stages (offered, never automatic)

- **Persona review** (`--persona-review=prfaq|prototype|both`): run the `persona-critic` panel (default:
  MissionOps domain panel; `--persona-panel=all` for all 18, or a custom slug list) and synthesize a
  prioritized digest into `prototype-runs/<slug>/persona-reviews/`. On the PRFAQ it runs at the Stage-1
  checkpoint; on the prototype it runs post-build.
- **Walkthrough**: NOT built by default. Suggest it only once the options are narrowed to a single chosen
  direction, or if the user asks. It is a standalone HTML tour that iframes the live scenes with a
  narrative rail outside the product frame.

## Hard stops — never bypass

- **Never self-resolve the Stage-1 clarification round.** Surface-and-pause is mandatory; only the user
  resolves Recommended options (per-question or `accept recommendations`).
- **Never deploy to Vercel without explicit user confirmation** — deploying is an external publish. Local
  `npm run dev` is the default. State exactly what will be deployed and where, and wait for a clear yes.
- **Never write to `internal-product-knowledge` or Confluence** from this pipeline — it emits no
  knowledge-repo artifacts (by design).
- **Never build into the production `mattermost` repo** — the sandbox target is the only build surface.
- **Never overwrite an existing prototype** without confirmation — offer reuse/extend or a new slug.
- **No customer names** in any artifact (the parser scrubs; verify).

## Report

1. Prototype route (e.g. `/prototypes/<slug>`) and the local run command (`cd <root> && npm run dev`).
2. Options built (with the recommended one marked) and the scenes/states each covers.
3. Build status (pass/fail).
4. Path to the option comparison (`prototype-runs/<slug>/04-option-comparison.md`).
5. Flagged items: `[AI DRAFT — COPY]` strings and any `[VERIFY WITH PM]` / `COMPONENT_GAP`.
6. Offered next steps: narrow to one option → walkthrough; run persona review; deploy to Vercel (on request).
