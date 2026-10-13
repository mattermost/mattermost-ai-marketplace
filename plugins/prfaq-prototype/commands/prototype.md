---
description: Fast-path — turn a PRFAQ into shareable, multi-option interactive prototypes for faster alignment
argument-hint: "<PRFAQ file path, doc link (GitHub / Google Doc / Confluence / Mattermost thread / other), or title> [--persona-review=prfaq|prototype|both] [--persona-panel=domain|all|<slugs>] [--option-count=2|3] [--target=<key>]"
---

Resolve `$ARGUMENTS` to a source PRFAQ with the `prfaq-source-resolver` skill (Step 0 below). The input
can be a workspace file, a title under `PRFAQs/`, or a link to the doc wherever it lives — GitHub, Google
Docs, Confluence, a Mattermost thread, or any other doc. Only the exact link or file the user gave is
pulled; nothing is searched for. If nothing resolves, **ask the user for the PRFAQ**. (Stage 1 always needs
a real source — a bare `prototype-runs/<slug>` is not a valid input.)

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

## Step 0 — Pre-flight (run by you, the top-level assistant)

Both steps can prompt the user, and both need this session's connectors and shell, so run them here — not
inside the Stage-1/Stage-2 subagents.

1. **Resolve the source** — invoke the `prfaq-source-resolver` skill with `$ARGUMENTS`. It classifies the
   input (local file / GitHub / Google Doc / Confluence / Mattermost thread / other service / web / title),
   finds a connected tool that can read it, and — if none can — asks the user to connect one, export the
   doc, or paste it. It saves a markdown copy with provenance under `PRFAQs/` (reusing an earlier copy of
   the same link when unchanged) and returns `prfaq_path`, `source_kind` (`prfaq` | `discussion`), and any
   `context_paths`.
2. **Make sure the playground exists** — invoke the `playground-bootstrap` skill with the resolved target
   profile. If the playground is missing and the profile has a `repo_url`, it asks the user before cloning
   it (plus any `companion_repos`) into the workspace and installing dependencies. If it exists, it checks
   the git remote is the expected sandbox repo.

## Preconditions

- A source PRFAQ resolved to a markdown file inside the workspace (Step 0.1).
- **Input path containment (security):** canonicalize the resolved `prfaq_path` (and every
  `context_paths` entry); require it to stay inside the project workspace (prefer the `PRFAQs/` root) and
  reject absolute paths or `..` traversal that escapes the workspace — before Stage 1 parses it.
- The resolved target playground exists at its `workspace_relative_root` and is the expected repo
  (Step 0.2). If it's still missing (no `repo_url`, or the user declined the clone), abort and tell the
  user to clone/point at their playground (or copy the bundled config into the project and set the path).
- **Path containment (security):** canonicalize `workspace_relative_root` (and companion repo paths) and
  require them to stay **inside the project workspace** — a real sandbox playground, never a production
  repo. Reject `..` traversal or absolute paths that escape the workspace. Re-verify this containment
  immediately before Stage 2 scaffolds, composes, or runs `npm run build`, so a misconfigured or malicious
  value cannot redirect writes/builds into `mattermost` or anywhere outside the sandbox.

If preconditions fail, abort with the specific reason.

## Stage 1 — Analyst (analysis + human checkpoint)

Invoke the `prfaq-analyst` agent. Pass: the PRFAQ path, `source_kind`, any `context_paths`, the slug, the
active target profile, and any run flags. It parses the PRFAQ (T3-aware), maps scenes + option axes + assumptions, writes the brief, and
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
- **Never write to `internal-product-knowledge`, Confluence, Google Docs, Mattermost, or any other source
  system** from this pipeline — it emits no knowledge-repo artifacts (by design). Reading the exact doc the
  user linked, and saving a local copy under `PRFAQs/`, is allowed; posting, commenting, editing, or
  sharing is not.
- **Never pull a doc the user didn't point at.** No searching for PRFAQs; links found inside a fetched
  doc or thread are only followed after the user says yes.
- **Never clone, install, or modify a playground without the user's yes** (Step 0.2), and never pull,
  reset, or clean an existing one.
- **Never ask for tokens, passwords, or cookies** to reach a source — prompt the user to connect the
  connector instead.
- **Don't build into a production `mattermost` repo by default** — the sandbox playground is the build
  target. A production repo is used only when the project profile names it as `repo_url` and the user has
  said yes to the prompt on that run (Step 0.2).
- **Never overwrite an existing prototype** without confirmation — offer reuse/extend or a new slug.
- **No customer names** in any artifact (the parser scrubs; verify).

## Report

1. Prototype route (e.g. `/prototypes/<slug>`) and the local run command (`cd <root> && npm run dev`).
2. Options built (with the recommended one marked) and the scenes/states each covers.
3. Build status (pass/fail).
4. Path to the option comparison (`prototype-runs/<slug>/04-option-comparison.md`).
5. Flagged items: `[AI DRAFT — COPY]` strings and any `[VERIFY WITH PM]` / `COMPONENT_GAP`.
6. Offered next steps: narrow to one option → walkthrough; run persona review; deploy to Vercel (on request).
