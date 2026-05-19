# Aerial Intelligence — UI Kit

The operator interface for FarmFriend's drone analysis pipeline.
A pixel-faithful recreation of the **Ground Control** screen — the same
three-column shell you'll find in `visionbrain/static/index.html`, retuned
to this design system (warm amber instead of electric green, hairlines
instead of glow, lowercase voice instead of tactical UPPERCASE).

## Files

| File | What it is |
|---|---|
| `index.html` | the full Ground Control screen, click-thru fake mission |
| `ui-primitives.jsx` | `<Button>`, `<StatusPill>`, `<Dot>`, `<Eyebrow>`, `<Hex>` |
| `HeaderBar.jsx` | logo lockup, mode tabs, connection status |
| `IntelPanel.jsx` | left column: model intel cards, remote server, mission stats |
| `MainStage.jsx` | center column: drop zone, video frame w/ HUD, pipeline orbs |
| `OpsPanel.jsx` | right column: operations log, detection cards, field report |
| `ConfigBar.jsx` | bottom config bar with query, threshold, launch button |

## Running it

Open `index.html` directly. Click **▶ launch** with a file selected (a
faked "drone footage" mp4 is pre-populated) to watch a mission stream
through. The pipeline animates from `sam 3.1` → `falcon perception` →
`gemma 4 26b` and a field report renders on the paper surface on the
right.

## Coverage

This kit replicates the core operator surfaces from visionbrain:

- header + tab nav (analyze · detect · segment · track · sam-3 · ocr)
- model intel card cluster (left)
- drag-and-drop video / image ingest (center)
- video viewer with corner brackets + HUD readouts
- 3-stage pipeline indicator (orbs joined by hairlines)
- streaming operations log with severity colors
- detection stat grid
- field report rendered on paper surface
- bottom config bar with per-tab options

The OCR, segment, track, sam-3 panes are stubbed to the same drop-zone
shell but their config bars are wired.

## What's intentionally simplified

This is a hi-fi visual recreation, **not a functional reimplementation**.
There is no real FastAPI server, no SSE stream, no MLX inference — the
mission simulator inside `index.html` walks through plausible states with
timeouts. Take any single component and drop it into a real app.
