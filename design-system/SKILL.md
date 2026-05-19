---
name: farmfriend-aerial-design
description: Use this skill to generate well-branded interfaces, slides, reports, and prototypes for FarmFriend Aerial Intelligence — the agricultural drone vision AI product line. Contains the design tokens, JetBrains Mono + Spectral type pairing, wheat-amber accent palette, terminal-shell component patterns, and a working Ground Control UI kit for prototyping.
user-invocable: true
---

# FarmFriend Aerial Intelligence — Design Skill

Read `README.md` in this skill folder first — it covers content
fundamentals, visual foundations, iconography, and the full token system.
Then explore the rest of the manifest.

## When you are invoked

If the user invokes this skill **without other guidance**, ask what they
want to build (a screen mock, a slide deck, a report, a marketing page,
production code) and ask 3–5 short questions to pin down scope. Then act
as an expert designer in this brand and produce HTML artifacts — or
production code if they're working on the real app.

## Quick rules of thumb

- **Type:** JetBrains Mono everywhere in the interface. Spectral (serif)
  only for field-report long-form prose and editorial slide bodies.
  No sans serif, ever.
- **Color:** warm near-black canvas, hairline-only borders. One wheat-
  amber accent (`#d4b572`) per view as a focal point. Semantic colors
  are muted (sage `#8fa97a`, clay `#c89766`, rust `#b66150`, slate
  `#7e94a6`) — never neon.
- **Voice:** lowercase body, small-caps eyebrow labels, uppercase only
  for status codes (`READY`, `MISSING`). Precise, plain, faintly dry.
  Never "MISSION COMPLETE" or "ALL SYSTEMS GO."
- **Surface treatment:** square or 2 px radii. Zero drop-shadows. Corner
  brackets on image / video regions instead of decorative frames.
- **Motion:** 120 – 280 ms, `cubic-bezier(0.2, 0, 0, 1)`. No bounces, no
  pulses on hover, no flash overlays.
- **Iconography:** geometric Unicode glyphs (`⬡ ◆ ▶ ▷ ↓ ↻ ⎘ ⛶ ▌`). No
  emoji. No icon-font sets. The brand mark is a single stroked hexagon
  drawn with hairline SVG.

## What's in this folder

| Path | Purpose |
|---|---|
| `README.md`                     | full brand & system reference |
| `colors_and_type.css`           | every CSS variable and type role |
| `assets/`                       | logo SVGs, corner-bracket SVG |
| `preview/`                      | rendered specimen cards (25 of them) |
| `ui_kits/aerial-intelligence/`  | working Ground Control UI in React + JSX |

## How to use

For **a static design artifact** (mock, slide, report):
1. Create an HTML file in the project root.
2. `<link rel="stylesheet" href="colors_and_type.css">` at the top.
3. Use the `.t-*` type roles and CSS variables from the token system.
4. Copy logo SVGs out of `assets/` rather than redrawing them.
5. Reference component patterns in `preview/` and the JSX components in
   `ui_kits/aerial-intelligence/` for visual fidelity.

For **production code work**, treat `ui_kits/aerial-intelligence/*.jsx`
as the source of truth for component structure. The components are
intentionally simple (mostly inline styles bound to CSS vars) so they
port cleanly into any React or HTML codebase.

## Things to avoid

- Bright / neon greens (that was the previous TERRA·VISION shell; we
  explicitly retired it).
- Drop shadows, glows, scanlines, vignettes, gradients.
- Sans-serif typography in any UI context.
- Emoji and colorful icon fonts.
- Marketing voice ("revolutionary", "AI-powered", "supercharge…").
- Title Case headings.
