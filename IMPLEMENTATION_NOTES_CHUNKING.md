# Implementation Notes: Temporal Chunking for Large Videos

**Date:** 2026-05-20
**Problem:** SAM 3.1 OOMs on videos >~30 seconds (1.17 GB neighborhood.mp4 killed at `every=5, res=512`)
**Root cause:** SAM 3.1 on M2 Pro (32GB) accumulates ~8-10 GB per detection frame at 4K. Long videos exhaust memory and/or take extremely long per frame.

---

## Architecture: Temporal Chunking + Pre-Downsampling

### Layer 1: Pre-Downsampling (NEW)

When source video width > 2× SAM resolution (e.g., 4K source with res=512 → 3840 > 1024),
ffmpeg extracts chunks at `resolution * 2` width (preserving aspect ratio).

**Why:** SAM processes frames internally at 512px anyway. Feeding 3840px frames means:
- Each frame decode: ~8MB vs ~0.5MB at 1024px
- Pixel scaling in SAM: 3840→512 every frame vs 1024→512
- On M2 Pro @ 4K+60fps: ~5-7 fps detection → ~10 fps at 1024px
- Pre-scaled segments are ~11MB vs ~536MB for raw stream copy

### Layer 2: Temporal Chunking

Splits video into `chunk_duration`-second segments with `overlap_duration`-second overlaps,
processes each through `track_video_with_json()`, then merges results:

1. `ffmpeg -ss START -t DURATION` extracts each chunk (with `-vf scale` if downsampling)
2. SAM 3.1 processes each chunk independently → detections JSON + annotated video
3. Frame indices and timestamps are remapped to global coordinates
4. Track IDs are offset-remapped (global_max + 1 per chunk) for uniqueness
5. Annotated video chunks are concatenated with `ffmpeg -f concat`
6. Final merged JSON written with `chunked: True` metadata

### Layer 3: Auto-Chunking Detection

CLI `--chunk-duration 0` (default) auto-enables chunking for videos >60 seconds.
Videos shorter than chunk_duration are processed without chunking.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Offset-remap track IDs instead of IoU matching | Simpler, deterministic, no false merges. Tradeoff: same object gets different IDs across chunks. Future: can add post-hoc IoU merging. |
| `max_width = resolution * 2` for downsampling | 2x SAM resolution preserves detail while cutting decode time by ~4x. SAM internally resizes to `resolution` anyway. |
| ffmpeg scale filter instead of stream copy | Stream-copy on 4K creates 500MB+ segments that go OOM. Scale+encode creates 11MB segments that process fine. |
| `/tmp` for temp segments | Avoids disk pressure on the volume holding the source video |
| Skip chunk on failure, continue processing | Partial results are better than total failure. Failed chunks are logged. |
| Auto-chunk threshold: 60 seconds | Empirically, 30-60s of 4K@60fps is the OOM boundary on 32GB M2 Pro |

---

## Tradeoffs

| Approach | RAM | Speed | Tracker Continuity | Complexity |
|----------|-----|-------|--------------------|------------|
| Current (no chunking) | OOM on large video | N/A | ✅ Perfect | Low |
| Frame-by-frame | Very low | Slow (I/O bound) | ❌ Lost | Medium |
| Segment chunking | ~8-10 GB/chunk | Fast (ffmpeg copy) | ✅ In-segment, ⚠️ cross-segment needs IoU | Medium-High |
| Targeted extraction (FastScan + chunk) | ~6-8 GB | Fastest | ✅ In-region, ⚠️ cross-boundary | High |
| **Chunking + Pre-downsample** | **~4-5 GB** | **~10 fps @ 1024px** | **✅ In-segment** | **Medium** |

**Chosen: Chunking + Pre-downsample** — best RAM/speed tradeoff for 4K footage on M2 Pro.

---

## Test Results

- **Video:** neighborhood.mp4 (1.17 GB, 3840x2160, 59.9 fps, ~90s)
- **Settings:** `every=30, res=512, threshold=0.10, chunk-duration=30, chunk-overlap=2`
- **RAM:** Peak ~4.3 GB (down from OOM with no chunking)
- **Time:** ~12 minutes total (3 chunks)
- **Output:** 1024x576 MP4, 83 processed frames, ~1633 detections
- **Resolution:** Source 3840px → chunks downsampled to 1024px → SAM processes at 512px internally

### Before chunking (OOM)
- 4K source, no downsampling → OOM killed at ~2 min
- Stream copy segments → 536MB per segment → disk exhausted at 99% capacity

### After chunking + downsampling
- 4K source → 1024px segments (~11MB each) → no OOM, no disk pressure
- Processing ~10 fps per detect frame (vs ~5-7 fps at 4K)

---

## Critical Finding: Disk Space

**The 1.17 GB neighborhood.mp4 test file cannot be chunk-processed with stream-copy extraction because the disk was at 99% capacity (226 MB free).** A 30-second MP4 segment copied from a 1.17 GB video is ~200-300 MB.

The downsampling fix resolves this: scaled segments are ~11 MB instead of ~536 MB.

**Recommendation:** Maintain at least 2 GB free disk for video processing with large files.

---

## Files Modified

- `src/visionbrain/sam3_inference.py` — `track_video_chunked()`, `_extract_segment()` (with max_width downsampling), `_concat_segments()`, `_iou_match_track_ids()`
- `src/visionbrain/cli.py` — `--chunk-duration`, `--chunk-overlap` flags, auto-chunking logic
- `src/visionbrain/web_app.py` — Form fields for chunk_duration, chunk_overlap
- `src/visionbrain/static/index.html` — CHUNK/OVERLAP UI controls in analyze config pane

---

## Remaining Work

- [ ] Cross-chunk IoU track ID merging (currently uses offset remapping — IDs don't persist across chunks)
- [ ] Concatenation of downsampled chunks produces smaller output — consider re-annotating original video from detections JSON
- [ ] Progress callback for web UI (chunk N/total)
- [ ] Test with `--fast` (FastScan regions integration)
- [ ] Test shorter overlaps (0s, 1s) for efficiency vs continuity tradeoff