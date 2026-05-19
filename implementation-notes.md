# UI Redesign Implementation Notes

Date: 2026-05-19
Target: `src/visionbrain/static/index.html`
Source baseline: `remotes/cyberdyne/main:design-system/handoff/visionbrain/index.html`

## Objective
Redesign Ground Control UI to conform to FarmFriend `design-system` while preserving all existing runtime behavior and API integration points.

## Decisions Made During Implementation

1. Chose the handoff patch file instead of `design-system/src/visionbrain/static/index.html`.
- Reason: `design-system/handoff/CLAUDE-CODE-HANDOFF.md` explicitly states this is the patched replacement for VisionBrain.
- Tradeoff: We trust curated handoff intent over older source variant.

2. Full file replacement rather than incremental CSS-only patch.
- Reason: The UI is a single monolithic HTML file with tightly-coupled CSS + markup + JS strings.
- Tradeoff: Larger diff, but lowest risk for missing required token/voice/styling interactions.

3. Preserved behavior by using the handoff’s backward-compatible variable aliases and unchanged IDs/classes/functions.
- Reason: Existing JS uses legacy CSS vars and specific selectors.
- Tradeoff: Carries alias layer in CSS, but avoids JS regressions.

4. Kept "MISSION" plumbing in JS but retired visual flash behavior.
- Reason: Existing call sites reference `triggerFlash()`; handoff keeps function as no-op.
- Tradeoff: Slight legacy naming remains in code comments/regex compatibility, but UX aligns to new calm-motion spec.

5. Adopted design-system typography strategy from handoff.
- Reason: JetBrains Mono + Spectral is specified in `design-system` docs and encoded in handoff file.
- Tradeoff: External font dependency remains via Google Fonts (as in existing implementation).

## Notable Changes Applied

- Visual identity switched to FarmFriend Aerial Intelligence.
- Neon/glow/scanline/flash-heavy styling retired in favor of restrained hairline system and wheat accent.
- Language/voice shifted toward lowercase/operator tone, while preserving uppercase status/eyebrow labels.
- Existing interaction model, endpoints, and tab/pipeline flow preserved.

## Validation Performed

- Verified replacement source and handoff metadata alignment.
- Spot-checked key compatibility points in resulting file:
  - Status labels remain `READY/CACHED/MISSING`.
  - Completion log line updated to `complete · report ready`.
  - `triggerFlash()` retained as no-op.
  - `scanlines` class retained in DOM but visually disabled via CSS.

## Open Items / Follow-ups

1. Run the app and execute manual UI smoke test from handoff checklist (upload, launch, SSE, tab swaps, downloads) in runtime environment.
2. If desired, split inline CSS/JS into static assets in a later refactor PR (out of scope for this redesign pass).

## 2026-05-19 — Edge Padding / Clipping Patch

### Why this change
- UI chrome could appear too close to viewport edges and risk clipping on devices/browsers with safe-area insets or dynamic viewport UI.

### What changed
- Added viewport-safe tokens in `:root`:
  - `--safe-top/right/bottom/left` from `env(safe-area-inset-*)`
  - `--app-gutter-x/y` as baseline desktop gutters
  - computed `--app-pad-*` as `max(safe-area, gutter)`
- Updated `#app` to apply global outer padding using those tokens.
- Added `height: 100dvh` (with existing `100vh` fallback) to better track dynamic viewport height.
- Explicitly set `#app` `width: 100%` to avoid accidental horizontal crop interactions with padding math.

### Tradeoffs
- Chose minimal, non-structural fix (no breakpoint/panel reflow changes) to avoid behavior risk and keep existing 3-column information density.
- This improves edge safety without solving narrow-screen ergonomics; responsive collapse remains a separate enhancement.
