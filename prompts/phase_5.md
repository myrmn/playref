# PHASE 5: Video analysis (experimental)

Precondition: Phase 4 approved by me. Set `docs/PROGRESS.md`: Phase 5 = IN PROGRESS. Re-read `AGENTS.md`, `docs/PROGRESS.md`, and the Phase 4 vision report.

## Goal
Short clip upload -> sampled frames -> per-frame observations -> timeline -> same RAG pipeline, with progress streaming.

## Principles
Same as Phase 4: describe, do not judge; experimental label; clarifying questions; no definitive verdicts. A video has a time dimension, so the timeline should describe what happened before/at/after the key moment, but still avoid claims about intent or contact intensity.

## Tasks
1. **Upload** `POST /media/videos`: mp4/mov/webm, max 20 MB, max `MAX_VIDEO_SECONDS` (15). Validate with `ffprobe` (duration, codec, streams), reject corrupt/oversize, re-encode/strip metadata, store in MinIO. Optional field `key_moment_seconds`.
2. **Frame sampling** `app/media/frames.py`: ffmpeg at 2 fps, scale 768px width, max 12 frames. If `key_moment_seconds` is given, sample densely around it (e.g. +/- 2 s at 4 fps) and sparsely elsewhere. Optional scene-change detection to avoid redundant frames. Include the timestamp for each frame.
3. **Per-frame observation**: reuse Phase 4 observer (parallel with bounded concurrency). Use the model chosen in the Phase 4 go/no-go.
4. **Timeline merge** `app/media/timeline.py`: combine frame observations into an ordered timeline (`t=3.5s: ...`), detect changes (ball contact appears, player enters box), carry uncertainty forward. Optionally use Qwen3.6-27B with the key frames + timeline to write a neutral scenario summary.
5. **Background jobs**: RQ (Redis) or Celery worker; `POST /media/videos` returns `job_id`; `GET /jobs/{id}` and an SSE channel emit progress: `uploading -> extracting_frames -> analyzing_frames (n/N) -> checking_laws -> done|failed`.
6. **Chat integration**: `POST /chat` accepts `video_job_id` or `media_ids`; the answer includes the timeline under "What I saw" and the experimental flag.
7. **Frontend**: video upload with preview, optional "key moment" slider/timestamp input, progress stepper, timeline view, error/retry states.
8. **Cleanup**: delete temp frames/files after processing, retention for stored videos, worker crash handling, job timeouts.
9. **Tests**: ffprobe validation, frame count/timestamps, timeline merge on fixture data, job lifecycle with mocked models, limits enforced. Provide 5 sample clips test run (I will supply clips; until then use a generated test clip with ffmpeg testsrc).
10. Note in the report: no audio/commentary processing exists (no ASR API available); list options if I want it later.

## Out of scope
Offside geometry, live streams, audio transcription.

## Acceptance criteria
See Phase 5 in `docs/ROADMAP.md`. Show: successful run end-to-end with progress events, a rejected oversize clip, a cleanup verification.

## When done
Phase Report, update `docs/PROGRESS.md` to AWAITING APPROVAL, STOP and ask:
"Phase 5 is complete. Approve moving to Phase 6? (reply "approved" or list changes)"
