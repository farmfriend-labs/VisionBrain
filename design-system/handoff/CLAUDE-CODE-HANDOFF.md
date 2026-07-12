# Claude Code handoff — visionbrain Ground Control brand refresh

This package contains a brand-refresh patch for visionbrain's single-file
Ground Control UI. Apply it to the `visionbrain` repo.

## What's in this folder

| File | Purpose |
|---|---|
| `visionbrain/index.html` | The **patched** version of `src/visionbrain/static/index.html`. Drop in as-is. |

## Target file (in visionbrain repo)

```
src/visionbrain/static/index.html
```

It's a single self-contained HTML file (one `<style>` block, one `<script>`
block, inline SVG favicon, no other static assets). The replacement is also
a single self-contained file.

## What the patch changes

### Brand surfaces (visual only)

1. **Title** — `TERRA·VISION` → `FarmFriend Aerial Intelligence`.
2. **Favicon** — inline hex SVG → inline FarmFriend double-F mark
   (teal `#42a4ac` + green `#42b67e`).
3. **Header logo** — hexagon → FF mark; wordmark `TERRA·VISION` →
   `farmfriend`; sub `v2 · GCS` → `aerial · gcs`.
4. **Typography** — Orbitron + Chakra Petch retired. **JetBrains Mono** is
   the entire interface voice; **Spectral** carries the field-report body
   (paper surface).
5. **Color palette** — neon-green operator theme (`#00ff6a`) replaced with
   the FarmFriend Aerial Intelligence system:
   - canvas `#0e100d` (warm near-black, slight olive cast)
   - accent `#d4b572` (wheat amber, one focal point per view)
   - semantic: sage `#8fa97a`, clay `#c89766`, rust `#b66150`, slate `#7e94a6`
   - new brand tokens: `--ff-teal`, `--ff-green`, `--ff-teal-deep`, `--ff-green-deep`
6. **Decoration retired**: animated logo-scan, glow box-shadows, body radial
   glow, scanlines, orb pulse glow, button glow, gradient header underline,
   MISSION-COMPLETE flash overlay. All replaced with hairlines + opacity-only
   pulses on active dots.
7. **Voice** — lowercase body and buttons (`▶ launch`, `browse files`,
   `↻ refresh status`), uppercase reserved for status codes (`READY`,
   `CACHED`, `MISSING`, `CHECKING`) and eyebrow labels (`MODEL INTEL`,
   `OPERATIONS LOG`). `ALL SYSTEMS GO` → `all models ready`,
   `MISSION COMPLETE` log line → `complete · report ready`.

### What stayed exactly the same (do not touch)

- **All DOM IDs**: `#app`, `#hdr`, `#workspace`, `#intel`, `#main`, `#ops`,
  `#config-bar`, `#flash`, `#mode-tabs`, `#conn-status`, `#conn-dot`,
  `#conn-lbl`, `#model-cards`, `#gemma-remote`, `#st-frames`/`-objects`/`-dets`/`-dur`,
  `#h-frames`/`-objects`/`-dets`/`-fps`/`-dur`, `#video-result`, `#image-result-*`,
  `#rv`, `#rv-track`, `#ri`, `#ri-*`, `#dz-*`, `#dz-file-*`, `#fi-*`,
  `#vwrap`, `#progress-wrap`, `#progress-bar`, `#pipeline`, `#ps-sam`/`-falcon`/`-gemma`,
  `#pl-1`/`-2`, `#ops-log`, `#det-panel`, `#det-cards`, `#report-panel`, `#rc`,
  `#btn-dl-video`/`-json`/`-report`, `#btn-launch-*`, `#btn-expand-report`,
  `#ocr-output`, `#ocr-text`, `#cfg-*`, `#c-*` (all config inputs),
  `#flash-txt` (still present, just hidden).
- **All class names**: `.logo-wrap`, `.logo-hex`, `.logo-text`, `.logo-sub`,
  `.tab-btn`, `.tab-btn.active`, `.conn-dot`, `.conn-dot.ok/warn/err`,
  `.ph`, `.model-card`, `.mc-*`, `.intel-row`, `.ir-lbl/val`, `.stat-grid`,
  `.sg-cell/lbl/val`, `.tab-pane`, `.drop-zone`, `.dz-icon/title/sub/file`,
  `.btn-browse`, `.video-wrap`, `.scanlines`, `.corner.tl/tr/bl/br`,
  `.vid-hud`, `.hud-item/lbl/val`, `.p-stage`, `.orb`, `.p-lbl`, `.p-line`,
  `.ll.i/h/p/w/e/d/s`, `.result-section`, `.rs-body/actions`, `.btn-xs`,
  `.det-cards`, `.dc/dc-v/dc-l`, `.cfg-pane`, `.cf`, `.range-row`, `.rv`,
  `.togs/tog`, `.sep`, `.btn-launch`, `.btn-launch.running`, `.flash-txt`.
- **All JS functions, signatures, behavior**: `S` state object,
  `checkStatus()`, `renderModels()`, `switchTab()`, `dzDragOver`/`Leave`/`Drop`/`Click`,
  `fileChosen()`, `uploadFile()`, `launchJob()`, `connectSSE()`,
  `onJobDone()`, `updatePipelineFromLog()`, `activateStage/doneStage/markStage/markLine`,
  `resetPipeline()`, `showVideo/showImage`, `loadDetectionStats()`, `loadReport()`,
  `renderMarkdown()`, `showOcrOutput()`, `clearOcrOutput()`, `hideResults()`,
  `updateProgress()`, `log()`, `classifyLine()`, `clearLog()`, `downloadResult()`,
  `copyReport()`, `expandReport()`, `enableDl()`, `g()`, `resetBtn()`.
- **All `/api/*` fetch endpoints**: status, upload, job dispatch, SSE stream,
  detections, report, file. URL paths unchanged.
- `triggerFlash()` is now a no-op (kept as a stub so existing call sites
  don't error).

### Backward-compat CSS alias trick

The legacy variable names visionbrain uses inline in JS (`var(--acc)`,
`var(--red)`, etc.) are aliased to the new tokens in `:root`:

```css
--bd:  var(--rule);          --bda: var(--rule-strong);
--acc: var(--accent);        --accd: var(--accent-deep);
--surf:var(--surface-2);     --card: var(--surface-3);
--tx:  var(--ink-1);         --txd:  var(--ink-3);   --txm: var(--ink-4);
--amr: var(--warn);          --red:  var(--err);     --blu: var(--info);
--font-d: var(--font-mono);  --font-u: var(--font-mono);  --font-m: var(--font-mono);
```

So any `style.color = 'var(--acc)'` in the JS still works and now resolves
to wheat amber. No JS color edits were needed.

## How to apply (Claude Code prompt)

Open the visionbrain repo in Claude Code and paste:

> Replace `src/visionbrain/static/index.html` entirely with the contents of
> the file I'll paste next. Do not modify anything else in the repo. The
> replacement keeps every DOM id, class name, and JS function signature
> intact — only CSS, brand SVGs, text labels, and a couple of JS string
> constants change. After replacement, run `python -m visionbrain.app`
> (or however the static server is started) and load the UI in a browser
> to verify the header shows the FF mark, fonts are JetBrains Mono, and the
> drop-zone still uploads. Then create branch `brand/ff-rebrand`, commit
> with message: "Brand: retire TERRA·VISION shell, adopt FarmFriend Aerial
> Intelligence", push, and open a PR against `main`.

Then paste the entire contents of `visionbrain/index.html` from this package.

## Manual smoke-test checklist

After applying:

- [ ] Page loads, no console errors, no missing-font fallback rendering.
- [ ] Favicon is the FF mark (teal+green).
- [ ] Header shows the FF mark, "farmfriend", "aerial · gcs".
- [ ] No green glow anywhere. No scanlines in the video frame. No
      MISSION-COMPLETE flash overlay on job complete.
- [ ] Drop-zone accepts a video, `/api/upload` is called, the launch
      button enables.
- [ ] Click ▶ launch → `/api/job/analyze` dispatches → SSE stream
      populates the ops log → pipeline orbs activate in order → field
      report renders on paper surface when done.
- [ ] Tabs (analyze / detect / segment / track / sam-3 / ocr) all switch
      correctly; their config panes swap; their drop-zones accept files.
- [ ] Status dots pulse gently (opacity only, no glow shadow).

## Things explicitly NOT in this patch

These were flagged in the design-system README as open items; they're
intentionally out of scope here because they would change behavior, not
just paint:

- Berkeley Mono / Söhne Mono swap (we stayed on JetBrains Mono via Google Fonts).
- Field-report layout overhaul (the markdown is still rendered by visionbrain's
  inline `renderMarkdown()`; only the paper-surface styling is new).
- Settings persistence, dark/light theme toggle, multi-language.
- Any backend / Python changes.

If any of those become priorities, they each warrant their own PR.

---

Brand owner: FarmFriend Aerial Intelligence
Design system: `farmfriend-aerial-design` (this project)
Patch generated: 2026-05-19
