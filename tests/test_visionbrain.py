"""Pytest suite for VisionBrain.

Run with:
    python -m pytest tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure visionbrain is importable
VBRAIN = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(VBRAIN))

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Loader tests (no MLX required)
# ──────────────────────────────────────────────────────────────────────────────

class TestLoader:
    def test_check_mlx_handles_runtime_error(self, monkeypatch):
        import builtins
        from visionbrain import loader

        original_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name.startswith("mlx"):
                raise RuntimeError("[metal::load_device] No Metal device available")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        assert loader._check_mlx() is False

    def test_falcon_perception_record(self):
        from visionbrain.loader import falcon_perception_record, HF_CACHE
        rec = falcon_perception_record()
        assert rec.hf_id == "tiiuae/Falcon-Perception"
        assert rec.cache_dir == HF_CACHE / "models--tiiuae--Falcon-Perception"
        assert rec.is_cached, f"Falcon Perception weights should be cached at {rec.cache_dir}"
        # can_load depends on mlx_vlm availability in this Python env
        print(f"\n  Falcon Perception: cached={rec.is_cached} ({rec.disk_gb} GB), can_load={rec.can_load}, note={rec.note}")

    def test_sam31_record(self):
        from visionbrain.loader import sam31_record, HF_CACHE
        rec = sam31_record()
        assert rec.hf_id == "mlx-community/sam3.1-bf16"
        assert rec.cache_dir == HF_CACHE / "models--mlx-community--sam3.1-bf16"
        # is_cached=True only if >0.5 GB downloaded
        print(f"\n  SAM 3.1: cached={rec.is_cached} ({rec.disk_gb} GB), can_load={rec.can_load}, note={rec.note}")

    def test_falcon_repo_accessible(self):
        from visionbrain.loader import falcon_repo
        rec = falcon_repo()
        assert rec.exists(), f"Falcon-Perception repo should exist at {rec}"
        assert (rec / "falcon_perception").exists()

    def test_status_printer(self):
        from visionbrain.loader import print_status
        # Just verify it doesn't crash
        print_status()


# ──────────────────────────────────────────────────────────────────────────────
# Falcon Perception tests (requires mlx + cached weights)
# ──────────────────────────────────────────────────────────────────────────────

class TestFalconPerception:
    @pytest.fixture
    def test_image(self):
        from PIL import Image
        path = Path.home() / "Falcon-Perception" / "test_results" / "friends_people.jpg"
        if not path.exists():
            pytest.skip(f"Test image not found: {path}")
        return Image.open(path)

    def test_segment(self, test_image):
        from visionbrain.fp_inference import segment
        from visionbrain.loader import falcon_perception_record

        rec = falcon_perception_record()
        if not rec.can_load:
            pytest.skip(f"Falcon Perception not ready: {rec.note}")

        masks, stats = segment(test_image, "person", max_new_tokens=200)
        assert isinstance(masks, list)
        assert stats.total_ms > 0
        print(f"\n  Segment 'person': {len(masks)} masks in {stats.total_ms:.0f}ms")
        if masks:
            assert masks[0].mask_id == 1
            assert 0 <= masks[0].centroid_x <= 1
            assert 0 <= masks[0].centroid_y <= 1

    def test_detect(self, test_image):
        from visionbrain.fp_inference import detect
        from visionbrain.loader import falcon_perception_record

        rec = falcon_perception_record()
        if not rec.can_load:
            pytest.skip(f"Falcon Perception not ready: {rec.note}")

        detections, stats = detect(test_image, "person", max_new_tokens=200)
        assert isinstance(detections, list)
        assert stats.total_ms > 0
        print(f"\n  Detect 'person': {len(detections)} detections in {stats.total_ms:.0f}ms")
        if detections:
            assert 0 <= detections[0].cx <= 1
            assert 0 <= detections[0].cy <= 1

    def test_attribute_expression(self):
        from visionbrain.fp_inference import detect
        from visionbrain.loader import falcon_perception_record
        from PIL import Image
        import numpy as np

        rec = falcon_perception_record()
        if not rec.can_load:
            pytest.skip(f"Falcon Perception not ready: {rec.note}")

        # Create a synthetic test image with a simple shape
        img = Image.fromarray(
            np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        )
        detections, stats = detect(img, "red object", max_new_tokens=200)
        print(f"\n  Attribute 'red object': {len(detections)} detections in {stats.total_ms:.0f}ms")
        # Don't assert on count — synthetic image, just verify it runs

    def test_ocr(self):
        from visionbrain.fp_inference import ocr
        from visionbrain.loader import falcon_perception_record
        from PIL import Image

        rec = falcon_perception_record()
        if not rec.can_load:
            pytest.skip(f"Falcon Perception not ready: {rec.note}")

        path = Path.home() / "Falcon-Perception" / "test_results" / "vis_all_people_0.jpg"
        if not path.exists():
            pytest.skip("OCR test image not found")
        img = Image.open(path)
        detections, text, stats = ocr(img, "read all text", max_new_tokens=500)
        assert isinstance(text, str)
        print(f"\n  OCR: {len(detections)} text regions, {len(text)} chars markup, {stats.total_ms:.0f}ms")


# ──────────────────────────────────────────────────────────────────────────────
# Agent tools tests (no torch)
# ──────────────────────────────────────────────────────────────────────────────

class TestAgentTools:
    def test_masks_to_vlm_json(self):
        from visionbrain.agent_tools import masks_to_vlm_json

        masks = {
            1: {
                "id": 1,
                "area_fraction": 0.05,
                "centroid_norm": {"x": 0.5, "y": 0.5},
                "bbox_norm": {"x1": 0.4, "y1": 0.4, "x2": 0.6, "y2": 0.6},
                "image_region": "center",
                "rle": {"size": [100, 100], "counts": "..."},
            }
        }
        out = masks_to_vlm_json(masks)
        assert isinstance(out, list)
        assert out[0]["id"] == 1
        assert "rle" not in out[0]  # RLE should be stripped

    def test_compute_relations(self):
        from visionbrain.agent_tools import compute_relations
        from pycocotools import mask as mask_utils
        import numpy as np

        # Two overlapping masks
        arr1 = np.zeros((100, 100), dtype=np.uint8)
        arr1[20:60, 20:60] = 1
        arr2 = np.zeros((100, 100), dtype=np.uint8)
        arr2[40:80, 40:80] = 1

        rle1 = mask_utils.encode(np.asfortranarray(arr1))
        rle2 = mask_utils.encode(np.asfortranarray(arr2))

        def str_rle(r):
            out = dict(r)
            out["counts"] = out["counts"].decode("utf-8")
            return out

        masks = {
            1: {"id": 1, "area_fraction": 0.16, "centroid_norm": {"x": 0.4, "y": 0.4},
                "bbox_norm": {"x1": 0.2, "y1": 0.2, "x2": 0.6, "y2": 0.6},
                "image_region": "center-left", "rle": str_rle(rle1)},
            2: {"id": 2, "area_fraction": 0.16, "centroid_norm": {"x": 0.6, "y": 0.6},
                "bbox_norm": {"x1": 0.4, "y1": 0.4, "x2": 0.8, "y2": 0.8},
                "image_region": "center-right", "rle": str_rle(rle2)},
        }

        result = compute_relations(masks, [1, 2])
        assert "pairs" in result
        assert "1_vs_2" in result["pairs"]
        pair = result["pairs"]["1_vs_2"]
        assert "iou" in pair
        assert pair["1_left_of_2"] is True
        assert pair["1_above_2"] is True


# ──────────────────────────────────────────────────────────────────────────────
# Viz tests
# ──────────────────────────────────────────────────────────────────────────────

class TestViz:
    @pytest.fixture
    def sample_mask(self):
        from visionbrain.fp_inference import MaskResult
        from pycocotools import mask as mask_utils
        import numpy as np

        arr = np.zeros((100, 100), dtype=np.uint8)
        arr[20:60, 20:60] = 1
        rle = mask_utils.encode(np.asfortranarray(arr))
        rle_str = dict(rle)
        rle_str["counts"] = rle_str["counts"].decode("utf-8")

        return MaskResult(
            mask_id=1,
            centroid_x=0.4,
            centroid_y=0.4,
            bbox_x1=0.2,
            bbox_y1=0.2,
            bbox_x2=0.6,
            bbox_y2=0.6,
            area_fraction=0.16,
            image_region="center-left",
            rle=rle_str,
        )

    @pytest.fixture
    def sample_image(self):
        from PIL import Image
        import numpy as np
        return Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))

    def test_render_som(self, sample_image, sample_mask):
        from visionbrain.viz import render_som
        out = render_som(sample_image, [sample_mask])
        assert out.size == sample_image.size

    def test_render_detections(self, sample_image):
        from visionbrain.fp_inference import DetectionResult
        from visionbrain.viz import render_detections
        det = DetectionResult(
            label="cow", score=0.95,
            cx=0.5, cy=0.5, h=0.3, w=0.4,
        )
        out = render_detections(sample_image, [det])
        assert out.size == sample_image.size

    def test_get_crop(self, sample_image, sample_mask):
        from visionbrain.viz import get_crop
        crop = get_crop(sample_image, sample_mask, pad=0.1)
        assert crop.width < sample_image.width
        assert crop.height < sample_image.height

    def test_compute_relations_viz(self, sample_mask):
        from visionbrain.viz import compute_relations
        # Need at least 2 masks — create a second one
        from visionbrain.fp_inference import MaskResult
        from pycocotools import mask as mask_utils
        import numpy as np

        arr2 = np.zeros((100, 100), dtype=np.uint8)
        arr2[60:90, 60:90] = 1
        rle2 = mask_utils.encode(np.asfortranarray(arr2))
        rle2_str = dict(rle2)
        rle2_str["counts"] = rle2_str["counts"].decode("utf-8")

        mask2 = MaskResult(
            mask_id=2,
            centroid_x=0.75,
            centroid_y=0.75,
            bbox_x1=0.6,
            bbox_y1=0.6,
            bbox_x2=0.9,
            bbox_y2=0.9,
            area_fraction=0.09,
            image_region="bottom-right",
            rle=rle2_str,
        )
        result = compute_relations([sample_mask, mask2])
        assert "pairs" in result
        assert result["pairs"]["1_vs_2"]["1_left_of_2"] is True
        assert result["pairs"]["1_vs_2"]["1_above_2"] is True


class TestReviewOutputs:
    def test_display_result_does_not_reuse_latest_without_propagation(self):
        from visionbrain.sam3_inference import _display_result_for_frame

        latest = object()
        assert _display_result_for_frame(
            should_process=False,
            latest_result=latest,
            propagated_result=None,
        ) is None
        assert _display_result_for_frame(
            should_process=False,
            latest_result=latest,
            propagated_result="propagated",
        ) == "propagated"
        assert _display_result_for_frame(
            should_process=True,
            latest_result=latest,
            propagated_result=None,
        ) is latest

    def test_review_reel_duration_matches_analyzed_frames(self, tmp_path):
        import cv2
        import numpy as np
        from visionbrain.sam3_inference import render_review_outputs

        video_path = tmp_path / "source.mp4"
        fps = 5.0
        writer = cv2.VideoWriter(
            str(video_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (64, 48),
        )
        for i in range(6):
            frame = np.full((48, 64, 3), i * 30, dtype=np.uint8)
            writer.write(frame)
        writer.release()

        frame_data = [
            {
                "frame_index": 1,
                "timestamp": 0.2,
                "n_detections": 1,
                "detections": [{
                    "label": "roof",
                    "score": 0.9,
                    "track_id": 3,
                    "bbox_xyxy": [10, 10, 30, 30],
                }],
            },
            {
                "frame_index": 4,
                "timestamp": 0.8,
                "n_detections": 0,
                "detections": [],
            },
        ]
        reel_path = tmp_path / "review.mp4"
        still_dir = tmp_path / "stills"

        result = render_review_outputs(
            str(video_path),
            frame_data,
            review_reel_path=str(reel_path),
            hold_seconds=0.4,
            still_dir=str(still_dir),
            prompts=["roof damage"],
        )

        cap = cv2.VideoCapture(str(reel_path))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        assert result["video_frames_written"] == 4
        assert frame_count == 4
        assert len(list(still_dir.glob("*.jpg"))) == 2


# ──────────────────────────────────────────────────────────────────────────────
# CLI smoke tests
# ──────────────────────────────────────────────────────────────────────────────

class TestCLI:
    def test_status_command(self):
        import subprocess
        import sys
        # Run as module so relative imports resolve
        result = subprocess.run(
            [sys.executable, "-m", "visionbrain", "status"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent / "src"),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "VisionBrain Model Status" in result.stdout

    def test_detect_help(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "visionbrain", "detect", "--help"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent / "src"),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "--image" in result.stdout

    def test_sam3_help(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "visionbrain", "sam3", "--help"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent / "src"),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "--image" in result.stdout
        assert "--prompts" in result.stdout

    def test_analyze_help_review_outputs(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "visionbrain", "analyze", "--help"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent / "src"),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "--review-reel-output" in result.stdout
        assert "--hold-seconds" in result.stdout
        assert "--still-dir" in result.stdout


class TestWebApp:
    def test_job_result_json_endpoints(self, tmp_path):
        from fastapi.testclient import TestClient
        from visionbrain import web_app

        det = tmp_path / "detections.json"
        det.write_text('{"processed_frames": 1, "frames": []}')
        report = tmp_path / "report.txt"
        report.write_text("Roof repair candidates: none visible.")
        fast = tmp_path / "fast.json"
        fast.write_text('{"quick_answer": "No roof damage detected.", "regions": []}')

        jid = "testjob123"
        web_app._jobs[jid] = {
            "id": jid,
            "kind": "analyze",
            "status": "done",
            "results": {
                "json": str(det),
                "report": str(report),
                "fast_json": str(fast),
            },
            "output": [],
            "error": None,
        }

        client = TestClient(web_app.app)
        assert client.get(f"/api/job/{jid}/detections").json()["processed_frames"] == 1
        assert "Roof repair" in client.get(f"/api/job/{jid}/report").json()["text"]
        assert client.get(f"/api/job/{jid}/fast").json()["quick_answer"].startswith("No roof")

        web_app._jobs.pop(jid, None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
