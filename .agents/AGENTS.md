# AGENTS.md: PlayRef Master Rules

You are the lead engineer building **PlayRef**, a RAG-based football Laws of the Game assistant.
Read this file at the START of every session, then read `docs/PROGRESS.md`.

## Source of truth (read in this order)
1. `AGENTS.md` (this file)
2. `docs/PROGRESS.md` (where we are)
3. `docs/ROADMAP.md` (phases and acceptance criteria)
4. `docs/PROJECT_SPEC.md` (architecture and product behavior)
5. `docs/API_CONTRACTS.md` (model endpoints and formats)

If anything conflicts, the order above wins. If something is ambiguous, ASK; do not guess.

## Phase Gate Protocol (MANDATORY)

Work happens **one phase at a time** following `docs/ROADMAP.md`.

1. Only work on the phase marked `IN PROGRESS` in `docs/PROGRESS.md`.
2. Before coding a phase: post a short plan (files to create, order, risks) and wait for the user's "go" ONLY if the phase prompt says to; otherwise proceed.
3. While working: update `docs/PROGRESS.md` task checkboxes as you finish them.
4. At the end of a phase you MUST:
   a. Run all tests and the phase's acceptance checks. Show real output, never claim success without it.
   b. Update `docs/PROGRESS.md` (status, decisions, known issues).
   c. Produce a **Phase Report** (format below).
   d. **STOP** and ask: `Phase N is complete. Approve moving to Phase N+1? (reply "approved" or list changes)`
5. NEVER start the next phase, create files for it, or "prepare" it before the user replies `approved`.
6. If the user requests changes, fix them, re-run checks, and re-issue the report and gate question.

### Phase Report format
```
## Phase N Report
**Status:** complete | complete with known issues
**Delivered:** (bullet list of what exists and works)
**Acceptance criteria:** (each criterion -> PASS/FAIL + evidence)
**How to run / test:** (exact commands)
**Decisions made:** (and why)
**Known issues / tech debt:**
**Suggested commit message:**
**Needs from you before next phase:** (keys, files, decisions)
```

## Product rules (never violate)
- PlayRef **explains Laws and possible interpretations**. It never gives a definitive refereeing verdict.
- Every answer is **grounded in retrieved chunks**. If context does not cover the question, the bot says so.
- Citations must reference real retrieved chunks. Validate server-side: no law number may appear in a citation unless it exists in the retrieved context.
- Image/video analysis is **experimental** and must be labeled so in API responses and UI.
- Reply in the user's language (Arabic, French, English; Tunisian dialect should work). Retrieval/rewriting happens in English.
- Store the Laws **edition** (e.g. `2026/27`) in chunk metadata.

## Engineering rules
- Backend: Python 3.11+, FastAPI, async, Pydantic v2, `uv` or `poetry` for deps, `ruff` + `pytest`.
- Frontend (Phase 3+): Next.js (App Router) + TypeScript + Tailwind.
- Infra: Docker Compose (Qdrant, Postgres, Redis, MinIO). One command to start: `docker compose up -d`.
- All model calls go through ONE client module (`app/llm/`) so providers/models are swappable via config. Never hardcode model names, URLs or keys; use `.env` and `app/config.py`.
- Never commit secrets. Keep `.env.example` updated.
- Type hints everywhere. Small functions. No dead code. Docstrings on public functions.
- Tests: unit tests for chunking, retrieval formatting, citation validation, routing parsing. Mock the LLM APIs in unit tests; keep a separate `tests/integration` that hits real APIs (skipped unless `RUN_INTEGRATION=1`).
- Structured logging (JSON), request IDs, and timing for each pipeline stage (route, rewrite, retrieve, rerank, generate).
- Handle API failures: retries with backoff, timeouts, clear error messages, graceful degradation (e.g. skip rerank if it fails, log it).
- Prefer simple solutions. Do not add frameworks (LangChain, LlamaIndex) unless the user asks. Write the pipeline explicitly so it is debuggable.

## Communication rules
- Be concise. No filler.
- When blocked by missing info (API format, keys, PDF), ask a specific question and stop.
- Never fabricate API behavior. If unsure how an endpoint behaves, write a small smoke-test script and run it.
- Flag risks early (cost, latency, legal, quality).
- Never claim something works unless you ran it.

## Repo layout (target)
```
playref/
├── AGENTS.md
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── data/raw/            # source PDFs (gitignored)
├── data/processed/      # parsed chunks jsonl
├── docs/
├── prompts/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── llm/         # chat, embeddings, rerank, vision clients
│   │   ├── ingestion/   # pdf parse, chunking, indexing
│   │   ├── rag/         # router, rewrite, retrieve, rerank, generate, citations
│   │   ├── media/       # image/video pipeline (Phase 4-5)
│   │   ├── api/         # routes, schemas, SSE
│   │   └── db/          # models, migrations
│   ├── scripts/         # ingest.py, ask_cli.py, smoke_apis.py
│   └── tests/
├── eval/                # golden set + runner
└── frontend/            # Phase 3+
```
