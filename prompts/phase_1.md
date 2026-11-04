# PHASE 1: Core RAG (CLI)

Set `docs/PROGRESS.md`: Phase 1 = IN PROGRESS. Follow `AGENTS.md` strictly.

## Goal
A command-line assistant that answers football-rules questions from the IFAB Laws PDF with citations to real chunks.

## Step 0: Plan first
Post a short plan (file list, order, risks) and then proceed. If `docs/API_CONTRACTS.md` has unfilled blanks that block you, ask me and stop.

## Tasks (in this order)

### 1. Scaffold
- Repo layout from AGENTS.md, `pyproject.toml` (ruff, pytest, httpx, pydantic, pydantic-settings, qdrant-client, pymupdf, tiktoken or similar, tenacity, rich/typer for CLI).
- `docker-compose.yml`: Qdrant + Postgres (Redis and MinIO may be added later).
- `app/config.py` with pydantic-settings reading `.env`.
- JSON structured logging helper.

### 2. LLM client layer (`app/llm/`)
- `chat.py`: async chat completion (supports streaming and JSON mode if available).
- `embeddings.py`: dense (+ sparse if the API provides it; otherwise implement a local sparse fallback and tell me).
- `rerank.py`: cross-encoder rerank client.
- `vision.py`: stub only (implemented in Phase 4).
- Shared: timeouts, retries with exponential backoff (tenacity), typed errors.

### 3. API smoke test: `scripts/smoke_apis.py`
Call every endpoint with a trivial input and print: status, latency, response shape, embedding dimension, whether sparse is returned, whether JSON mode and streaming work, and the real context limits you can verify. Run it and show me the output. Update `docs/API_CONTRACTS.md` with the verified facts.

### 4. Ingestion (`app/ingestion/`, `scripts/ingest.py`)
- Parse `data/raw/laws_of_the_game.pdf` with PyMuPDF using font size/boldness to detect the heading hierarchy (Law N > title > section > sub-section).
- Structure-aware chunking: 200-500 tokens, never cross a heading, keep tables/bullets with their heading, add `parent_id`.
- Metadata exactly as in `PROJECT_SPEC.md` (edition from `LAWS_EDITION` env).
- Prepend the section path to the text used for embedding. Store the original clean text separately for display/citation.
- Save chunks to `data/processed/chunks.jsonl`.
- Detect pages that look like diagrams/images and record them as `page_images` metadata (do not embed).
- Embed in batches, upsert into Qdrant collection with named dense vector + sparse vector. Idempotent: re-running does not duplicate.
- Print a summary: number of laws, chunks, avg tokens, chunks per law.
- **Show me 10 random chunks** (text + metadata) and ask me to confirm quality before continuing.

### 5. Retrieval + rerank (`app/rag/`)
- `retrieve.py`: hybrid search (dense + sparse fusion, RRF or Qdrant native), top 30, optional filter by `law_number`.
- `rerank.py` usage: top 6 after rerank; if rerank fails, fall back to retrieval order and log.
- `parents.py`: optionally attach the parent section text.

### 6. Generation (`app/rag/generate.py`)
- System prompt from `PROJECT_SPEC.md`.
- Context formatting with `[chunk_id | Law N - Section | page]` headers.
- Output JSON per the answer contract; parse + validate with Pydantic; retry once on malformed JSON.
- Citation validator: drop any citation whose `chunk_id` is not in the retrieved set.

### 7. CLI: `scripts/ask_cli.py`
- `python scripts/ask_cli.py "Can a goalkeeper score from a goal kick?"`
- Pretty output: short answer, laws, interpretations, then a debug panel (`--debug`) showing retrieved/reranked chunks with scores and per-stage timings.

### 8. Tests and mini eval
- Unit tests: chunking invariants, metadata completeness, citation validator, JSON parsing, rerank fallback (mock APIs).
- `eval/mini_eval.jsonl`: 20 questions with expected law numbers, `eval/run_mini_eval.py` reporting recall@6 and a pass/fail list. Draft the 20 questions yourself, then ask me to review them.

## Out of scope (do NOT build)
Router, query rewriting, multilingual handling, FastAPI routes, database persistence, UI, image/video. Those are later phases.

## Acceptance criteria
See Phase 1 in `docs/ROADMAP.md`. Show real command output for each.

## When done
Produce the Phase Report (format in AGENTS.md), update `docs/PROGRESS.md` to AWAITING APPROVAL, then STOP and ask:
"Phase 1 is complete. Approve moving to Phase 2? (reply "approved" or list changes)"
