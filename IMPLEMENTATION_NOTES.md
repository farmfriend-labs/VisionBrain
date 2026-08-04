# Implementation Notes — Tier 2 Run-State Feedback

## Purpose
Track implementation decisions, tradeoffs, and deviations while adding robust visual liveness feedback.

## Running Notes
- Started Tier 2 implementation on 2026-05-19.
- Chosen notes format: Markdown (`IMPLEMENTATION_NOTES.md`) at repo root for easy diff/review.

## Decisions Made During Implementation
- Added `GET /api/healthz` for app-level liveness separate from model readiness.
- Job schema now tracks timing fields: `started_at`, `ended_at`, `last_heartbeat_at`, `last_output_at`, `phase`.
- Heartbeat cadence set to ~1s in backend execution loop and SSE stream.
- UI stale thresholds chosen as:
  - `<=3s`: running
  - `>3s and <=10s`: quiet/stale-warning
  - `>10s`: no-heartbeat error

## Tradeoffs
- Used `readline()` timeout polling for heartbeats instead of a separate heartbeat task to keep job execution flow simple and avoid extra task lifecycle complexity.
- Added heartbeat SSE messages even without logs to make long quiet model phases visibly alive.
- Reused header status region with a compact mission pill instead of adding a large new panel to reduce layout disruption.

## Behavior Changes
- Job creation endpoints now return `created_at` in addition to `job_id`.
- UI now polls `/api/healthz` every 5s for app running signal when no mission is active.
- SSE stream now emits `{type: "heartbeat", ...}` once per second while active.

## Notes for Review
- `last_heartbeat_at` is process-liveness, not model-internal progress.
- Quiet model steps now remain visibly "running" as long as the subprocess is alive.

## Verification Notes
- Backend Python syntax check passed for `src/visionbrain/web_app.py` via `python3 -m py_compile`.
- Local model runtime verification in this sandbox is blocked by missing Metal device access (`RuntimeError: [metal::load_device] No Metal device available`).
- Remote Gemma probe returned `Operation not permitted` on outbound URL open in this sandbox, so remote availability cannot be confirmed from this environment.
