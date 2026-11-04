# PHASE 4: Image upload (experimental)

Precondition: Phase 3 approved by me. Set `docs/PROGRESS.md`: Phase 4 = IN PROGRESS. Re-read `AGENTS.md`, `docs/PROJECT_SPEC.md` (Media analysis principle), `docs/PROGRESS.md`.

## Goal
Users upload a football incident image; the system extracts **neutral visual observations** and feeds them into the existing RAG pipeline. Vision models describe; they never judge.

## Non-negotiable principles
- The VLM prompt must say: "Describe only what is visible. Do not judge fouls, offside, or intent. If unsure, answer 'unclear'."
- Final answers from media must (a) be labeled experimental, (b) list what was observed vs. assumed, (c) ask a clarifying question when observations are uncertain, (d) never present a definitive verdict.

## Tasks
1. **Upload endpoint** `POST /media/images`: accept jpg/png/webp, max `MAX_UPLOAD_MB`, validate real MIME (magic bytes, not extension), re-encode with Pillow (strips EXIF/GPS), resize to max 1280px, store in MinIO with random key, return `media_id`. Add MinIO to docker-compose. Add a retention job (delete after N hours, configurable).
2. **Vision client** `app/llm/vision.py`: send image per the verified format in `API_CONTRACTS.md` (smoke test it first, including multi-image if supported).
3. **Observation extraction** `app/media/observe.py`: Gemma-3-4B-IT with forced JSON:
   ```json
   {"location":"penalty_area|midfield|attacking_third|defensive_third|touchline|unclear",
    "ball_visible":true,"ball_contact":"yes|no|unclear",
    "arm_position":"away_from_body|close_to_body|unclear|not_applicable",
    "players_involved":"free text","contact_between_players":"free text|none_visible|unclear",
    "overlay_text":"OCR text of scoreboard/VAR lines or null",
    "uncertainty":["list of things that cannot be determined"],
    "confidence":"low|medium|high"}
   ```
   Pydantic validation, retry on malformed output, enum normalization.
4. **Escalation**: if confidence is low or the user asks a complex question, optionally call Qwen3.6-27B with the image + observations to produce a neutral factual scenario paragraph. Make this configurable and log which path was used.
5. **Pipeline integration**: router intent `media` -> observe -> build `scenario_text = user_text + "Observed: ..." + "Uncertain: ..."` -> existing rewrite/retrieve/rerank/generate. The generator prompt receives an `experimental_media=true` flag that enforces the principles above and forces `assumptions` + clarifying question when `uncertainty` is non-empty.
6. **API**: `POST /chat` accepts `media_ids[]`; response includes `experimental: true` and the `observations` object so the UI can display "What I saw".
7. **Frontend**: enable the upload button, drag-and-drop + paste, preview thumbnail, "Experimental" badge, a "What I saw" collapsible section, error states (too large, wrong type, analysis failed).
8. **Vision test set**: `eval/vision/` with 30-50 images. I will supply images; until then create the harness and a manifest format (`image, expected_observations, notes`). Report per-field accuracy for Gemma-3-4B vs Qwen3.6-27B, hallucination examples, latency. Give me a **go/no-go recommendation** on which model to default to.
9. **Safety/hygiene**: rate limit uploads, reject animated/huge/corrupt files, no filenames from users in storage keys, no logging of image bytes.
10. Tests: MIME spoofing rejected, EXIF stripped, observation parsing/retry, "no definitive verdict" check via a prompt test, clarifying question triggered on uncertainty.

## Out of scope
Video, offside geometry, any model training.

## Acceptance criteria
See Phase 4 in `docs/ROADMAP.md`. Demo with 3 images: clear handball-like situation, ambiguous situation (must ask a clarifying question), unrelated image (must refuse politely).

## When done
Phase Report (include the vision quality report and recommendation), update `docs/PROGRESS.md` to AWAITING APPROVAL, STOP and ask:
"Phase 4 is complete. Approve moving to Phase 5? (reply "approved" or list changes)"
