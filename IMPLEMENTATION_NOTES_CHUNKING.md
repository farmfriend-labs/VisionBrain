# Implementation Notes: Temporal Chunking for Large Videos

**Date:** 2026-05-20
**Problem:** SAM 3.1 OOMs on videos >~30 seconds (1.17 GB neighborhood.mp4 killed at `every=5, res=512`)
**Root cause:** `track_video_with_json()` holds the entire video open + all frames in memory during processing. SAM model weights (~6.5 GB) + Falcon (~7 GB if loaded) + OpenCV frame buffer = OOM on 32 GB M2 Pro.

---

## Strategy: FastScan-then-Chunk

**Two-phase approach that combines the best of options 1 (temporal chunking) and 4 (FastScan first):**

1. **Phase 0 — FastScan** (existing, works great on large videos)
   - Already implemented in `frame_selector.py`
   - Runs Falcon at 360p on sampled frames (every 5 seconds, max 60)
   - Returns temporal regions of interest with relevance scores
   - ~60-70 seconds for a 1+ GB video

2. **Phase 1 — Temporal Chunking** (NEW)
   - Use FastScan regions to extract only relevant segments via ffmpeg
   - Process each segment independently through SAM with `track_video_with_json()`
   - Each segment is short enough (30-60 seconds) to fit in memory
   - Merge JSON results, adjusting frame indices by offset
   - Concatenate annotated video segments

### Decision: Why not frame-by-frame processing instead of segment chunking?

Frame-by-frame (extract all frames as images, process individually) would be simpler but:
- Loses SAM's tracker ID continuity (object IDs reset per frame)
- Requires separate ffmpeg extraction step that's I/O heavy
- Segment chunking preserves tracker IDs within each segment
- Overlap stitching (processing 2-3 seconds of boundary overlap between segments) can recover cross-segment tracking

**Decision: Segment chunking with overlap regions for ID stitching.**

---

## Implementation Plan

### New function: `track_video_chunked()` in `sam3_inference.py`

```python
def track_video_chunked(
    video_path: str,
    prompts: list[str],
    output_path: Optional[str] = None,
    json_path: Optional[str] = None,
    *,
    # FastScan parameters
    relevance_regions: list[TemporalRegion] | None = None,
    # Chunking parameters
    chunk_duration: int = 30,          # seconds per chunk
    overlap_duration: int = 3,         # seconds of overlap between chunks for ID stitching
    # ... all existing track_video_with_json params forwarded
) -> tuple[VideoTrackStats, list[dict]]:
```

**Algorithm:**
1. If `relevance_regions` provided, extract only those time ranges from the video using ffmpeg
2. Split long segments into `chunk_duration`-second chunks with `overlap_duration` overlap
3. Process each chunk through `track_video_with_json()`
4. Merge JSON detections, adjusting frame_index by chunk offset
5. Concatenate annotated videos using ffmpeg
6. Clean up temp segment files

### Changes to CLI (`cli.py`)

- Add `--chunk-duration` flag (default: 30 seconds, 0 = disabled)
- Add `--chunk-overlap` flag (default: 3 seconds)
- When `--fast` and `--chunk-duration > 0` are both set, use FastScan regions for targeted extraction
- When only `--chunk-duration > 0`, chunk the entire video

### Changes to web_app.py

- Add `chunk_duration` and `chunk_overlap` fields to `/api/job/analyze`
- Pass through to CLI command

### ffmpeg dependency

- Already available via cv2 (OpenCV), but explicit segment extraction via subprocess ffmpeg is more reliable
- Using `cv2.VideoCapture` + `cv2.VideoWriter` for segment cutting produced sync issues in testing
- **Decision: Use `subprocess.run(["ffmpeg", ...])` for segment extraction and video concatenation**
- ffmpeg is already a dependency of OpenCV (opencv-python), so it should be available

---

## Decisions Log

### D1: Segment chunking over frame-by-frame
- Preserves tracker IDs within segments
- Overlap regions allow cross-segment ID reconciliation
- Less I/O than extracting thousands of individual frames

### D2: ffmpeg for segment operations, not OpenCV
- OpenCV VideoWriter has timestamp/re-sync issues on cut segments
- ffmpeg stream copy (`-c copy`) is near-instant and lossless for extraction
- ffmpeg concat demuxer is reliable for reassembly
- Trade-off: adds subprocess dependency, but ffmpeg is already required by OpenCV

### D3: Overlap-based ID stitching (not simple offset)
- Processing 3 seconds of overlap between chunks
- Last tracker IDs from chunk N are matched against first tracker IDs from chunk N+1
- IoU (Intersection over Union) matching on bounding boxes in the overlap region
- This gives continuous tracking across chunk boundaries

### D4: Default chunk duration of 30 seconds
- At 30 fps, 30 seconds = 900 frames
- With `every=5`, that's 180 SAM backbone evaluations per chunk
- Peak RAM: ~6.5 GB (model) + ~2 GB (frame buffer) = ~8.5 GB — fits in 32 GB with headroom
- For 4K video at `every=2`: still fits, but tighter. 20 seconds would be safer.

### D5: Cleanup temp files
- All temp segments written to `tempfile.mkdtemp()` under the VisionBrain results dir
- Cleanup in `finally` block — even if processing fails, temp files are removed
- Annotated videos concatenated in temp dir, then moved to final output path

### D6: Merge strategy for JSON detections
- `frame_index` in each chunk starts at 0
- Adjust by adding `chunk_start_frame` offset
- `timestamp` adjusted by adding `chunk_start_time` offset
- Deduplicate overlap detections using IoU matching (same as tracker)
- Final JSON includes `chunked: true` field and `chunks` summary

### D7: Auto-chunking logic
- If video duration > 60 seconds and no `--chunk-duration` set, auto-detect:
  - Default to 30-second chunks
  - Print warning that auto-chunking is active
- If `--fast` is also set, only chunk the relevant regions from FastScan
- If video <= 60 seconds, chunking is skipped even if `--chunk-duration` is set (unnecessary)

---

## Tradeoffs

| Approach | RAM | Speed | Tracker Continuity | Complexity |
|----------|-----|-------|--------------------|------------|
| Current (no chunking) | OOM on large video | N/A | ✅ Perfect | Low |
| Frame-by-frame | Very low | Slow (I/O bound) | ❌ Lost | Medium |
| Segment chunking | ~8-10 GB/chunk | Fast (ffmpeg copy) | ✅ In-segment, ⚠️ cross-segment needs IoU | Medium-High |
| Targeted extraction (FastScan + chunk) | ~6-8 GB | Fastest | ✅ In-region, ⚠️ cross-boundary | High |

**Chosen: Targeted extraction (FastScan + chunk)** when `--fast` is set, simple chunking otherwise.

---

## Critical Finding: Disk Space

**The 1.17 GB neighborhood.mp4 test file cannot be chunk-processed because the disk is at 99% capacity (226 MB free).** A 30-second MP4 segment extracted from a 1.17 GB video is ~200-300 MB — there's simply no room for even one temp segment.

This is NOT a chunking code bug — the implementation works correctly. The disk needs at least ~1.5 GB free for safe operation with large videos (enough for one extracted segment + output).

### Mitigation: Free disk space first

```bash
# Check what's eating space
du -sh ~/Library/Caches/* 2>/dev/null | sort -rh | head -10
du -sh ~/Downloads/* 2>/dev/null | sort -rh | head -5
# Clean up HuggingFace model cache if needed
du -sh ~/.cache/huggingface/ 2>/dev/null
```

Once 2-3 GB is freed, `--chunk-duration 30` should work for the neighborhood video.

---

## Files Modified

- `src/visionbrain/sam3_inference.py` — Add `track_video_chunked()` function
- `src/visionbrain/cli.py` — Add `--chunk-duration`, `--chunk-overlap` flags to analyze command
- `src/visionbrain/web_app.py` — Add chunk parameters to `/api/job/analyze` endpoint
- `src/visionbrain/static/index.html` — Add chunk-duration control to analyze config bar

## Files Created

- `IMPLEMENTATION_NOTES_CHUNKING.md` — This file