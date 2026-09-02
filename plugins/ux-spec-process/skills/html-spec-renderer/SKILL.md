---
name: HTML Spec Renderer
description: Generates self-contained, IL-honest HTML artifacts that are the PRIMARY shareable deliverable for pre-spec work (Phases 1–6). Codifies the "unreasonable effectiveness of HTML" aesthetic — ivory/clay/serif editorial language — and provides per-phase pattern selection rules. Produces the master spec.html (living surface) and per-phase artifacts (Phase 4 option comparison, Phase 5 interactive flowchart, VERIFY tracker, traceability heatmap) using verified design tokens, 16+ modules, and reference implementations. Air-gap safe (no CDN), WCAG 2.1 AA, degrades without JS.
version: 2.1.0
author: Mattermost Design Team
tags: [ux-spec, html-rendering, living-surface, defense, il5, pre-spec-deliverable]
---

# HTML Spec Renderer

## What this surface is (BLUF)

The HTML living surface is the **primary, shareable, presentation-grade deliverable for all pre-spec work — Phases 1–6.** When a designer needs to show discovery, research, a PRD, ideation options, or flows to a teammate or to leadership, **the HTML is what they share** — not the raw markdown, not a Confluence page.

- **Markdown remains canonical content.** Every fact lives in the spec folder's `*.md` artifacts and `spec-state.json`. The HTML is *generated from* that markdown — it is the presentation surface, never an independent source of truth.
- **Confluence is reserved for end-state specs and final proposals (Phase 7/8) only.** Pre-spec artifacts never go to Confluence. The HTML living surface fills that gap for Phases 1–6.
- **It must be IL-honest.** This surface is shown to a defense audience. It works air-gapped (no CDN, no fetch), passes WCAG 2.1 AA, and stays usable with JavaScript disabled. These are hard requirements, not nice-to-haves — see **IL-Honest Hard Requirements** below. A surface that fails any of them is disqualified for this audience and must not be presented.

Patterns are adapted from the [html-effectiveness gallery](../../html-effectiveness-main/) (Anthropic's "unreasonable effectiveness of HTML" examples) with consistent design tokens.

## When to Use

- **As the default deliverable surface for every pre-spec phase (1–6).** Whenever a Phase 1–6 artifact is produced or updated, regenerate the relevant HTML — it is the thing the designer hands to a teammate or to leadership.
- After any phase produces a new gate artifact, regenerate the relevant per-phase HTML
- After any phase, regenerate the master `spec.html` to surface new content
- As the **review surface** for gate sign-offs — reviewers open the HTML, not the markdown
- Before publishing to Confluence (Phase 7) — the HTML is a sanity check on the spec's readability
- For SCIF / classified review — the print mode flattens to a clean PDF-ready document; the air-gap and JS-off guarantees mean it survives a disconnected, locked-down workstation

## When NOT to Use

- For markdown editing — markdown remains canonical; edit there, then regenerate the HTML
- For Phase 7/8 publication — **end-state specs and final proposals go to Confluence** (per the Output Rules in CLAUDE.md), not the HTML living surface. The HTML is the pre-spec (Phases 1–6) surface; Confluence is the post-spec (Phase 7/8) surface.
- For dynamic/server-side rendering — HTML is intentionally static, single file
- For interactive prototypes — those live in proto-playground, not the spec surface
- For data the agent does not own — never hallucinate FRs, threat counts, or coverage status

---

## Pattern Selection per Phase

| Phase | Primary pattern | Source file (reference) | Output file |
|---|---|---|---|
| **Phase 1 — Discovery** | Section-anchored phase block inside `spec.html` | 11-status-report.html, 16-implementation-plan.html | Merged into `spec.html` |
| **Phase 2 — Research** | Section-anchored phase block; standards table | 14-research-feature-explainer.html, 11-status-report.html | Merged into `spec.html` |
| **Phase 3 — PRD** | Section-anchored phase block + threat heatmap module + requirement list | 16-implementation-plan.html (risks), 12-incident-report.html (impact table) | Merged into `spec.html` |
| **Phase 4 — Ideation** | **Side-by-side option comparison** with scored evaluation matrix + tradeoff table + chips + recommendation panel | **01-exploration-code-approaches.html** | Per-phase `options.html` + summary block in `spec.html` |
| **Phase 5 — Flows** | **Interactive SVG flowchart** with clickable nodes + side panel + coverage strip | **13-flowchart-diagram.html** | Per-phase `flow-diagram.html` per major flow + summary in `spec.html` |
| **Phase 6 — Prototype** | Iframe embed of playground + state-matrix grid + visual comparison cards | 06-component-variants.html, 02-exploration-visual-designs.html | Per-phase `prototype-tour.html` + summary in `spec.html` |
| **Phase 7 — UX Spec** | Complete living surface (master `spec.html`) | 17-pr-writeup.html (file-tour), 16-implementation-plan.html (milestones) | `spec.html` (the living surface) |
| **Cross-phase: VERIFY tracker** | **4-column kanban with drag/drop + markdown export** | **18-editor-triage-board.html** | `specs/{feature-id}/verify-board.html` (per-spec; see Module 16) |
| **Cross-phase: Traceability** | Interactive coverage grid with side panel | (custom; based on 13/15 interaction patterns) | `traceability-heatmap.html` (per-spec) |
| **Cross-phase: PR review** | Annotated diff + file-by-file tour + focus items + test plan + rollout | **03-code-review-pr.html, 17-pr-writeup.html** | `pr-review-<n>.html` (per-PR, lives at ux-pr-reviewer-agent output) |

---

## Operating Rules

The first five rules are the **IL-Honest Hard Requirements** — they are non-negotiable for a defense audience. Failing any one disqualifies the surface; do not present a render that violates them. They are restated with implementation detail in the dedicated section below.

1. **No external CDN — ever. Single file, self-contained.** No `<script src=>`, no `<link href=>` to a CDN, no `@import url(...)`, no `fetch`, no web fonts pulled over the network, no build step at view time. All CSS inline. All JS inline as progressive enhancement. The file must work when opened offline by double-click on a disconnected, air-gapped workstation. **Any diagram (e.g., Mermaid) is pre-rendered to inline SVG at build time via `mmdc` — never a runtime `cdn.jsdelivr` script.** (See IL-Honest Hard Requirements §4.)
2. **Light theme is the true default.** The page loads light with no JS and no stored preference. Reviewers in SCIF environments often print under harsh lighting; a dark default fails. Dark theme is opt-in via toggle only.
3. **Content survives JS-off.** Every collapsible uses native `<details>`/`<summary>` (open by default for completed-phase content so nothing is hidden behind a script). A `<noscript>` fallback block states that the page is fully readable without JavaScript and points to the canonical markdown. JS only *adds* active-state TOC, expand/collapse-all, on-click panel updates, and drag-drop — it never gates content.
4. **WCAG 2.1 AA.** Never encode meaning by color alone (1.4.1): every status/severity badge pairs **color + text** (and may add an icon), never color alone. Interactive elements (flowchart nodes, heatmap cells, kanban cards, toggles) carry meaningful `role`, `aria-label`/`aria-labelledby`, `tabindex`, and keyboard handlers. Contrast meets 4.5:1 for body text and 3:1 for large text and UI components, in both themes.
5. **Print mode mandatory.** `@media print` block flattens collapsibles, hides controls and TOC, inlines link URLs, switches dark surfaces to high-contrast white.
6. **No hallucinated content.** Every fact must trace back to an artifact, the state object, or the codebase. When in doubt, omit. **See Example-Data Guardrail below.**
7. **Self-resolving references.** Never render a bare internal code (`FR-10`, `EC-21`, `AC-2`) that forces the reader to look it up elsewhere. Each ID renders as a hover/expand revealing its full text inline (per `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §5). See **Self-Resolving References** below.
8. **Two-layer output.** The surface opens with a skim layer (masthead + BLUF + summary band + VERIFY rail) that a reader gets in under a minute; the deep body follows (per `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §6). Never make the reader parse the whole body to find the decision.
9. **Citation, not restatement.** Cross-phase references use the citation pattern (blockquote with clay left border), never paraphrase prior content. This pairs with the dedup pass in phase agents.

---

## 🛡 IL-Honest Hard Requirements

This surface is shown to a defense audience. These four requirements are the gaps that previously disqualified the surface for IL5 use (see `process-review/FINDINGS.md` pilot item 3). They are **hard pass/fail gates** on every render. The Agent Self-Check refuses to emit a render that violates any of them.

### 1. Light theme is the true default

- The page renders **light with zero JavaScript and zero stored preference.** Do not read `localStorage` or `prefers-color-scheme` to pick the *initial* theme; light is the literal default in `:root`. Dark is opt-in only, applied by adding `.dark-preview` to `<html>` via the toggle.
- Rationale: SCIF print-under-harsh-light, and a guarantee that the first paint a reviewer sees is the audited, high-contrast light surface.

### 2. Content survives JS-off (native `<details>` + `<noscript>`)

- **Every collapsible is a native `<details>`/`<summary>`** — no `<div>` + click-handler accordions. Completed-phase blocks carry the `open` attribute so all approved content is visible with JS disabled.
- **A `<noscript>` block is mandatory**, placed immediately after `<body>` opens, before the masthead:

  ```html
  <noscript>
    <div class="noscript-note" role="note">
      <strong>JavaScript is off — this is by design.</strong> Every section below is fully readable.
      Collapsibles are open; the table of contents and theme/print controls are the only things that need JS.
      Canonical source: the markdown in this spec's folder.
    </div>
  </noscript>
  ```

  Style `.noscript-note` with an oat background, slate text, clay left border — visible but not alarming.
- JS is **progressive enhancement only**: active-state TOC highlighting, expand/collapse-all, on-click side panels, drag-drop. If any of these is the *only* way to reach a piece of content, the render fails this requirement.

### 3. WCAG 2.1 AA — color + text, meaningful ARIA

- **Every status/severity badge pairs color + text** (P1/P2/P3, done/gap/deferred, v1.0/v2.0, covered/partial/missing). Color is never the sole carrier of meaning (WCAG 1.4.1). A prefix icon may be added but does not replace the text label.
- **Interactive elements carry meaningful ARIA and keyboard support:** flowchart nodes, heatmap cells, and kanban cards get `role="button"` (or appropriate role), `aria-label` describing the action/state, `tabindex="0"`, and `keydown` handlers for Enter/Space. The theme toggle uses `aria-pressed`. The TOC is a `<nav aria-label="...">`. Side panels that update on click use `aria-live="polite"`.
- **Contrast:** body text ≥ 4.5:1; large text and UI component boundaries ≥ 3:1 — verified in **both** light and dark variants.
- **Focus visible:** never remove focus outlines without a replacement; provide a visible `:focus-visible` style on every interactive element.

### 4. No external CDN — diagrams pre-rendered to inline SVG (HARD RULE)

- **No runtime network dependency of any kind.** Forbidden in the emitted file: `<script src=>`, `<link rel="stylesheet" href=>` to a CDN, `@import url(...)`, `fetch(`, `XMLHttpRequest`, web fonts loaded over the network, and any `cdn.jsdelivr` / `unpkg` / `cdnjs` reference. Fonts use the system stacks already declared in the tokens.
- **Mermaid (and any other diagram) is pre-rendered to inline `<svg>` at build time using `mmdc` (Mermaid CLI).** The shipped HTML contains the resulting `<svg>` markup inline. **A runtime `<script src="https://cdn.jsdelivr.net/npm/mermaid...">` is forbidden and is an automatic render failure** — it is the exact IL5/air-gap disqualifier called out in `process-review/FINDINGS.md`.

  Build step (offline, at generation time, not at view time):

  ```bash
  # input.mmd → inline SVG embedded directly in the HTML body
  mmdc -i flow.mmd -o flow.svg
  # then inline the <svg>…</svg> contents into the HTML (no <img>, no external ref)
  ```

  Prefer inlined `<svg>` over `<img src="flow.svg">` so the diagram is truly single-file and styleable by the token CSS.
- The Agent Self-Check greps the emitted file for these forbidden tokens and **fails the render** if any are present.

---

---

## Self-Resolving References

Per `${CLAUDE_PLUGIN_ROOT}/templates/conventions.md` §5, a reader skimming one section must never have to scroll to a glossary or open another file to understand a cited ID. In the HTML surface, **every internal code (`FR-N`, `EC-N`, threat IDs, control IDs like `AC-2`) renders as a hover/expand that reveals its full text inline.** The markdown still carries the inline gloss so it reads correctly without the HTML.

Use a self-contained pattern that works **without JS** (native title/hover and a `<details>` fallback) and is enhanced **with JS** (click-to-pin tooltip):

```html
<!-- Inline, JS-free: native tooltip + visible gloss on focus/hover via CSS -->
<span class="ref" tabindex="0" role="note"
      aria-label="FR-10: admins bulk-assign attributes by policy">
  FR-10
  <span class="ref-pop">admins bulk-assign attributes by policy</span>
</span>
```

```css
.ref { border-bottom: 1.5px dotted var(--clay-d); cursor: help; position: relative; }
.ref-pop {
  position: absolute; left: 0; top: 1.5em; z-index: 5;
  background: var(--paper); border: var(--border); border-radius: var(--radius-row);
  padding: 6px 10px; min-width: 220px; font: 13px/1.45 var(--sans); color: var(--slate);
  box-shadow: 0 6px 24px rgba(20,20,19,.12);
  opacity: 0; visibility: hidden; transition: opacity .12s;
}
.ref:hover .ref-pop, .ref:focus .ref-pop, .ref:focus-within .ref-pop { opacity: 1; visibility: visible; }
@media print { .ref-pop { position: static; opacity: 1; visibility: visible; display: inline; box-shadow: none; border: none; } }
```

Rules:
- The full gloss text is **in the DOM** (inside `.ref-pop` and the `aria-label`), so it is reachable by keyboard, screen reader, and print — not injected by JS.
- IDs are **stable across phases** (assigned once in the PRD, reused downstream), so a citation always resolves to one definition. Pull the gloss text from the manifest (`requirements[].name`, etc.), never hardcode it.
- In print mode the popover flattens to inline text so the PDF carries the full meaning.

---

## Design Tokens — the canonical palette

Always inline these tokens at the top of `<style>`. Source: the "unreasonable effectiveness of HTML" gallery, extended with a sky accent for v2.0 release markers and rust for P1 severity.

```css
:root {
  --ivory:   #FAF9F5;   /* page background */
  --paper:   #FFFFFF;   /* panel background */
  --slate:   #141413;   /* primary text */
  --clay:    #D97757;   /* primary accent — current, attention */
  --clay-d:  #B85C3E;   /* clay on light surfaces */
  --oat:     #E3DACC;   /* warm neutral, tier 2 panels */
  --olive:   #788C5D;   /* success, done, v1.0 */
  --rust:    #B04A3F;   /* P1, blocker, error */
  --sky:     #6A8CAF;   /* v2.0, secondary accent */
  --g100:    #F0EEE6;
  --g150:    #E8E5DB;
  --g300:    #D1CFC5;
  --g500:    #87867F;
  --g700:    #3D3D3A;

  --serif: ui-serif, Georgia, "Times New Roman", serif;
  --sans:  system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono:  ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;

  --radius-panel: 14px;
  --radius-row: 10px;
  --border: 1.5px solid var(--g300);
}

/* Optional dark variant — toggled via .dark-preview on <html>. Light default. */
html.dark-preview {
  --ivory: #161614; --paper: #1F1E1B; --slate: #F2F0E8;
  --clay: #E08766; --clay-d: #D97757; --oat: #3A332A; --olive: #92A66F;
  --rust: #D17169; --sky: #8AA8C7; --g100: #25241F; --g150: #2E2C26;
  --g300: #3D3B33; --g500: #908F83; --g700: #C5C3B8;
  --border: 1.5px solid #3D3B33;
}
```

**Color semantics:**
- `--clay` = current phase, attention, citation accent, primary action
- `--olive` = done, covered, P3, v1.0
- `--rust` = P1, gap, blocker, error
- `--oat` = warm tier-2 backgrounds, badges, content shelves
- `--sky` = v2.0 release tag, secondary surface accent

**Typography rules:**
- Serif for headlines (h1, h2, h3, panel titles, "human" content)
- Sans for body, descriptions, table cells
- Mono for IDs, file paths, technical labels, eyebrows, timestamps, badges
- H1: 32–44px serif, weight 500, letter-spacing -0.012em, max-width 22ch
- H2: 22–26px serif, weight 500
- H3: 17–19px serif, weight 500
- Body: 14–15.5px sans, line-height 1.55–1.65

---

## Module Library (16 modules)

### Master `spec.html` modules

#### 1. Masthead

```html
<header class="mast">
  <div class="eyebrow">Living Spec · Mattermost Defense &amp; National Security</div>
  <h1>{Spec title}</h1>
  <div class="pillbar">
    <span class="pill tier"><span class="k">Tier</span> {N} — Standard Spec</span>
    <span class="pill il"><span class="k">Mission tier</span> {IL4/5/6}</span>
    <span class="pill phase"><span class="k">Phase</span> {N} of 7 — {status}</span>
    <span class="pill draft">[AI DRAFT]</span>
  </div>
</header>
```

**Pill height contract:** all pills use `padding: 6px 14px; line-height: 16px; height: 28px;` to guarantee identical visual height. Do NOT override `font-size` or `font-family` on individual variants — only color/background.

#### 2. BLUF — Dark TLDR panel

```html
<div class="bluf">
  <div class="label">BLUF · Bottom Line Up Front</div>
  <p>2–3 sentences. The problem, the scope, the constraints.</p>
  <p>Phased release detail with <code>v1.0</code> and <code>v2.0</code> code spans.</p>
  <div class="roles">
    <span class="role primary">primary: …</span>
    <span class="role">…</span>
  </div>
</div>
```

Slate background, ivory text. Oat label, oat-on-slate code, clay primary role. Max 2 paragraphs.

#### 3. Summary band — stat cards

```html
<div class="summary">
  <div class="stat warn">
    <div class="num olive">0</div>
    <div class="lbl">Open VERIFY items</div>
    <div class="delta">7 resolved {date}</div>
  </div>
</div>
```

Variants: `.stat.accent` (clay left border), `.stat.warn` (olive left border).

#### 4. VERIFY rail (in-spec compact view)

Empty state: olive background + ✓.
Non-empty: clay-bordered rows pinned to the top.

#### 5. Phase timeline — explicit dot-column

**Critical alignment rule:** use the explicit dot-column pattern from `16-implementation-plan.html`, NOT absolute positioning. The dot lives in its own grid column with a `flex: 1` line below it.

```html
<div class="timeline">
  <div class="tl-entry">
    <span class="tl-time">{date}</span>
    <div class="tl-dotcol"><span class="tl-dot done"></span><span class="tl-line"></span></div>
    <div class="tl-body">
      <div class="name">Phase {N} · {Name}</div>
      <div class="sub">{one-line phase summary}</div>
    </div>
    <span class="tl-status done">complete</span>
  </div>
</div>
```

CSS uses `grid-template-columns: 110px 28px minmax(0, 1fr) auto`. The dot-col is a flex column. The line is `flex: 1` and `min-height: 30px`. Last entry hides its line.

#### 6. Phase collapsible (file-tour pattern)

`<details>` element with g100 summary background, clay chevron rotating 90° on open. JS-free.

#### 7. Citation block (dedup pass output)

```html
<div class="cite">
  <span class="src">Problem framing →</span>
  see <a href="#p1">Phase 1 § BLUF</a> · <em>not restated here</em>
</div>
```

Clay 3px left border. Ivory background.

#### 8. Decisions table

Hover-row in ivory. Badge variants: `flipped` (clay ↺), `expanded` (sky +), `resolved` (olive ✓), `deferred` (gray →). Always pair color with prefix icon.

#### 9. Role-impact cards (auto-flow grid)

`.role-card.primary` has a clay left border.

#### 10. Requirement list (file-tour-style nested collapsibles)

Each FR is a `<details class="req">` with `<summary>` showing id + name + release tag (v1 olive, v2 sky). Acceptance criteria render inside.

#### 11. Threat heatmap (bar-row chart)

Bar width = **vector count × 22px** (consistent scale across rows so surface-to-surface comparison is honest). Legend explains P1/P2/P3 semantics.

#### 12. Pre-flight verdict

Olive border + ✓ icon for "ready"; clay for "needs revision"; rust for "blocked."

#### 13. Pending-phases block

Single section replacing per-phase stubs for not-yet-started phases. Two-column grid showing what each will render.

```html
<section id="pending">
  <div class="sec-head"><span class="ix">{N}</span><h2>Phases not yet started</h2></div>
  <div class="pending-block">
    <h3>What each will render when run</h3>
    <p style="font-size: 13.5px; color: var(--g500);">Each pending phase produces a gate artifact rendered into this same living surface.</p>
    <div class="pre-list">
      <div class="pre-item">
        <div class="num">P4 — Ideation</div>
        <div class="what">Solution directions</div>
        <div class="modules">Side-by-side option cards · 8-dimension evaluation matrix · top 3 risks · BLUF recommendation</div>
      </div>
      <!-- repeat for each pending phase, sourced from per-phase module list -->
    </div>
  </div>
</section>
```

CSS: `.pre-list { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }` collapsed to single column on mobile. Each `.pre-item` has a 2px gray-300 left border, `.num` in clay mono, `.what` in serif slate, `.modules` in g500 12px sans.

---

### Per-phase pattern modules

#### 14. Phase 4 Ideation — option comparison (pattern from `01-exploration-code-approaches.html`)

**File:** `phase-4-ideation/options.html`
**Reference:** `process-improvements-pilot/phase-4-ideation/options.html`

Structure:
- Masthead + meta pillbar + lead paragraph
- 3-column grid of `<article class="approach">` cards
- Each approach card: numbered header + tagline + score panel (8 dimensions × 5-cell bars) + tradeoff table (Pro/Con) + chip footer
- One card is `.recommended` (clay border + "✓ Recommended" tag at top-left)
- Recommendation panel (clay left-border, serif h2, paragraph rationale)
- Top 3 risks grid (cards with severity pill)

**Score panel uses 5-cell discrete bars** (not slider/percentage) — readable at a glance, prints cleanly.

#### 15. Phase 5 Flows — interactive flowchart (pattern from `13-flowchart-diagram.html`)

**File:** `phase-5-flow/flow-diagram.html`
**Reference:** `process-improvements-pilot/phase-5-flow/flow-diagram.html`

Structure:
- Masthead + lead
- 2-column layout: SVG flowchart left (max-width 720px), sticky side panel right (320px)
- SVG nodes are clickable + keyboard-activatable; each populates the side panel with title/meta/body/fields
- Node variants: `.term` (terminal, oat rounded), `.gate` (diamond), `.ok` (olive tint), `.warn` (clay tint), `.bad` (rust tint)
- Edge variants: solid gray (default), olive (yes/happy), dashed dark gray (no/failure)
- Legend below canvas
- Coverage strip showing FR coverage (✓/partial/missing chips)

**This replaces prose flow routing description.** A 2,000-word Phase 5 §3.2 becomes a single SVG + side panel.

**The flowchart is pre-rendered to inline `<svg>` — never a runtime Mermaid CDN script (HARD RULE, see §4).** The author writes the routing logic once as Mermaid source; the build step converts it to inline SVG at generation time. This is the only acceptable path for an IL5/air-gap artifact — the `cdn.jsdelivr` Mermaid loader used by the demo file `process-improvements-pilot/diagram-sample/flow-diagram.html` is a render failure here.

**Concrete build step (offline, at `spec render` time, not at view time):**

```bash
# 1. Author the routing logic as Mermaid source next to the flow:
#    specs/{feature-id}/phase-5-flow/{flow-name}.mmd
# 2. Pre-render to SVG with the Mermaid CLI (mmdc):
mmdc -i specs/{feature-id}/phase-5-flow/{flow-name}.mmd \
     -o specs/{feature-id}/phase-5-flow/{flow-name}.svg
# 3. Inline the <svg>…</svg> contents directly into flow-diagram.html
#    (paste the SVG markup into the body — no <img src>, no external ref).
# 4. The shipped HTML contains ONLY inline <svg>; grep it for `mermaid`,
#    `jsdelivr`, `<script src` → must be zero hits.
```

Two acceptable flowchart sources, both ending in inline SVG: (a) hand-authored SVG using the node/edge variant classes above (the `13-flowchart-diagram.html` pattern — gives the clickable-node + side-panel interaction); or (b) Mermaid source → `mmdc` → inlined SVG (best for dense branchy routing the agent generates as text). Either way the emitted file carries inline `<svg>` and nothing networked. If `mmdc` is unavailable in the environment, fall back to the hand-authored SVG pattern — **do not** ship a CDN Mermaid loader as a stopgap.

#### 17. TOC convention — sticky left rail with auto-open

Master `spec.html` has a sticky-left `nav.toc` with three groups: **On this page** / **Phases** / **Reference**.

Anchor convention:
- Section anchors use plain `<a href="#{id}">{label}</a>` — work without JS via native scroll behavior
- Phase anchors carry `data-anchor` attribute: `<a href="#p3" data-anchor>...</a>` — JS handler opens the `<details class="phase">` on click

Active-state highlighting (progressive enhancement only):
```js
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const link = document.querySelector(`nav.toc a[href="#${entry.target.id}"]`);
        if (link) {
          document.querySelectorAll('nav.toc a').forEach(a => a.classList.remove('active'));
          link.classList.add('active');
        }
      }
    });
  }, { rootMargin: '-30% 0px -60% 0px' });
  // Observe BOTH phase details AND standalone sections so every TOC link lights up
  document.querySelectorAll('details.phase[id], section[id]').forEach(el => observer.observe(el));
}

document.querySelectorAll('nav.toc a[data-anchor]').forEach(link => {
  link.addEventListener('click', () => {
    const id = link.getAttribute('href').slice(1);
    const target = document.getElementById(id);
    if (target && target.tagName === 'DETAILS') target.open = true;
  });
});
```

Without JS: TOC links still scroll to targets; `<details>` stays in its default state (closed unless `open` attribute is set in markup); no active highlighting. All baseline functionality preserved.

#### 16. VERIFY tracker — kanban board with comment-on-drop (pattern from `18-editor-triage-board.html`, extended)

**File:** `specs/{spec-id}/verify-board.html` — **per-spec, lives next to that spec's `spec.html`**
**Reference:** `process-improvements-pilot/verify-tracker/verify-board.html` (note: the pilot aggregates across 4 specs for pattern showcase; production is single-spec)
**Data source:** `specs/{spec-id}/spec-state.json::context.open_questions[]` for that spec only

**Per-spec model:**
- Each spec gets its own verify-board, scoped to its own VERIFY items
- The spec is fixed per-file; phase references inside the payload drop the spec prefix (just `P5`, not `DPC/P5`)
- Generated and re-generated by whichever phase agent adds/resolves/defers VERIFY items in that spec
- If a workspace-level cross-spec view is ever needed, build it as a separate aggregating artifact — don't conflate the two

Structure:
- 4 columns: `Verify with PM` (clay), `Verify with Eng` (sky), `Resolved` (olive), `Deferred` (gray)
- Cards: id + tag chip + phase chip + title + body + opener handle + history footer
- Tag-click filters board to one tag (clay/sky/rust/oat)
- Foot text per column states the column's rationale
- Cards are keyboard-focusable (Section 508)

**Comment-on-drop workflow (the load-bearing extension):**

1. User drags a card from one column to another
2. On drop, a modal opens asking for an optional comment
3. User saves the move (with or without comment); card moves to new column; history entry recorded
4. Card now displays a clay left border (`.has-pending`) until the move is exported and acknowledged
5. Modal can be dismissed via Cancel button, Esc key, or click-outside-modal

**Persistence:**
- Board state (tickets + pending moves + history) is **in-memory only by default** — a page refresh/reload
  clears it, and nothing is written to persistent browser storage (`localStorage`, `sessionStorage`, IndexedDB)
  for a later user of the same profile to recover through ordinary means. **This is not a secure-erasure or
  air-gap guarantee** — it does not protect against memory capture, crash dumps, browser extensions with
  page-content access, clipboard export, or session/tab restoration. Classified environments still need
  endpoint-level controls (disk encryption, extension allowlisting, crash-reporting policy, session-restore
  disabled) for those vectors; this default only removes the browser-storage recovery path.
- Users must export state explicitly via **Copy as markdown** or **Copy for agent** before closing/reloading
  the page.
- An **explicit opt-in** "Enable local persistence" toggle may store state in `localStorage` under key
  `verify-board.v1` **only when the reviewer confirms the environment is not classified/SCIF**. When enabled,
  "Reset" / "Clear local state" wipes it — but this is a convenience clear, not a secure-erasure guarantee, and
  the UI must label it as such. Persistence, when enabled, is per-browser, per-machine — not collaborative.

**Two export buttons:**
- **Copy as markdown** — human-readable GitHub-flavored markdown grouped by column. Includes last comment per card. For pasting into Slack, 1:1 docs, status updates.
- **Copy for agent ↗** — structured JSON payload (see schema below). For pasting back into a chat with the spec-orchestrator agent so it can update `spec-state.json` mechanically.

**Agent payload schema (per-spec):**

```jsonc
// Wrapped in ```verify-board-payload code fence when copied.
// spec_id is constant per file — the verify-board is per-spec.
{
  "schema": "verify-board-payload",
  "version": "v2",
  "spec_id": "hierarchical-attributes",      // ← top-level; the file's spec
  "generated_at": "2026-05-22T15:30:00Z",
  "pending_changes": [
    {
      "id": "V-001",
      "phase": "P5",                          // ← just the phase; spec is implicit
      "title": "Permission entry naming: 'Manage join requests for this channel'",
      "tag": "pm",                            // pm | eng | sec | design
      "from": "verify-pm",                    // column key
      "to": "resolved",                       // column key
      "comment": "Resolved 2026-05-22 — PM confirmed copy as 'Manage join requests'",
      "moved_at": "2026-05-22T14:55:00Z"
    }
  ],
  "current_state": {
    "verify-pm": ["V-002", "V-003"],
    "verify-eng": ["V-007"],
    "resolved": ["V-001", "V-101", "V-102"],
    "deferred": ["V-201", "V-202"]
  }
}
```

**Schema version bump v1 → v2:** v1 used `phase_ref: "<spec-id>/P<N>"` per item (workspace-aggregate model). v2 uses top-level `spec_id` + per-item `phase: "P<N>"` (per-spec model). Orchestrator parser should accept both during the transition; treat v1 as legacy.

**Pending-moves badge:**
- The toolbar shows `N pending moves · ready to copy for agent` whenever `pending_changes` is non-empty
- Clicking the badge triggers `Copy for agent ↗` directly
- Until the agent applies the changes, cards keep their `.has-pending` border so it's clear what's local-only vs. authoritative

#### 18. Traceability heatmap — coverage grid with side panel (custom; interaction pattern from 13/15)

**File:** `specs/{spec-id}/traceability-heatmap.html` — **standalone, per-spec, lives next to `spec.html`**
**Reference:** `process-improvements-pilot/traceability-sample/heatmap.html`
**Data source:** `spec-state.json::artifacts.traceability_matrix` (the block already exists in the schema — `content`, `total_requirements`, `covered`, `partial`, `gaps[]`, `scope_creep[]`, `coverage_percentage`, `version`). The per-cell grid is derived from the `traceability-checker` skill output (`traceability_matrix[]` rows: `requirement_id`, `requirement_text`, `coverage_status`, `notes`, `severity_if_gap`) crossed against the design surfaces/flows.

**What it answers at a glance:** "Which PRD requirements have design gaps, and which gaps are blockers vs. polish?" — at gate review, in seconds instead of manually tracing N requirements × M surfaces.

**Role in the system (NOT a gate-blocking appendix):** This is an **internal/review surface**, additive to — not a replacement for — the canonical markdown traceability output. Per `traceability-checker` and `spec-writer-agent`, traceability is INTERNAL validation folded into the spec or surfaced as open questions; it is never a mandatory published appendix and never gates a phase on its own. The markdown table (`07-spec-traceability.md`) is canonical and diff-/Confluence-safe; the heatmap is a *view* of that same data.

Structure (mirrors the reference):
- Masthead + eyebrow + lead (state the regeneration source: `state.artifacts.traceability_matrix`)
- Summary stat row: FRs fully covered (olive) · partially covered (clay) · with blocker gap (rust) — **color + text + count**, never color alone
- The grid: rows = requirements (FRs/NFRs), columns = design surfaces/flows; each cell carries a coverage status
- Side panel (sticky, `aria-live="polite"`): clicking any cell, row label, or column header populates it with the requirement text, surface, status, source citation, blocker status, and the phase that must close it
- Legend below the grid (one swatch + text label per status)
- "Open gaps" list below the grid, sorted by severity then phase impact, each row self-resolving (`FR-N (gloss)` + surface + note)

**Cell status mapping (IL-honest — color + text + symbol, never color alone):**

| `coverage_status` | Cell class | Color | In-cell text/symbol | Maps to |
|---|---|---|---|---|
| `COVERED` | `.cell.ok` | olive tint | `✓` | full coverage |
| `PARTIAL` | `.cell.partial` | clay tint | `~` + qualifier | P2/P3 partial |
| `GAP` | `.cell.gap` | rust tint | `✕` | P1/P2 gap (use `severity_if_gap`) |
| `DEFERRED` | `.cell.na` | gray | `→` | tracked, non-blocking |
| `OUT_OF_SCOPE` / no trace | `.cell.na` | gray | `·` | n/a |

Cell tint values (already in the reference): `ok rgba(120,140,93,0.18)`, `partial rgba(217,119,87,0.18)`, `gap rgba(176,74,63,0.18)`, `na var(--g100)`. Each cell shows its symbol so the meaning survives grayscale print and color-blind viewers (WCAG 1.4.1). Row-level rollup takes the **worst applicable status** across that requirement's cells.

**IL-honest requirements (same hard gates as every other surface):**
- Light default, `<noscript>` block present, `@media print` flattens the side panel inline and forces high-contrast
- Grid cells, row heads, and column heads are interactive: `role="button"`, `aria-label` describing the requirement × surface × status, `tabindex="0"`, Enter/Space `keydown` handlers, visible `:focus-visible`
- No CDN, no fetch, single self-contained file; all data inlined from the manifest
- Every `FR-N`/`NFR-N` renders self-resolving (full gloss inline + in `aria-label`), never a bare code

**Regeneration cadence:** regenerate whenever the matrix changes. Spec-writer-agent generates it in Phase 7 (it already runs `traceability-checker`); earlier phases may regenerate it to surface coverage drift as it appears rather than waiting for Phase 7. Link it from the `spec.html` § Spec / Traceability section.

---

## Reference Sections (always at the bottom of spec.html)

After all phase content:
- **Decisions log** — chronological audit-trail rows: `<date> · <phase·Q-id> · <one-line what changed>`
- **Compliance footprint** — grid of comp-cards, one per framework
- **Cross-spec coordination** — grid of x-cards, one per coordinating spec

### Footer

```html
<footer>
  <div><span class="k">Living spec</span> · generated {timestamp} from <code>spec-state.json</code> + per-phase artifacts</div>
  <div>regenerate with <code>spec render {feature-id}</code> · canonical source: markdown in spec folder</div>
</footer>
```

---

## TOC (left rail)

Sticky on left. Three groups: **On this page** / **Phases** / **Reference**. Active state via IntersectionObserver observing both `details.phase[id]` and `section[id]`. JS-free fallback uses `:target`.

---

## Controls (topbar) — all four buttons must work

- **Expand all phases** — opens every `details.phase[data-status="done"]` and every `details.req`
- **Collapse all** — closes every `<details>` on the page
- **Print / PDF** — `window.print()`
- **Toggle theme** — toggles `.dark-preview` class on `<html>`; updates button text (☾ Dark theme / ☀ Light theme) and visual pressed state

---

## Print Mode

Mandatory `@media print` block:
- Reset to white background
- Hide TOC and controls
- Force-open all `details.phase[data-status="done"]`
- Hide pending-phase blocks
- Inline URL after each link
- Page-break-inside: avoid on cards, panels, heatmaps, threat charts
- BLUF dark panel → high-contrast white-with-slate-border (no ink-heavy background)

---

## How the Agent Generates Each Artifact

When invoked with a spec folder path and target artifact type:

1. **Read inputs** — `spec-state.json`, every `*.md` artifact in the spec folder, any images referenced.
2. **Validate state** — check `phase.current`, `gates.*.status`, `artifacts.*.content`. Refuse to generate if state is missing required fields.
3. **Pre-generation manifest (MANDATORY).** Before composing any HTML, write a JSON manifest of the verified facts that will appear in the artifact. The manifest is the *only* source of dynamic content the composition step is allowed to read — the reference implementation is the structural template, never a content source.

   ```json
   {
     "spec_id": "{feature-id}",
     "spec_title": "{from state.meta.feature_name}",
     "tier": "{from state.meta.complexity_tier}",
     "il": "{from state.meta.mission_tier}",
     "current_phase": {N},
     "bluf": "{verbatim from 01-problem-statement.md § BLUF, first paragraph}",
     "affected_roles": [
       { "name": "{role name}", "primary": true|false, "pain": "{verbatim pain point}" }
     ],
     "decisions": [
       { "id": "Q1", "text": "{verbatim from intake}", "outcome": "matches|flipped|expanded|deferred", "rationale": "..." }
     ],
     "requirements": [
       { "id": "FR-N", "name": "{verbatim from PRD line}", "release": "v1.0|v2.0", "prd_line": {line_number} }
     ],
     "threat_counts": {
       "vectors_total": {N},
       "p1": {N},
       "p2": {N},
       "p3": {N},
       "by_surface": [
         { "surface": "{name}", "vectors": {N}, "p1": {N}, "p2": {N}, "p3": {N} }
       ]
     },
     "verify_items": [
       { "id": "V-N", "owner": "PM|Eng|Sec|Design", "phase": "{spec/phase}", "title": "...", "status": "open|resolved|deferred" }
     ],
     "traceability": {
       "surfaces": [ "{surface/flow name}" ],
       "rows": [
         {
           "requirement_id": "FR-N",
           "requirement_text": "{verbatim from PRD}",
           "row_status": "covered|partial|gap|deferred",
           "cells": [
             { "surface": "{surface}", "status": "COVERED|PARTIAL|GAP|DEFERRED|OUT_OF_SCOPE", "note": "...", "severity_if_gap": "P1|P2|P3|null" }
           ]
         }
       ],
       "covered": {N}, "partial": {N}, "gaps": {N},
       "coverage_percentage": {N}
     },
     "decisions_log": [
       { "when": "{date}", "phase": "{N}", "what": "{one-line summary}" }
     ],
     "compliance_frameworks": [
       { "name": "NIST 800-N", "implication": "..." }
     ],
     "cross_specs": [
       { "spec_id": "...", "relationship": "..." }
     ]
   }
   ```

   Every value in the manifest must be traceable to a specific source: a line in the source markdown, a JSON
   path in `spec-state.json` (e.g. `state.meta.mission_tier`, `state.phase.current`, `state.gates.phase_4.status`
   — these are the correct citation for fields like `tier`/`il`/`current_phase` above, which have no markdown
   line to point to), or another artifact's path. If a value cannot be sourced from any of these, mark it `null`
   and surface it as a `MANIFEST_GAP` in the audit log — do not fabricate. Log which citation type backed each
   value (`markdown-line` | `state-path` | `artifact-path`) so the audit trail shows real provenance, not just
   presence.

4. **Select pattern** — per the table above (Pattern Selection per Phase).
5. **Plan modules** — based on `phase.current` and the chosen artifact type.
6. **Compose body** — assemble the HTML, inlining all token CSS, module CSS, and progressive-enhancement JS. **Pull all dynamic content from the manifest, never from the reference implementation.** **Every manifest value inserted into HTML must be escaped for its context:** HTML-entity-escape (`&`, `<`, `>`, `"`, `'`) for text content and attribute values; for any URL-typed value, validate the scheme (only `#`, relative paths, or `mailto:` — never `javascript:`) before insertion. The manifest being a controlled artifact does not exempt it — verbatim-sourced text (BLUF, requirement text, PRD lines) can still contain characters that break HTML structure.
7. **Validate output (IL-honest gates) — network-reference sweep.** Before the literal greps below, sweep for any construct capable of a network reference: **URLs anywhere in the file** (`https://`, `http://`, protocol-relative `//host/...`, not just in `src`/`href`); **CSS** `url(...)` / `@import` / `@font-face` with a network `src`; **dynamic resource assignment** (`.src =`, `.href =`, `.action =`, `setAttribute("src"`, `setAttribute("href"`); **network APIs** (`fetch(`, `XMLHttpRequest`, `sendBeacon(`, `new WebSocket(`, `ws://`, `wss://`, `new EventSource(`, `importScripts(`); **resource hints/redirects** (`rel="preconnect"`, `dns-prefetch`, `prefetch`, `preload`, `<meta http-equiv="refresh"` with a non-fragment target). Then, as defense-in-depth, grep the literal set: `cdn.`, `jsdelivr`, `unpkg`, `cdnjs`, `<script src`, `<link rel="stylesheet"`, `@import url`, `fetch(`, and any networked web font. Confirm zero hits on both passes. Confirm light is the initial paint with no JS, the `<noscript>` block is present, every collapsible is native `<details>`, any diagram is inline `<svg>` (no runtime mermaid CDN), every badge pairs color+text, interactive elements carry ARIA + keyboard handlers, every internal ID self-resolves, and every manifest-sourced value was escaped for its insertion context (no raw `<`/`>`/unescaped quotes from manifest text appearing in output markup). Any failure → do not write; emit `RENDER_FAIL`.
8. **Run Example-Data Guardrail** — see below.
9. **Write to** — `specs/{feature-id}/{artifact-name}.html` (per-phase) or `specs/{feature-id}/spec.html` (master).
10. **Log to state** — append a `RENDER_HTML` audit entry with timestamp, artifact name, manifest source-line citations, and module count.

---

## Agent Self-Check Before Returning

**IL-Honest hard gates — any unchecked box = do not emit (fail the render):**
- [ ] **Light default:** initial paint is light with no JS and no stored preference; theme is not chosen from `localStorage`/`prefers-color-scheme` at load
- [ ] **JS-off survival:** every collapsible is native `<details>` (completed-phase blocks carry `open`); `<noscript>` fallback block present right after `<body>`; no content reachable only via JS
- [ ] **No external CDN:** the full network-reference sweep from step 7 above passes (URLs anywhere in the file, CSS `url()`/`@import`/`@font-face`, dynamic `.src`/`.href` assignment, `fetch`/`XMLHttpRequest`/`WebSocket`/`EventSource`/`sendBeacon`, resource-hint `<link>`s, meta-refresh) — zero hits, plus the literal `cdn.`/`jsdelivr`/`unpkg`/`cdnjs` grep as defense-in-depth
- [ ] **Diagrams pre-rendered:** any Mermaid/diagram is inline `<svg>` — built via `mmdc`, or hand-authored per the fallback pattern (§16) when `mmdc` is unavailable, provided it still satisfies the inline-SVG and accessibility checks; **no runtime mermaid CDN script** anywhere in the file
- [ ] **WCAG 2.1 AA:** every status/severity badge pairs color + text (never color alone); contrast ≥ 4.5:1 body / 3:1 large+UI in both themes
- [ ] **ARIA + keyboard:** interactive elements (heatmap cells, flowchart nodes, kanban cards, toggle) have meaningful `role`, `aria-label`, `tabindex`, Enter/Space handlers, and a visible `:focus-visible` style
- [ ] **Self-resolving refs:** every `FR-N`/`EC-N`/threat/control ID renders its full gloss inline (in the DOM + `aria-label`), not a bare code

**Structure & content:**
- [ ] All tokens declared in `:root`; dark-preview variables declared in `html.dark-preview`
- [ ] Masthead present with eyebrow + h1 + pills; all pills the same height (28px)
- [ ] Skim layer reads in <60s (masthead + BLUF + summary band + VERIFY rail) before the deep body
- [ ] BLUF panel present and dark-slate
- [ ] VERIFY rail present (empty or populated)
- [ ] Phase timeline uses explicit dot-column with per-segment line; last entry hides its line
- [ ] Every completed phase has a `<details class="phase">` block
- [ ] Pending phases collapsed into a single block (not individual stubs)
- [ ] All four buttons (`expandAll`, `collapseAll`, `print`, `toggleTheme`) have working `onclick` handlers
- [ ] Footer cites the regeneration command and canonical source
- [ ] Print mode CSS block is present (popovers flatten inline; dark surfaces → high-contrast white)
- [ ] Canonical output path used (`specs/{feature-id}/...`); not written to Confluence
- [ ] No hallucinated FR numbers, threat counts, or coverage statuses
- [ ] **Traceability heatmap (when generated):** every cell status sourced from `traceability-checker` output / `state.artifacts.traceability_matrix`; cells pair color + symbol + (in `aria-label`) text; row rollup = worst applicable status; rendered as an internal/review surface, not a gate-blocking appendix
- [ ] **Phase-5 flowchart:** diagram is inline `<svg>` (hand-authored or `mmdc`-built); no runtime Mermaid CDN; routing prose replaced by the diagram + branch table
- [ ] Example-Data Guardrail check passes (see below)

---

## Outputs — canonical output-path convention

**One convention, everywhere: all surfaces for a spec live under `specs/{feature-id}/`, with per-phase artifacts in their phase subfolder and the living master at the folder root.** The HTML living surface is the primary pre-spec (Phases 1–6) deliverable; do not write these to Confluence (that is the Phase 7/8 surface).

Per spec project (canonical paths):
- `specs/{feature-id}/spec.html` — the living master surface (single file); the primary shareable artifact for Phases 1–6
- `specs/{feature-id}/phase-4-ideation/options.html` — Phase 4 option comparison
- `specs/{feature-id}/phase-5-flow/{flow-name}.html` — Phase 5 flowchart per major flow
- `specs/{feature-id}/traceability-heatmap.html` — coverage grid (standalone view)
- `specs/{feature-id}/verify-board.html` — per-spec VERIFY kanban tracker (lives next to `spec.html`)

Workspace-level (only for genuinely cross-spec artifacts):
- `workspace/pr-review-{n}.html` — PR review writeups (ux-pr-reviewer-agent output; not part of the per-spec pre-spec surface)

Naming rules: lowercase kebab-case `{feature-id}` matching `spec-state.json::meta.feature_id`; phase subfolders named `phase-{N}-{slug}`; one `spec.html` per spec folder (never a second master). The footer's `spec render {feature-id}` command regenerates against these exact paths.

---

## Reference Implementations

The canonical examples ship at `process-improvements-pilot/`:
- `spec-html/hierarchical-attributes.spec.html` — the master spec.html
- `traceability-sample/heatmap.html` — interactive heatmap with side panel
- `phase-4-ideation/options.html` — option comparison (Phase 4)
- `phase-5-flow/flow-diagram.html` — interactive flowchart (Phase 5)
- `verify-tracker/verify-board.html` — VERIFY kanban tracker
- `dedup-sample/` — citation pattern before/after
- `frontmatter-samples/` — frontmatter block examples

When unsure how a module should look, open the reference implementation in a browser and inspect.

The `html-effectiveness-main/` folder contains 20 source patterns from Anthropic. Reference them when extending:
- `01-exploration-code-approaches.html` — comparison of options (Phase 4)
- `02-exploration-visual-designs.html` — visual layout options
- `03-code-review-pr.html` — annotated diff with margin notes (PR reviewer)
- `04-code-understanding.html` — module map / box-and-arrow diagram
- `05-design-system.html` — tokens + component sheet
- `06-component-variants.html` — variant grid
- `09-slide-deck.html` — arrow-key deck (for executive summaries)
- `11-status-report.html` — stat cards + timeline + shipped table + velocity SVG
- `12-incident-report.html` — TL;DR + timeline (dots) + root cause + action items
- `13-flowchart-diagram.html` — interactive flowchart (Phase 5)
- `14-research-feature-explainer.html` — TLDR + collapsible steps + tabbed code + FAQ (Phase 2)
- `15-research-concept-explainer.html` — interactive demo + glossary aside (hover-link)
- `16-implementation-plan.html` — milestones timeline + data flow + mockups + risks (Phase 3, 7)
- `17-pr-writeup.html` — TLDR + before/after + file-by-file + focus + tests + rollout (PR reviewer)
- `18-editor-triage-board.html` — kanban + drag/drop + markdown export (VERIFY tracker)
- `19-editor-feature-flags.html` — toggle list with dependency callouts
- `20-editor-prompt-tuner.html` — live editable template + multi-input preview

---

## 🛑 Example-Data Guardrail

**The reference implementation is content-anchored to `hierarchical-attributes`** — its FR list, threat counts, role names, and decisions log are pulled from that spec's real artifacts. **Do NOT copy that data into a new spec's HTML.**

When generating for a different spec, every one of the following must be re-derived from the target spec's own artifacts:

- BLUF copy → from target spec's `01-problem-statement.md` § BLUF
- Affected roles → from target spec's `01-problem-statement.md` § Affected Roles
- Intake decisions table → from target spec's intake-clarification rounds
- Requirements (FRs, ACs, release tags) → from target spec's `03-prd.md` § Story sections
- Threat vector counts → from target spec's `03-threat-model.md` § Findings Summary
- Decisions log entries → from target spec's `spec-state.json::audit_log`
- Compliance footprint cards → from target spec's `02-research-brief.md` § Standards
- Cross-spec coordination → from target spec's `01-problem-statement.md` § Cross-Spec Coordination

**Agent self-check (mandatory before emitting):**

1. Scan the generated HTML for tokens from the example: `Hierarchical Attributes`, `Five Eyes`, `Jade-class`, `O-4`, `DoDM 5200.01`, `administration.go:38–41`, `Q1`–`Q10`, `FR-1`–`FR-18`, `PRD-VPM-1`–`PRD-VEL-4`, `Compass`, `Zero Trust ABAC`. If any appear in the generated output AND the target spec is not `hierarchical-attributes`, **fail the render** and report the verbatim-copy violation.

2. Verify each FR-N label in the generated output matches the FR-N entry in the target spec's PRD by line number. Refuse to generate if the FR-N referent cannot be resolved.

3. Verify threat-vector counts match the target threat model's Findings Summary table verbatim.

If any check fails, emit a `RENDER_FAIL` audit entry with the specific violation and do not write the HTML.
