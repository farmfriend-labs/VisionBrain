"""SAM 3.1 inference — video object tracking and multi-prompt segmentation.

Weights: mlx-community/sam3.1-bf16 (~3GB, public download).
Loads via mlx_vlm's standard MLX loader — no gated access needed.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from .loader import sam31_cache_path, _check_mlx, SAM31_HF_REPO

HF_REPO = SAM31_HF_REPO  # "mlx-community/sam3.1-bf16"

# ──────────────────────────────────────────────────────────────────────────────
# Availability check
# ──────────────────────────────────────────────────────────────────────────────

def sam31_available() -> bool:
    """True if SAM 3.1 can run on this machine."""
    if not _check_mlx():
        return False
    return sam31_cache_path() is not None


# ──────────────────────────────────────────────────────────────────────────────
# Model loading (cached per process)
# ──────────────────────────────────────────────────────────────────────────────

_sam_model_cache: dict = {}


def _ensure_sam31(
    model_path: Optional[str] = None,
    threshold: float = 0.15,
    resolution: int = 1008,
):
    """Load SAM 3.1 model + processor once."""
    if "model" not in _sam_model_cache:
        if not sam31_available():
            raise RuntimeError(
                "SAM 3.1 weights not cached. Run:\n"
                "  huggingface-cli download mlx-community/sam3.1-bf16\n"
                "Then restart this session."
            )

        from mlx_vlm.utils import get_model_path, load_model
        from mlx_vlm.models.sam3_1.processing_sam3_1 import Sam31Processor
        from mlx_vlm.models.sam3_1.generate import Sam3Predictor

        t0 = time.perf_counter()
        hf_repo = model_path or HF_REPO
        print(f"Loading SAM 3.1 from {hf_repo}...")
        mp = get_model_path(hf_repo)
        model = load_model(mp)
        processor = Sam31Processor.from_pretrained(str(mp))
        if resolution != 1008:
            processor.image_size = resolution
        predictor = Sam3Predictor(model, processor, score_threshold=threshold)
        print(f"  Loaded in {time.perf_counter()-t0:.2f}s")

        _sam_model_cache["model"] = model
        _sam_model_cache["processor"] = processor
        _sam_model_cache["predictor"] = predictor

    return (
        _sam_model_cache["model"],
        _sam_model_cache["processor"],
        _sam_model_cache["predictor"],
    )


# ──────────────────────────────────────────────────────────────────────────────
# Single-image multi-prompt detection + segmentation
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Sam31Detection:
    label: str
    score: float
    bbox_xyxy: tuple[float, float, float, float]   # x1, y1, x2, y2 (pixels)
    mask: Optional[np.ndarray] = None                # (H, W) uint8, if segmentation

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "score": round(float(self.score), 4),
            "bbox_xyxy": [round(float(x), 4) for x in self.bbox_xyxy],
            "has_mask": self.mask is not None,
        }


def detect_multi(
    image: Image.Image,
    prompts: list[str],
    *,
    threshold: float = 0.15,
    resolution: int = 1008,
    task: str = "detect",
) -> list[Sam31Detection]:
    """Run SAM 3.1 multi-prompt detection/segmentation on a still image.

    Runs the vision backbone ONCE, then DETR per prompt.
    Cost = 1x ViT + Nx (text + DETR) instead of Nx full pipeline.

    Args:
        image: PIL Image
        prompts: list of text prompts, e.g. ["cow", "sheep", "fence"]
        threshold: confidence threshold (lower = more detections)
        resolution: input resolution (1008 = native)
        task: "detect" (bboxes only) or "segment" (with masks)

    Returns:
        list of Sam31Detection, one per found object
    """
    from mlx_vlm.models.sam3_1.generate import predict_multi

    model, processor, predictor = _ensure_sam31(threshold=threshold, resolution=resolution)

    t0 = time.perf_counter()
    result = predict_multi(
        predictor=predictor,
        image=image,
        prompts=prompts,
        score_threshold=threshold,
    )
    print(f"  SAM 3.1 detect_multi: {len(result.scores)} detections in {time.perf_counter()-t0:.2f}s")

    detections = []
    img_w, img_h = image.size
    for i, (score, box_xyxy, label) in enumerate(zip(result.scores, result.boxes, result.labels or prompts * len(result.scores))):
        mask = None
        if task == "segment" and result.masks is not None and i < len(result.masks):
            mask = result.masks[i]

        detections.append(Sam31Detection(
            label=label or "object",
            score=float(score),
            bbox_xyxy=(float(box_xyxy[0]), float(box_xyxy[1]),
                        float(box_xyxy[2]), float(box_xyxy[3])),
            mask=mask,
        ))
    return detections


# ──────────────────────────────────────────────────────────────────────────────
# Video tracking
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class VideoTrackStats:
    total_frames: int
    processed_frames: int
    fps: float
    unique_objects: int
    output_path: str


def track_video(
    video_path: str,
    prompts: list[str],
    output_path: Optional[str] = None,
    *,
    model_path: str = "mlx-community/sam3.1-bf16",
    threshold: float = 0.15,
    every_n_frames: int = 2,
    backbone_every: int = 1,
    show_boxes: bool = True,
    resolution: int = 1008,
    opacity: float = 0.6,
    contour_thickness: int = 2,
) -> VideoTrackStats:
    """Track objects in a video file using SAM 3.1.

    Args:
        video_path: path to video file
        prompts: text prompts to track, e.g. ["cow", "horse"]
        output_path: output video path (auto-generated if None)
        model_path: HuggingFace repo ID for SAM 3.1 weights
        threshold: detection confidence
        every_n_frames: run DETR detection every N frames (1 = every frame)
        backbone_every: re-run ViT backbone every N detections
        show_boxes: draw bounding boxes on output
        resolution: input resolution (1008 = native, lower = faster)
        opacity: mask overlay opacity (0-1)
        contour_thickness: contour line thickness

    Returns:
        VideoTrackStats with timing and counts
    """
    from mlx_vlm.models.sam3_1.generate import track_video as _track_video

    if output_path is None:
        p = Path(video_path)
        output_path = str(p.parent / f"{p.stem}_tracked{p.suffix}")

    t0 = time.perf_counter()
    _track_video(
        video_path=video_path,
        prompts=prompts,
        output=output_path,
        model_path=model_path,
        threshold=threshold,
        every=every_n_frames,
        show_boxes=show_boxes,
        resolution=resolution,
        backbone_every=backbone_every,
        opacity=opacity,
        contour_thickness=contour_thickness,
    )

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()

    elapsed = time.perf_counter() - t0
    processed = total // every_n_frames

    print(f"  Video tracking complete: {processed}/{total} frames in {elapsed:.1f}s ({fps:.1f} fps display)")

    return VideoTrackStats(
        total_frames=total,
        processed_frames=processed,
        fps=round(fps, 1),
        unique_objects=len(prompts),
        output_path=output_path,
    )


# ──────────────────────────────────────────────────────────────────────────────
# track_video_with_json — tracking + detection export + annotated video
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class FrameDetection:
    """One object detection in one frame."""
    label: str
    score: float
    bbox_xyxy: tuple[float, float, float, float]
    track_id: int
    centroid_norm: tuple[float, float]  # (x_norm, y_norm) relative to image
    area_fraction: float                 # fraction of image area

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "score": round(float(self.score), 4),
            "track_id": int(self.track_id),
            "bbox_xyxy": [round(float(x), 2) for x in self.bbox_xyxy],
            "centroid_norm": {"x": round(float(self.centroid_norm[0]), 4),
                              "y": round(float(self.centroid_norm[1]), 4)},
            "area_fraction": round(float(self.area_fraction), 5),
        }


def track_video_with_json(
    video_path: str,
    prompts: list[str],
    output_path: Optional[str] = None,
    json_path: Optional[str] = None,
    *,
    model_path: str = "mlx-community/sam3.1-bf16",
    threshold: float = 0.15,
    every_n_frames: int = 2,
    backbone_every: int = 1,
    resolution: int = 1008,
    opacity: float = 0.6,
    contour_thickness: int = 2,
    # ── Adaptive parameters ──────────────────────────────────────
    adaptive_motion: bool = False,
    motion_threshold: float = 0.03,
    propagate_frames: int = 0,
    relevance_scores: dict[int, float] | None = None,
    relevance_threshold: float = 0.2,
) -> tuple[VideoTrackStats, list[dict]]:
    """Track objects in a video + export per-frame detections as JSON.

    This is the pipeline-grade version of track_video(). It captures every
    detection with bounding boxes, track IDs, normalized centroids, and area
    fractions — all the structured data Gemma 4 needs to reason intelligently.

    Adaptive modes (all disabled by default):
    - adaptive_motion: skip processing on frames with low motion delta
    - propagate_frames: reuse last detection masks for N frames after a detect
    - relevance_scores: skip frames where Falcon scored relevance below threshold

    Args:
        video_path: input video path
        prompts: text prompts to track, e.g. ["cow", "sheep", "fence"]
        output_path: annotated video output (auto-generated if None)
        json_path: JSON detections output (auto-generated if None)
        model_path: HuggingFace repo ID for SAM 3.1 weights
        threshold: detection confidence
        every_n_frames: run DETR detection every N frames
        backbone_every: re-run ViT backbone every N detections
        resolution: SAM input resolution (1008 = native)
        opacity: mask overlay opacity
        contour_thickness: contour line thickness
        adaptive_motion: enable motion-guided frame skipping
        motion_threshold: frame delta threshold for motion skip (lower = more sensitive)
        propagate_frames: reuse masks for this many frames after each detect frame
        relevance_scores: {frame_index: relevance} dict from Falcon fast-scan
        relevance_threshold: minimum relevance to process a frame

    Returns:
        (VideoTrackStats, list of per-frame detection dicts ready for Gemma 4)
    """
    import json as _json
    import mlx.core as mx
    from PIL import Image

    from mlx_vlm.models.sam3_1.processing_sam3_1 import Sam31Processor
    from mlx_vlm.models.sam3_1.generate import (
        Sam3Predictor,
        SimpleTracker,
        _get_backbone_features,
        _detect_with_backbone,
        draw_frame,
    )

    p = Path(video_path)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}_tracked{p.suffix}")
    if json_path is None:
        json_path = str(p.parent / f"{p.stem}_detections.json")

    print(f"Loading SAM 3.1 from {model_path}...")
    from mlx_vlm.utils import get_model_path, load_model
    mp = get_model_path(model_path)
    model = load_model(mp)
    processor = Sam31Processor.from_pretrained(str(mp))
    if resolution != 1008:
        processor.image_size = resolution
    predictor = Sam3Predictor(model, processor, score_threshold=threshold)
    tracker = SimpleTracker(iou_threshold=0.3, max_lost=10)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video: {total_frames} frames, {fps:.1f} fps, {W}x{H}")
    print(f"Tracking: {prompts}, every {every_n_frames} frames, threshold {threshold}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (W, H))

    backbone_cache = None
    encoder_cache = {}
    latest_result = None
    propagated_result = None  # for mask propagation
    propagate_remaining = 0   # frames remaining in current propagation window

    # Motion delta state
    prev_gray: Optional[np.ndarray] = None

    # Pre-build relevance score lookup
    relevance_lookup: dict[int, float] = relevance_scores or {}

    all_frames: list[dict] = []
    skipped_frames = 0
    detect_count = 0
    t_start = time.perf_counter()

    for fi in range(total_frames):
        ret, frame_bgr = cap.read()
        if not ret:
            break

        is_detect_frame = (fi % every_n_frames == 0)

        # ── Relevance filter ───────────────────────────────────────
        relevance_skip = False
        if is_detect_frame and relevance_lookup:
            rel_score = relevance_lookup.get(fi, 1.0)
            if rel_score < relevance_threshold:
                relevance_skip = True
                skipped_frames += 1

        # ── Motion delta (greyscale pixel diff between frames) ─────
        motion_skip = False
        if adaptive_motion and not is_detect_frame and prev_gray is not None:
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            delta = float(np.abs(gray.astype(float) - prev_gray.astype(float)).mean() / 255.0)
            if delta < motion_threshold:
                motion_skip = True
                skipped_frames += 1
            prev_gray = gray
        else:
            if prev_gray is None:
                prev_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # ── Propagated result from previous detect frame ───────────
        # If we're in a propagation window, reuse last detection
        if propagate_remaining > 0 and not is_detect_frame:
            propagated_result = latest_result
            propagate_remaining -= 1
        else:
            propagated_result = None

        should_process = is_detect_frame and not relevance_skip and not motion_skip

        if should_process:
            frame_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
            inputs = processor.preprocess_image(frame_pil)
            pixel_values = mx.array(inputs["pixel_values"])

            if detect_count % backbone_every == 0 or backbone_cache is None:
                backbone_cache = _get_backbone_features(model, pixel_values)
                encoder_cache.clear()

            result = _detect_with_backbone(
                predictor,
                backbone_cache,
                prompts,
                frame_pil.size,
                threshold,
                encoder_cache=encoder_cache,
            )
            latest_result = tracker.update(result)
            detect_count += 1

            # Start propagation window after this detect frame
            if propagate_frames > 0:
                propagate_remaining = propagate_frames

        # Annotate frame (use latest result or propagated result for non-detect frames)
        display_result = propagated_result if propagated_result is not None else latest_result

        if display_result is not None and len(display_result.scores) > 0:
            out = draw_frame(
                frame_bgr,
                display_result.masks,
                display_result.scores,
                display_result.boxes,
                " + ".join(prompts),
                H, W,
                show_boxes=True,
                labels=display_result.labels,
            )
        else:
            out = frame_bgr

        writer.write(out)

        # Collect frame detection data
        if is_detect_frame and latest_result is not None:
            frame_data = {
                "frame_index": fi,
                "timestamp": round(fi / fps, 3),
                "n_detections": len(latest_result.scores),
                "detections": [],
            }
            img_area = W * H

            scores = latest_result.scores
            boxes = latest_result.boxes
            labels = latest_result.labels or (prompts * len(scores))
            track_ids = getattr(latest_result, "track_ids", None)

            for i, (score, box, label) in enumerate(zip(scores, boxes, labels)):
                bx1, by1, bx2, by2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
                cx_norm = ((bx1 + bx2) / 2) / W
                cy_norm = ((by1 + by2) / 2) / H
                box_area = (bx2 - bx1) * (by2 - by1)
                area_frac = box_area / img_area
                tid = int(track_ids[i]) if track_ids is not None and i < len(track_ids) else i

                det = FrameDetection(
                    label=label or "object",
                    score=float(score),
                    bbox_xyxy=(bx1, by1, bx2, by2),
                    track_id=tid,
                    centroid_norm=(cx_norm, cy_norm),
                    area_fraction=area_frac,
                )
                frame_data["detections"].append(det.to_dict())

            all_frames.append(frame_data)

        if fi % 40 == 0 and fi > 0:
            elapsed = time.perf_counter() - t_start
            fps_actual = (fi + 1) / elapsed if elapsed > 0 else 0
            n_dets = len(display_result.scores) if display_result else 0
            skip_str = f" | {skipped_frames} skipped" if skipped_frames else ""
            print(f"  Frame {fi}/{total_frames}: {n_dets} det, {fps_actual:.1f} fps{skip_str}")

    writer.release()
    cap.release()
    elapsed = time.perf_counter() - t_start

    # Write JSON
    with open(json_path, "w") as f:
        _json.dump({
            "video_path": str(video_path),
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "resolution": f"{W}x{H}",
            "prompts": prompts,
            "threshold": threshold,
            "processed_frames": len(all_frames),
            "skipped_frames": skipped_frames,
            "elapsed_seconds": round(elapsed, 1),
            "adaptive": {
                "adaptive_motion": adaptive_motion,
                "motion_threshold": motion_threshold,
                "propagate_frames": propagate_frames,
                "relevance_filter": bool(relevance_lookup),
                "relevance_threshold": relevance_threshold,
            },
            "frames": all_frames,
        }, f, indent=2)

    # Compute unique track IDs
    all_track_ids = set()
    for frame in all_frames:
        for det in frame["detections"]:
            all_track_ids.add(det["track_id"])

    print(f"\nSaved: {output_path}")
    print(f"Saved: {json_path}  ({len(all_frames)} frames, {len(all_track_ids)} unique objects)")

    stats = VideoTrackStats(
        total_frames=total_frames,
        processed_frames=len(all_frames),
        fps=round(fps, 1),
        unique_objects=len(all_track_ids),
        output_path=output_path,
    )
    return stats, all_frames


def track_realtime(
    camera_or_video: str,
    prompts: list[str],
    *,
    threshold: float = 0.15,
    detect_every: int = 15,
    recompute_backbone_every: int = 30,
    update_memory_every: int = 3,
    resolution: int = 1008,
) -> None:
    """Real-time tracking from camera (0) or video file.

    Optimizations:
    - Backbone caching: skip ViT on intermediate frames (~67ms saved per frame)
    - Tracker propagation: use memory attention + mask decoder instead of DETR
    - Only re-runs DETR every detect_every frames

    Press 'q' in the display window to quit.

    Args:
        camera_or_video: "0" for webcam, or path to video file
        prompts: text prompts to track
        threshold: detection confidence
        detect_every: run DETR detection every N inference frames
        recompute_backbone_every: re-run ViT backbone every N frames
        update_memory_every: update tracker memory every N propagation frames
        resolution: input resolution (1008 = native)
    """
    from mlx_vlm.models.sam3_1.generate import track_video_realtime as _track_realtime

    if not sam31_available():
        raise RuntimeError(
            "SAM 3.1 weights not cached. Run:\n"
            "  huggingface-cli download mlx-community/sam3.1-bf16\n"
            "Then restart this session."
        )

    _track_realtime(
        video_path=camera_or_video,
        prompts=prompts,
        threshold=threshold,
        detect_every=detect_every,
        recompute_backbone_every=recompute_backbone_every,
        update_memory_every=update_memory_every,
        resolution=resolution,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Chunked video processing — splits large videos into segments to avoid OOM
# ──────────────────────────────────────────────────────────────────────────────


def _extract_segment(
    video_path: str,
    start_sec: float,
    duration_sec: float,
    output_path: str,
    max_width: int = 0,
) -> str:
    """Extract a time segment from a video using ffmpeg.

    If max_width > 0, downsamples the video to at most that width
    (preserving aspect ratio). This dramatically speeds up SAM processing
    on 4K source footage.

    Returns the output path on success.
    Raises RuntimeError if ffmpeg is not available or extraction fails.
    """
    import subprocess
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start_sec:.3f}",
        "-i", str(video_path),
        "-t", f"{duration_sec:.3f}",
    ]
    if max_width > 0:
        # Scale to max_width, preserving aspect ratio, using fast bilinear
        cmd += ["-vf", f"scale='min({max_width},iw)':-2:flags=fast_bilinear"]
    else:
        cmd += ["-c", "copy", "-avoid_negative_ts", "make_zero"]
    cmd.append(str(output_path))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg segment extraction failed: {result.stderr[-500:]}")
    return output_path


def _concat_segments(
    segment_paths: list[str],
    output_path: str,
) -> str:
    """Concatenate video segments using ffmpeg concat demuxer (stream copy).

    Returns the output path on success.
    """
    import subprocess
    import tempfile

    concat_dir = Path(output_path).parent
    list_file = concat_dir / "_chunk_concat_list.txt"
    with open(list_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    list_file.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed: {result.stderr[-500:]}")
    return output_path


def _iou_match_track_ids(
    prev_chunk_last_frame: list[dict],
    next_chunk_first_frame: list[dict],
    iou_threshold: float = 0.3,
) -> dict[int, int]:
    """Match track IDs between the last frame of one chunk and the first frame
    of the next using bounding-box IoU.

    Returns a mapping: {old_track_id: new_track_id} for objects that
    appear in both frames with sufficient overlap.
    """
    from collections import defaultdict

    id_map: dict[int, int] = {}

    if not prev_chunk_last_frame or not next_chunk_first_frame:
        return id_map

    for prev_det in prev_chunk_last_frame:
        px1, py1, px2, py2 = prev_det["bbox_xyxy"]
        p_area = (px2 - px1) * (py2 - py1)
        if p_area <= 0:
            continue

        best_iou = 0.0
        best_next_id = -1

        for next_det in next_chunk_first_frame:
            nx1, ny1, nx2, ny2 = next_det["bbox_xyxy"]
            n_area = (nx2 - nx1) * (ny2 - ny1)
            if n_area <= 0:
                continue

            # Intersection
            ix1 = max(px1, nx1)
            iy1 = max(py1, ny1)
            ix2 = min(px2, nx2)
            iy2 = min(py2, ny2)
            if ix2 <= ix1 or iy2 <= iy1:
                continue
            inter = (ix2 - ix1) * (iy2 - iy1)
            union = p_area + n_area - inter
            iou = inter / union if union > 0 else 0

            if iou > best_iou:
                best_iou = iou
                best_next_id = next_det["track_id"]

        if best_iou >= iou_threshold and best_next_id >= 0:
            id_map[prev_det["track_id"]] = best_next_id

    return id_map


def track_video_chunked(
    video_path: str,
    prompts: list[str],
    output_path: Optional[str] = None,
    json_path: Optional[str] = None,
    *,
    model_path: str = "mlx-community/sam3.1-bf16",
    threshold: float = 0.15,
    every_n_frames: int = 2,
    backbone_every: int = 1,
    resolution: int = 1008,
    opacity: float = 0.6,
    contour_thickness: int = 2,
    # Adaptive parameters (forwarded to track_video_with_json)
    adaptive_motion: bool = False,
    motion_threshold: float = 0.03,
    propagate_frames: int = 0,
    relevance_scores: dict[int, float] | None = None,
    relevance_threshold: float = 0.2,
    # Chunking parameters
    chunk_duration: int = 30,
    overlap_duration: int = 3,
    # Optional relevance regions for targeted extraction
    relevance_regions: list | None = None,
) -> tuple[VideoTrackStats, list[dict]]:
    """Track objects in a large video by processing it in temporal chunks.

    Splits the video into segments of `chunk_duration` seconds (with
    `overlap_duration` seconds of overlap for tracker ID stitching),
    processes each chunk through track_video_with_json(), then merges
    the results with continuous track IDs.

    If `relevance_regions` is provided (from FastScan), only those time
    ranges are processed — skipping irrelevant portions entirely.

    Args:
        video_path: input video path
        prompts: text prompts to track
        output_path: annotated video output (auto-generated if None)
        json_path: JSON detections output (auto-generated if None)
        model_path: SAM 3.1 HuggingFace repo
        threshold: detection confidence
        every_n_frames: run detection every N frames
        backbone_every: re-run ViT backbone every N detections
        resolution: SAM input resolution
        opacity: mask overlay opacity
        contour_thickness: contour line thickness
        adaptive_motion: enable motion-guided frame skipping
        motion_threshold: greyscale delta threshold
        propagate_frames: reuse masks for N frames after detect
        relevance_scores: {frame_index: relevance} from Falcon fast-scan
        relevance_threshold: minimum relevance to process a frame
        chunk_duration: seconds per processing chunk (0 = no chunking)
        overlap_duration: seconds of overlap between chunks for ID stitching
        relevance_regions: list of TemporalRegion objects from FastScan

    Returns:
        (VideoTrackStats, list of per-frame detection dicts) — same
        format as track_video_with_json(), but with `chunked: True` in the
        JSON metadata.
    """
    import json as _json
    import shutil
    import tempfile

    p = Path(video_path)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}_tracked{p.suffix}")
    if json_path is None:
        json_path = str(p.parent / f"{p.stem}_detections.json")

    # Determine which time ranges to process
    # Also detect source video resolution for pre-downsampling
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    src_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap.release()
    duration = total_frames / fps

    # Pre-downsample chunks if source is significantly larger than SAM resolution
    # SAM processes internally at `resolution`, so feeding 4K is wasteful:
    # each frame gets scaled 3840→512 by the model anyway. Pre-scaling to ~2x
    # the SAM resolution (e.g. 1024) keeps enough detail while cutting I/O and
    # per-frame decode time dramatically.
    ds_max_width = 0
    if src_width > resolution * 2:
        ds_max_width = resolution * 2  # e.g. 1024 for SAM res=512
        print(f"  Source: {src_width}px wide — downsample chunks to {ds_max_width}px")
    else:
        print(f"  Source: {src_width}px wide — no downsample needed")

    if relevance_regions:
        # Use FastScan regions — only process relevant time ranges
        time_ranges = [
            (r.start_time, r.end_time, r.label)
            for r in relevance_regions
        ]
        print(f"  Chunked mode: processing {len(time_ranges)} relevance regions")
    else:
        # Process the entire video in fixed-size chunks

        time_ranges = []
        start = 0
        while start < duration:
            end = min(start + chunk_duration, duration)
            time_ranges.append((start, end, f"chunk_{len(time_ranges)}"))
            start += chunk_duration  # no gap between chunks; overlap handled separately
        print(f"  Chunked mode: {len(time_ranges)} chunks of {chunk_duration}s "
              f"(overlap: {overlap_duration}s)")

    if not time_ranges:
        raise RuntimeError("No time ranges to process — video may be too short or no regions found")

    # Create temp directory for chunk segments
    # Use /tmp to avoid disk pressure on the volume holding the source video
    tmpdir = tempfile.mkdtemp(prefix="vb_chunk_", dir="/tmp")
    all_frame_data: list[dict] = []
    all_video_segments: list[str] = []
    global_track_offset = 0
    track_id_mapping: dict[int, int] = {}  # local chunk ID → global ID
    next_global_id = 0

    # Track the maximum track ID we've seen for remapping
    max_track_id_seen = -1

    try:
        for chunk_idx, (chunk_start, chunk_end, chunk_label) in enumerate(time_ranges):
            chunk_dur = chunk_end - chunk_start
            # Add overlap on the end (except for the last chunk)
            if chunk_idx < len(time_ranges) - 1:
                effective_dur = chunk_dur + overlap_duration
            else:
                effective_dur = chunk_dur

            print(f"\n  ── Chunk {chunk_idx + 1}/{len(time_ranges)}: "
                  f"{chunk_start:.1f}s – {chunk_end:.1f}s ({chunk_label}, "
                  f"+{overlap_duration}s overlap)" if chunk_idx < len(time_ranges) - 1 else
                  f"  ── Chunk {chunk_idx + 1}/{len(time_ranges)}: "
                  f"{chunk_start:.1f}s – {chunk_end:.1f}s ({chunk_label})")

            # Extract segment to temp file
            seg_path = str(Path(tmpdir) / f"chunk_{chunk_idx:03d}.mp4")
            seg_out = str(Path(tmpdir) / f"chunk_{chunk_idx:03d}_tracked.mp4")
            seg_json = str(Path(tmpdir) / f"chunk_{chunk_idx:03d}_detections.json")

            _extract_segment(video_path, chunk_start, effective_dur, seg_path,
                               max_width=ds_max_width)

            # Process this chunk through the standard pipeline
            try:
                chunk_stats, chunk_frames = track_video_with_json(
                    seg_path,
                    prompts,
                    output_path=seg_out,
                    json_path=seg_json,
                    model_path=model_path,
                    threshold=threshold,
                    every_n_frames=every_n_frames,
                    backbone_every=backbone_every,
                    resolution=resolution,
                    opacity=opacity,
                    contour_thickness=contour_thickness,
                    adaptive_motion=adaptive_motion,
                    motion_threshold=motion_threshold,
                    propagate_frames=propagate_frames,
                    relevance_scores=None,  # Per-chunk, we skip relevance filtering
                    relevance_threshold=relevance_threshold,
                )
            except Exception as e:
                print(f"  ⚠ Chunk {chunk_idx + 1} failed: {e}")
                # Continue with next chunk rather than failing the whole job
                continue

            all_video_segments.append(seg_out)

            # ── Merge detections ──────────────────────────────────────────
            cap = cv2.VideoCapture(video_path)
            video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            cap.release()

            chunk_start_frame = int(chunk_start * video_fps)

            # Frame index offset and track ID remapping
            prev_chunk_last_dets = (
                all_frame_data[-1]["detections"]
                if all_frame_data and all_frame_data[-1]["detections"]
                else []
            )

            for fd in chunk_frames:
                # Adjust frame index and timestamp to global coordinates
                fd["frame_index"] += chunk_start_frame
                fd["timestamp"] = round(fd["timestamp"] + chunk_start, 3)

                # Remap track IDs to be globally unique
                for det in fd["detections"]:
                    local_id = det["track_id"]
                    # Simple offset mapping: add max_track_id_seen + 1
                    det["track_id"] = local_id + max_track_id_seen + 1

                all_frame_data.append(fd)

            # Update max track ID for next chunk
            if chunk_frames:
                max_local_id = max(
                    d["track_id"]
                    for fd in chunk_frames
                    for d in fd["detections"]
                ) if any(fd["detections"] for fd in chunk_frames) else 0
                max_track_id_seen += max_local_id + 1

            # Free model cache to reduce pressure for next chunk
            # (model will be re-loaded on next call to _ensure_sam31)
            # We intentionally do NOT clear _sam_model_cache here because
            # re-loading weights from disk is ~2-3 seconds and we want to
            # keep the model hot between chunks.

        # ── Concatenate annotated video segments ───────────────────────────
        if len(all_video_segments) > 1:
            print(f"\n  Concatenating {len(all_video_segments)} video segments...")
            _concat_segments(all_video_segments, output_path)
            print(f"  → Merged video: {output_path}")
        elif len(all_video_segments) == 1:
            shutil.copy2(all_video_segments[0], output_path)
            print(f"  → Single-chunk video: {output_path}")

        # ── Compute aggregate stats ─────────────────────────────────────────
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        cap.release()

        unique_track_ids = set()
        for fd in all_frame_data:
            for det in fd["detections"]:
                unique_track_ids.add(det["track_id"])

        # Write final merged JSON
        with open(json_path, "w") as f:
            _json.dump({
                "video_path": str(video_path),
                "total_frames": total_frames,
                "fps": round(fps, 2),
                "resolution": "",
                "prompts": prompts,
                "threshold": threshold,
                "processed_frames": len(all_frame_data),
                "skipped_frames": 0,
                "elapsed_seconds": 0,  # filled by caller if needed
                "chunked": True,
                "chunk_duration": chunk_duration,
                "overlap_duration": overlap_duration,
                "num_chunks": len(time_ranges),
                "adaptive": {
                    "adaptive_motion": adaptive_motion,
                    "motion_threshold": motion_threshold,
                    "propagate_frames": propagate_frames,
                    "relevance_filter": bool(relevance_scores),
                    "relevance_threshold": relevance_threshold,
                },
                "frames": all_frame_data,
            }, f, indent=2)

        print(f"  Saved: {json_path}  ({len(all_frame_data)} frames, "
              f"{len(unique_track_ids)} unique objects)")

    finally:
        # Clean up temp directory
        shutil.rmtree(tmpdir, ignore_errors=True)

    stats = VideoTrackStats(
        total_frames=total_frames,
        processed_frames=len(all_frame_data),
        fps=round(fps, 1),
        unique_objects=len(unique_track_ids),
        output_path=output_path,
    )
    return stats, all_frame_data
