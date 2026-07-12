# FarmFriend — Aerial Intelligence

> Agricultural drone vision AI on Apple Silicon. A two-machine pipeline that
> tracks cattle, surveys crops, reads ear tags, and produces field reports
> from drone footage — running locally.

This is the **design system** for FarmFriend's Aerial Intelligence product
line — the visual and editorial foundations for any UI, marketing surface,
slide deck, or report that carries the brand.

---

## The product, briefly

Aerial Intelligence is built on three vision models stitched into one
pipeline:

| Stage     | Model                                         | Job                                         |
|-----------|-----------------------------------------------|---------------------------------------------|
| Tracking  | SAM 3.1 (`mlx-community/sam3.1-bf16`)         | per-frame masks + persistent track IDs      |
| Grounding | Falcon Perception (`tiiuae/Falcon-Perception`)| expression-level detect / segment / OCR     |
| Reasoning | Gemma 4 26B (`mlx-community/gemma-4-26b...`)  | field reports, anomaly calls, Q&A           |

The local entry points are a Python CLI (`visionbrain detect | segment |
track | analyze | ocr`) and a "Ground Control" web UI for drag-and-drop
analysis of drone footage.

The brand promise is **calm, local, accountable**: weights live in your
Hugging Face cache; results live on your disk; no subscription, no sync,
no cloud. The UI should feel like that — an operator's instrument, not a
SaaS dashboard.

---

## Aesthetic direction — read this first

The product is a **professional operator's terminal**. Not cyberpunk, not
flamboyant.  Think Bloomberg Terminal modernized, or Vercel's CLI in a
field office. The previous TERRA·VISION shell had the right DNA (mono,
dark canvas, status orbs, hairline panels) but pushed too far into tactical
sci-fi — neon green, scanlines, "MISSION COMPLETE" flashes. **We strip that
out.** What remains is the same operator's grammar — but elegant.

The five non-negotiables:

1. **Monospace voice** — JetBrains Mono everywhere in the interface. The
   only escape from mono is **Spectral serif**, reserved for long-form
   field reports and editorial slide bodies.
2. **One restrained accent — warm amber** (`#d4b572`, "wheat"). Used
   sparingly: one focal point per view. No green glow. No gradients.
3. **Hairlines, not shadows.** Every divider is 1 px `--rule`. Avoid
   drop-shadows entirely; if you need separation, inset a hairline.
4. **Lowercase voice.** Buttons, statuses, labels lean lowercase or small
   caps. Uppercase only for status codes (`READY`, `MISSING`) and eyebrow
   labels.
5. **Quiet motion.** 120–280 ms with `cubic-bezier(.2,0,0,1)`. No bounces,
   no scanlines, no pulses, no flash overlays.

---

## Sources used to build this system

The system was reverse-engineered from the public visionbrain repository
and the surrounding FarmFriend product line.  All links below — explore
them to do an even better job of branded design work:

| Source | URL |
|---|---|
| visionbrain (vision pipeline + Ground Control UI)      | https://github.com/0-CYBERDYNE-SYSTEMS-0/visionbrain |
| aerial-intelligence-v3 (5-stage analysis pipeline)     | https://github.com/0-CYBERDYNE-SYSTEMS-0/aerial-intelligence-v3 *(private)* |
| FarmFriend Terminal React                              | https://github.com/0-CYBERDYNE-SYSTEMS-0/FarmFriend-Terminal-React |
| FFT_nano (autonomous farm coworker)                    | https://github.com/0-CYBERDYNE-SYSTEMS-0/FFT_nano |
| farmfriend-landing                                     | https://github.com/0-CYBERDYNE-SYSTEMS-0/farmfriend-landing |
| FarmFriend Consulting page                             | https://github.com/0-CYBERDYNE-SYSTEMS-0/farmfriend-page |

The primary source-of-truth for this system was `visionbrain` — its CLI
output, `SPEC.md`, and `src/visionbrain/static/index.html` Ground Control
UI.

---

## CONTENT FUNDAMENTALS — how FarmFriend talks

### Voice
The product is built and run by one operator-engineer. The voice is the
voice of a senior field engineer writing notes for another one: **precise,
plain, faintly dry**. It never sells. It rarely exclaims. It tells you
what the system is and what it just did.

### Casing
- **Lowercase** for body copy, button labels, captions.
- **Small caps / uppercase** ONLY for: status codes, eyebrow section
  labels, key data labels.  E.g. `READY`, `MODEL INTEL`, `FRAMES`.
- **Sentence case** for headings, never Title Case.
- Acronyms stay uppercase: `SAM 3.1`, `MLX`, `OCR`, `CLI`.

### Pronouns
- "you" addresses the operator directly: *you can run this locally*.
- "we" is rare — only when describing pipeline behavior:
  *we re-run the backbone every N detections*.
- "I" — never.

### Tone — concrete examples

✅ **In voice:**
- "ready" / "missing" / "cached"
- "12 cows tracked across 240 frames"
- "weights live in your hugging face cache"
- "run locally. no subscriptions."
- "drop drone footage to begin"
- "field report — pasture 4, 14:32"

❌ **Out of voice:**
- "ALL SYSTEMS GO" → use `READY` or "all models ready"
- "MISSION COMPLETE" → use "complete" or "report ready"
- "Welcome to FarmFriend!" → no welcome flourishes
- "🚀 Get started" → no emoji, no rocket metaphors
- "Revolutionary AI-powered..." → never market-speak

### Emoji
**Not used.**  In their place: geometric Unicode glyphs (`◆ ◇ ⬡ ▷ ⊞ ▌ →`)
and small caps status text. See ICONOGRAPHY below.

### Numbers + units
Always with units, always tabular-aligned.
- `4.73 GB`, `120 ms`, `7.3 tok/s`, `0.15 thresh`
- never `4.73GB` (always a space)
- normalized coordinates: `cx=0.137 cy=0.718` — three decimals
- timestamps: `t=14.2s` or `14:32` (HH:MM), never AM/PM

### Microcopy patterns
- Empty states say what to do next: *"drop drone footage to begin"*.
- Errors name the thing and the fix: *"sam 3.1 not ready — run
  `huggingface-cli download mlx-community/sam3.1-bf16`"*.
- Loading states are honest: *"tracking · frame 142/240"*, not
  *"working magic..."*.
- Status badges use four states only: `READY`, `CACHED`, `MISSING`,
  `CHECKING`.

---

## VISUAL FOUNDATIONS

### Colors

**Canvas + surfaces** — a warm near-black with a faint olive cast (the
agricultural cue is in the chroma, not in literal green). Lift via
hairlines, never via shadow.

| Token         | Value     | Use                                       |
|---------------|-----------|-------------------------------------------|
| `--canvas`    | `#0e100d` | viewport background                       |
| `--surface-2` | `#181b16` | panels                                    |
| `--surface-3` | `#1f221c` | lifted (popovers, hover)                  |
| `--surface-4` | `#262a23` | strongest lift                            |

**Ink scale** — text descends from warm bone to scaffolding.

| Token     | Value     | Use                                |
|-----------|-----------|------------------------------------|
| `--ink-1` | `#ebe5d2` | primary text                       |
| `--ink-2` | `#b8b29f` | secondary                          |
| `--ink-3` | `#807a68` | tertiary, captions                 |
| `--ink-4` | `#555044` | labels, disabled                   |
| `--ink-5` | `#383428` | dimmest scaffolding                |

**Accent — wheat amber.** `#d4b572`. Used sparingly. One focal element
per view: an active tab, a cursor, the launch button, a key data figure.
If you find yourself painting two amber things, demote one.

**Semantic — muted, never neon.**

| Token     | Value     | Use                                |
|-----------|-----------|------------------------------------|
| `--ok`    | `#8fa97a` | sage — ready, success              |
| `--warn`  | `#c89766` | clay — checking, caution           |
| `--err`   | `#b66150` | rust — missing, error              |
| `--info`  | `#7e94a6` | slate — informational              |

**Paper surface** (`--paper #f3eee2`) is reserved for **field reports**
and **editorial slide bodies** — the system literally renders prose on a
warm paper surface, the way a printed report would arrive. The contrast
to the dark terminal is intentional: the terminal *runs the pipeline*;
the paper *delivers the finding*.

### Type

- **JetBrains Mono** carries the entire interface. Weights 300 / 400 /
  500 / 700.  OpenType features `ss01 ss02 cv02 cv03 zero` enabled —
  this kills the dotless zero (we want a slashed zero, terminal-style).
- **Spectral** carries field reports and editorial bodies on paper. It
  pairs with mono naturally — both have technical proportions.
- **No sans serif.** Ever. The pairing is mono + serif. A sans would
  immediately read as "SaaS."

Tracking matters. Caps labels use `letter-spacing: 0.16em` minimum;
data uses 0; running text uses 0.

### Spacing

A clean 4-pixel scale: `4 · 8 · 12 · 16 · 20 · 24 · 32 · 40 · 48 · 64 ·
80`. Gutters between major regions are `--s-4` (16). Within panels,
content padding is `--s-3` (12). Stat grids use 0 gap with hairlines
between cells — let the rules do the spacing.

### Borders, radii, shadows

- **Borders are hairlines.** `1px solid var(--rule)` (`#292d25`). When
  emphasis is needed, swap for `--rule-strong` (`#3a3e34`).
- **Radii are tiny or absent.** `0` for layout containers and tabs;
  `2px` for inputs and chips; `4px` for cards if needed. Pills are
  reserved for status dots only.
- **Shadows are forbidden.** If two surfaces need separation, use a
  hairline. The only legal shadow is `inset 0 0 0 1px var(--rule)`
  (which is just a hairline drawn inward).

### Backgrounds + texture

- The canvas carries a **single, very subtle 26 px dot grid** at
  ~4 % opacity — barely perceptible, a tooling cue. It is **off by
  default** in slides and reports.
- No full-bleed photography in product UI. Imagery — drone stills, crop
  rows, livestock — is contained in framed video / image regions with
  **corner brackets** at all four corners (1.5 px, accent or ink-3,
  16 px arms). The brackets are the closest thing this brand has to
  ornament.
- **No gradients.** Anywhere.
- **No glow / drop shadow / scanlines / vignettes.** These are the four
  things the old TERRA·VISION shell did that we explicitly do not.

### Imagery tone

- Drone stills feel **warm, daylit, slightly dusty** — fields at golden
  hour, not cold-tinted machine vision. Apply a faint warm tint
  (`hue-rotate(-4deg) saturate(0.92)`) if source footage reads too
  cool / clinical.
- Pixel-accurate masks render in **muted sage / clay / amber** — never
  neon. The Set-of-Marks viz already uses Falcon's palette; we tone its
  saturation by ~15 %.

### Motion

- Duration: 120 / 180 / 280 ms — that's it.
- Easing: `cubic-bezier(0.2, 0, 0, 1)` for everything. No bounces.
- The only animated element by default is a **slow status pulse** on
  active dots (2.5 s ease-in-out, opacity-only — no glow).
- Page transitions: none. Tab switches: a 120 ms cross-fade at most.
- The old shell's animated logo-scan, orb pulses, MISSION-COMPLETE
  flash, fill-line animations — **removed**.

### Hover & press states

- **Hover** on interactive surface: text color steps from `ink-2` →
  `ink-1`; border steps from `rule` → `rule-strong`. No fills, no
  brightness boost.
- **Press**: no transform, no shrink. A 60 ms color step is enough.
- **Active / selected**: 2 px left border in `--accent` OR full text
  swap to `--accent`. Never both.
- **Focus**: 1 px outline in `--accent` at `outline-offset: 2px`.

### Transparency + blur

- Sticky bars (the top header, the bottom config bar) use
  `background: rgba(14, 16, 13, 0.94)` with `backdrop-filter: blur(8px)`.
- Everything else is opaque.
- No translucent panels in the body. The eye should not have to
  resolve depth ambiguity.

### Layout rules

- Three-column workspace for the operator UI: **246 px intel / fluid
  main / 372 px ops log**.
- Fixed 56 px header, 58 px config bar at the bottom of operator views.
- Slides are 1280 × 720 (16:9). Print/report pages are A4 portrait on
  the paper surface.
- Content does not exceed 64 ch line length in serif prose; mono prose
  can run wider (88 ch).

### What cards look like

- Background `--surface-2`, border `1px solid var(--rule)`, radius
  `--r-2` (4 px) max, **no shadow**.
- A header strip with `--t-eyebrow` label and an optional status pill.
- Content uses a 12 px inset.
- Hover state: border → `--rule-strong`. That's all.

---

## ICONOGRAPHY

The brand uses **geometric Unicode glyphs and minimal stroked SVGs** —
no icon font library, no emoji.

### Glyph set (lifted directly from the existing CLI / Ground Control)

| Use                  | Glyph  | Notes                          |
|----------------------|--------|--------------------------------|
| brand mark / hex     | `⬡` `⬢` | the hexagon is the only logo |
| drop-zone / file     | `⬡` `◈` `⬟` `⊞` | rotated through tabs |
| play / launch        | `▶`    | always paired with a verb     |
| step indicator       | `▷`    | for "next" / pipeline arrows  |
| download / save      | `↓`    | terminal arrows               |
| copy                 | `⎘`    | bracket-corner glyph           |
| expand               | `⛶`    | corner brackets — same DNA as our frame corners |
| refresh              | `↻`    | clockwise arrow                |
| clear / dismiss      | `⌫` `×` | the × is preferred in elegant contexts |
| status dot           | `●` `○` | filled = active; ring = idle |
| separator            | `·`    | mid-dot, for metadata rows    |
| key result emphasis  | `▌`    | left-bar glyph as a margin tick |
| pipeline join        | `─` `→` | em-dash + arrow, no images   |

### SVGs

- **The brand mark** — the FarmFriend double-F monogram in two
  tones: teal (`#42a4ac`) for the left F, green (`#42b67e`) for the
  right. The SVG fills bind to `--ff-teal` / `--ff-green` CSS custom
  properties so a parent can retheme; set both to `currentColor` for a
  single-color mono lockup. Clear space = the height of one F-stem on
  every side. No outline. No container. The monogram is the only
  branded shape — do not introduce hexagons, shields, circles, or
  wordmark frames.
- **Corner brackets** — 16 px L-shapes at all four corners of any
  image / video region. Stroke: 1.5 px, color: `--ink-3` at rest,
  `--accent` when the region is active or selected.
- **Pipeline orbs** — circles drawn with the same hairline as panels,
  not filled. Stage names typeset *inside* in mono.

### What we never use

- ❌ Emoji of any kind.
- ❌ Filled / colored icon-font sets (Material, Font Awesome).
- ❌ Skeuomorphic illustrations.
- ❌ Hand-drawn / sketch icons.
- ❌ Three-color gradient brand marks.

### Substitutions we made
Where Falcon Perception or the existing Ground Control referenced glyphs
we couldn't ship (e.g. terminal box-drawing characters from a particular
Nerd Font), we use **plain Unicode** equivalents instead — they render in
any browser, no font load required.

---

## Index — files in this design system

| Path                                | What it is                                              |
|-------------------------------------|---------------------------------------------------------|
| `README.md`                         | this file                                               |
| `SKILL.md`                          | machine-readable manifest for Claude Code skill use     |
| `colors_and_type.css`               | every CSS variable and type role — `@import` this first |
| `fonts/`                            | (CDN) JetBrains Mono + Spectral via Google Fonts        |
| `assets/`                           | logo SVGs, corner-bracket SVG, paper texture, samples   |
| `preview/`                          | the cards rendered in the Design System tab             |
| `ui_kits/aerial-intelligence/`      | a working Ground Control recreation + JSX components    |

To use in a new file:
```html
<link rel="stylesheet" href="colors_and_type.css">
<body class="t-body">
  <h1 class="t-h1">field report — pasture 4</h1>
  <p class="t-eyebrow">14:32 · 240 frames · 12 cattle</p>
</body>
```

---

## Caveats

- **Fonts:** the system uses JetBrains Mono and Spectral via Google
  Fonts (CDN). If you require local font files for offline use or
  brand-locked typography, replace these with self-hosted weights —
  ideally **Berkeley Mono** (paid) and **Söhne Mono** as alternates
  if your brand owns licenses.
- **Logo:** the FarmFriend brand mark is the **double-F monogram** in
  teal + green, shipped as `assets/logo.svg`, `assets/logo-mark.svg`,
  and `assets/logo-lockup.svg`. Fills are bound to `--ff-teal` /
  `--ff-green` CSS variables so any page can retheme. The earlier
  hexagon mark (lifted from visionbrain's favicon) has been retired.
- **Aerial Intelligence v3** is private — we could not read it. If
  newer brand decisions live there, please re-attach the repo or copy
  in any updated tokens / logos.
