# PlayRef Roadmap

Phases are sequential. Each ends with a Phase Gate (see AGENTS.md). Do not start a phase until the user approves the previous one.

## Phase 1: Core RAG (CLI)
**Goal:** PDF -> chunks -> embeddings -> Qdrant -> query -> rerank -> grounded answer with citations.
Deliverables: repo scaffold, docker-compose (Qdrant, Postgres), config, LLM client module, API smoke test, ingestion pipeline, retrieval + rerank, generation with citations, CLI `ask_cli.py`, unit tests, mini eval (20 questions).
Acceptance:
- [ ] `docker compose up -d` starts Qdrant + Postgres
- [ ] `python scripts/smoke_apis.py` verifies every model endpoint
- [ ] `python scripts/ingest.py` indexes the Laws PDF with correct metadata (law number, section path, page, edition)
- [ ] Spot check: 10 random chunks inspected and shown to user
- [ ] CLI answers with citations to real chunks
- [ ] Mini eval: recall@6 reported
- [ ] Tests pass, ruff clean

## Phase 2: Production pipeline + API + eval
**Goal:** Router, rewrite, multilingual, history, streaming API, structured output, evaluation.
Deliverables: router (intent+language), query rewrite with history, structured JSON answers, citation validator, FastAPI `/chat` (SSE) + `/health`, Postgres persistence (conversations, messages, feedback), Redis rate limit, hand-written situation->law Q&A layer, golden eval set (100+) and runner with metrics.
Acceptance:
- [ ] Arabic, French, English questions answered in the same language
- [ ] Follow-ups work ("what if it was outside the box?")
- [ ] Off-topic politely redirected
- [ ] Invalid citations are stripped and logged (tested)
- [ ] Eval report: recall@6, citation accuracy, faithfulness, abstention
- [ ] SSE streaming works end-to-end (curl demo)

## Phase 3: Web UI
**Goal:** Next.js chat app.
Deliverables: chat panel with streaming, citation chips + drawer, interpretations accordion, suggested prompts, language toggle with RTL, feedback buttons, Law browser, responsive/mobile layout, disclaimer footer.
Acceptance:
- [ ] Full chat flow in browser against the real backend
- [ ] Citation drawer shows exact chunk text + page
- [ ] RTL layout correct in Arabic
- [ ] Lighthouse/a11y basics acceptable

## Phase 4: Image upload (experimental)
**Goal:** Image -> observations -> RAG.
Deliverables: upload endpoint (MIME/size validation, Pillow re-encode, EXIF strip), MinIO storage with retention, Gemma-3-4B observation extraction (forced JSON, "unclear" allowed), merge with user text, optional escalation to Qwen3.6-27B, clarifying-question behavior, "Experimental" labeling in API + UI, vision test set of 30-50 screenshots with a quality report.
Acceptance:
- [ ] Observation JSON validated by Pydantic; malformed output retried
- [ ] Bot never states a definitive verdict from an image
- [ ] Uncertainty leads to a clarifying question
- [ ] Vision test report shared with user (go/no-go on Gemma vs Qwen-27B)

## Phase 5: Video
**Goal:** Short clip analysis.
Deliverables: ffmpeg frame sampling (2 fps, 768px, max 12 frames), user-tagged key moment (optional timestamp), limits (<=15 s, <=20 MB), background jobs (RQ/Celery) with progress events over SSE, timeline merge of observations, same RAG flow.
Acceptance:
- [ ] Upload -> progress -> answer works on 5 sample clips
- [ ] Limits enforced, temp files cleaned
- [ ] Failures reported cleanly to the UI

## Phase 6: Advanced
**Goal:** Extend value, in order of user choice (ask the user which to do first).
Options: VAR Protocol assistant collection; quiz mode ("test yourself on Law 11"); offside geometry research spike (YOLO + line detection + homography with user-selected frame; document feasibility before building); admin dashboard for feedback review; deployment (Docker, CI, monitoring).
Acceptance: defined with the user at phase start.
