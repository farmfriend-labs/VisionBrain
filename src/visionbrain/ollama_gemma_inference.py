"""Ollama Gemma 4 inference — reasoning layer for VisionBrain via Ollama.

Model:  gemma4:e2b (7.2 GB) via Ollama localhost:11434
Role:   reasoning on top of SAM 3.1 + Falcon Perception outputs.
        Given structured detections/masks, answers questions and
        generates field reports — the "brain" layer.

Why Ollama: The 26B Gemma requires ~32GB RAM; this Mac Mini has 16GB.
            gemma4:e2b at 7.2GB fits comfortably via Ollama.

Usage:
    from visionbrain.ollama_gemma_inference import ask, generate_report, gemma_available
    resp = ask("Which cattle are isolated from the herd?", detections=frame_data)
    report = generate_report(summary_text, report_type="field")

Note: Ollama gemma4:e2b requires max_tokens >= 200 for structured reasoning
      responses. Lower limits cause the output to be truncated before the
      visible text is generated (Gemma's generation is slow relative to its
      context fill; the model hits max_tokens before producing visible output).
"""

from __future__ import annotations

import time
import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_ENDPOINT = "http://localhost:11434/v1/chat/completions"
DEFAULT_MODEL = "gemma4:e2b"

# Stop sequences prevent Gemma's chat template from generating multiple turns.
# Without these, gemma4:e2b sometimes produces a second <end_of_turn> block
# before returning, resulting in empty visible output.
STOP_TOKENS = ["<end_of_turn>", "<eos>"]

SYSTEM_PROMPT = (
    "You are an agricultural intelligence assistant helping farmers and ranchers "
    "analyze drone and camera footage. You have access to structured object detection "
    "data from vision AI models: bounding boxes with confidence scores, pixel-level "
    "segmentation masks with area fractions, object tracks across video frames "
    "(track IDs, centroid positions), and class labels (e.g. 'cow', 'sheep', 'fence', "
    "'crop row'). "
    "Be specific, practical, and actionable. Focus on: animal health and behavior "
    "(injuries, isolation, unusual movement), infrastructure (fence damage, water "
    "trough availability), crop stress indicators, and anomalies requiring human "
    "attention. Keep reports concise but detailed enough to act on in the field."
)

# ──────────────────────────────────────────────────────────────────────────────
# Result types (compatible with existing GemmaResponse/GemmaStats interfaces)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class GemmaStats:
    prompt_tokens: int
    generation_tokens: int
    prompt_tps: float
    generation_tps: float
    decode_ms: float


@dataclass
class GemmaResponse:
    text: str
    stats: GemmaStats


# ──────────────────────────────────────────────────────────────────────────────
# Availability
# ──────────────────────────────────────────────────────────────────────────────

def gemma_available() -> bool:
    """True if Ollama server is reachable and gemma4:e2b is listed."""
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            headers={"Content-Type": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            names = [m.get("name", "") for m in data.get("models", [])]
            return DEFAULT_MODEL in names or "gemma4:latest" in names
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _serialize_detections(detections: list[dict]) -> str:
    """Compact one-line-per-detection format.

    Uses comma-separated "name(conf,centroid)" syntax — gemma4:e2b produces
    empty output when the pipe character "|" appears alongside 2+ detection
    objects, and truncates output when token budget is exhausted.

    For 3+ detections the model runs out of generation budget before
    producing complete visible output at 300 max_tokens; use 512+ for
    queries expected to produce long answers.
    """
    if not detections:
        return "No detections available."
    parts = []
    for d in detections:
        label = d.get("label", "?")
        score = d.get("score", 0)
        track_id = d.get("track_id", d.get("id", "?"))
        cx = d.get("centroid_norm", {}).get("x", 0)
        cy = d.get("centroid_norm", {}).get("y", 0)
        parts.append(f"{track_id}/{label}/{score:.2f}/({cx:.2f},{cy:.2f})")
    return "[" + "], [".join(parts) + "]"


def _serialize_frame_history(frames: list[dict]) -> str:
    if not frames:
        return "No frame history."
    lines = []
    for frame in frames:
        frame_id = frame.get("frame_index", "?")
        ts = frame.get("timestamp", "?")
        dets = frame.get("detections", [])
        if not dets:
            lines.append(f"Frame {frame_id} (t={ts}s): no detections")
            continue
        # Use slash "/" to avoid pipe character issue with gemma4:e2b
        obj_parts = []
        for d in dets:
            label = d.get("label", "?")
            track_id = d.get("track_id", d.get("id", "?"))
            cx = d.get("centroid_norm", {}).get("x", 0)
            cy = d.get("centroid_norm", {}).get("y", 0)
            obj_parts.append(f"{track_id}/{label}/({cx:.2f},{cy:.2f})")
        lines.append(f"Frame {frame_id} (t={ts}s): [{', '.join(obj_parts)}]")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def ask(
    question: str,
    *,
    detections: Optional[list[dict]] = None,
    frame_history: Optional[list[dict]] = None,
    image_path: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
    endpoint: str = DEFAULT_ENDPOINT,
    model: str = DEFAULT_MODEL,
) -> GemmaResponse:
    """Ask a question about structured detection data via Ollama gemma4:e2b.

    Args:
        question: Natural-language question about the detections or footage.
        detections: List of detection dicts from SAM 3.1 or Falcon Perception.
                    Expected fields: label, score, centroid_norm {x,y},
                    area_fraction, track_id/id.
        frame_history: For tracking — list of frames with detections,
                      each having frame_index, timestamp, detections.
        image_path: Not yet supported — include as text description instead.
        max_tokens: Max output tokens. Must be >= 200 for structured responses.
        temperature: Sampling temperature.
        endpoint: Ollama OpenAI-compatible API endpoint.
        model: Model ID (default: gemma4:e2b).

    Returns:
        GemmaResponse with answer text and timing stats.

    Note:
        gemma4:e2b via Ollama produces empty output if max_tokens is too low
        relative to the prompt length. Use max_tokens >= 200 for best results.
    """
    sections = []
    if detections:
        sections.append(f"## Detections\n{_serialize_detections(detections)}")
    if frame_history:
        sections.append(f"## Frame tracking data\n{_serialize_frame_history(frame_history)}")
    if image_path:
        sections.append(f"## Image\n(image at {image_path} — describe if useful)")
    sections.append(f"## Question\n{question}")
    prompt_text = "\n\n".join(sections)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt_text},
    ]

    t0 = time.perf_counter()
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stop": STOP_TOKENS,
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to connect to Ollama at {endpoint}: {e}") from e

    decode_ms = (time.perf_counter() - t0) * 1000
    usage = result.get("usage", {})
    choice = result.get("choices", [{}])[0]
    message = choice.get("message", {})
    text = message.get("content", "")

    return GemmaResponse(
        text=text,
        stats=GemmaStats(
            prompt_tokens=usage.get("prompt_tokens", 0),
            generation_tokens=usage.get("completion_tokens", 0),
            prompt_tps=round(usage.get("prompt_tokens", 0) / (decode_ms / 1000), 1)
                       if decode_ms > 0 else 0.0,
            generation_tps=round(usage.get("completion_tokens", 0) / (decode_ms / 1000), 1)
                          if decode_ms > 0 else 0.0,
            decode_ms=round(decode_ms, 1),
        ),
    )


def generate_report(
    summary_text: str,
    *,
    report_type: str = "field",
    max_tokens: int = 768,
    temperature: float = 0.7,
    endpoint: str = DEFAULT_ENDPOINT,
    model: str = DEFAULT_MODEL,
) -> GemmaResponse:
    """Generate a written field report via Ollama gemma4:e2b.

    Args:
        summary_text: Structured or free-text description of analysis results.
        report_type: "field" (detailed actionable report), "brief" (one paragraph),
                     or "json" (structured JSON).
        max_tokens: Max output tokens. Must be >= 200 for structured responses.
        temperature: Sampling temperature.
        endpoint: Ollama OpenAI-compatible API endpoint.
        model: Model ID (default: gemma4:e2b).

    Returns:
        GemmaResponse with report text and timing stats.
    """
    styles = {
        "field": (
            "Write a detailed field report a rancher or farmer can act on. "
            "Include: overview, key findings, animals/areas of concern with severity, "
            "and recommended actions. Be specific about locations, counts, and urgency."
        ),
        "brief": (
            "Write a one-paragraph summary suitable for a text message or phone call "
            "to the farm manager. Include the most critical finding."
        ),
        "json": (
            "Write a structured JSON report with fields: overview (string), "
            "findings (list of {severity: string, description: string, location: string}), "
            "and actions (list of string). Output ONLY the JSON, no markdown."
        ),
    }
    style = styles.get(report_type, styles["field"])

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"## Analysis summary\n{summary_text}\n\n## Task\n{style}"},
    ]

    t0 = time.perf_counter()
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stop": STOP_TOKENS,
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to connect to Ollama at {endpoint}: {e}") from e

    decode_ms = (time.perf_counter() - t0) * 1000
    usage = result.get("usage", {})
    choice = result.get("choices", [{}])[0]
    message = choice.get("message", {})
    text = message.get("content", "")

    return GemmaResponse(
        text=text,
        stats=GemmaStats(
            prompt_tokens=usage.get("prompt_tokens", 0),
            generation_tokens=usage.get("completion_tokens", 0),
            prompt_tps=round(usage.get("prompt_tokens", 0) / (decode_ms / 1000), 1)
                       if decode_ms > 0 else 0.0,
            generation_tps=round(usage.get("completion_tokens", 0) / (decode_ms / 1000), 1)
                          if decode_ms > 0 else 0.0,
            decode_ms=round(decode_ms, 1),
        ),
    )


def unload_gemma() -> None:
    """No-op for Ollama — no local model to unload. Kept for API compatibility."""
    pass


def test_connection() -> dict:
    """Smoke test Ollama + gemma4:e2b. Returns status dict."""
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            headers={"Content-Type": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            names = [m.get("name", "") for m in data.get("models", [])]
            has_gemma = DEFAULT_MODEL in names or "gemma4:latest" in names
            return {"status": "connected", "ollama_models": names, "gemma_ready": has_gemma}
    except Exception as e:
        return {"status": "error", "message": str(e)}
