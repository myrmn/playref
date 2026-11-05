# PHASE 2: Production pipeline + API + evaluation

Precondition: I replied "approved" for Phase 1. Set `docs/PROGRESS.md`: Phase 2 = IN PROGRESS. Re-read `AGENTS.md`, `docs/ROADMAP.md`, `docs/PROGRESS.md` first.

## Goal
Turn the CLI pipeline into a robust, multilingual, conversational backend with a streaming API and a real evaluation harness.

## Tasks

### 1. Router (`app/rag/router.py`)
- Llama-3.2-3B classifies: `intent` in {rules_question, scenario, media, off_topic} and `lang` in {en, fr, ar, other}. Forced JSON, Pydantic-validated, fallback to {scenario, en} on failure.
- Handle Tunisian dialect / Arabizi / mixed languages reasonably.
- Off-topic: polite redirect in the user's language; no retrieval.

### 2. Query rewrite (`app/rag/rewrite.py`)
- Qwen3.6-35B-A3B rewrites the latest message + chat history into a standalone English query plus keywords and an optional `law_hint`.
- Must work for follow-ups: "what if it was outside the box?"
- Keep it fast: low max_tokens, no thinking mode if the API allows disabling it.

### 3. Generation upgrades
- Answer in the user's language while retrieval stays English.
- Add `needs_more_info` + `clarifying_question` behavior when key facts are missing.
- Streaming: stream the `short_answer` tokens first, then emit the full structured payload as the final event.
- Server-side citation validation stays mandatory; add tests for stripped citations.

### 4. Situation->law Q&A layer
- Create `data/curated/situations.jsonl` with 60+ short Q&A pairs mapping fan phrasing to laws (offside, handball, DOGSO, advantage, penalty area fouls, goal kick, throw-in, substitutions, VAR scope, etc.).
- Index them as a separate Qdrant collection or payload type `kind=situation`; retrieval merges both with the Laws as primary source. Citations must still point to the official Law chunks.
- Ask me to review the file before indexing.

### 5. API (`app/api/`)
- `POST /chat` (SSE streaming), `GET /conversations/{id}`, `POST /feedback`, `GET /laws` and `GET /laws/{n}` (for the Law browser), `GET /chunks/{chunk_id}` (for the citation drawer), `GET /health`.
- Pydantic schemas, OpenAPI docs, CORS config, request IDs.
- Stage timing in logs and in a debug field when `DEBUG=1`.

### 6. Persistence and limits
- Supabase: conversations, messages (store answer JSON + retrieved chunk ids), feedback (thumbs, reason incl. "wrong_law_cited").
- Redis rate limiting (per IP/session) and optional response cache for identical standalone queries.


### 7. Evaluation (`eval/`)
- Golden set `eval/golden.jsonl`, 100+ items: rules questions, scenario questions, EN/FR/AR variants of the same questions, trap questions (not covered by Laws, missing info), off-topic.
  Fields: `id, question, lang, expected_laws[], expected_behavior (answer|abstain|clarify|redirect)`.
- Runner `eval/run_eval.py` with metrics: retrieval recall@6, citation accuracy (cited chunks all in retrieved set and matching expected laws), faithfulness (LLM judge with Qwen3.6-27B, claim-by-claim), abstention accuracy, language match, latency p50/p95.
- Output a Markdown report in `eval/reports/` and a comparison against the previous run.
- Draft the golden set, then ask me to review a sample of 20 before relying on it.

### 8. Tests
Unit tests for router parsing, rewrite with history, citation stripping, API schema, rate limiter. One integration test for `/chat` guarded by `RUN_INTEGRATION=1`.

## Out of scope
Web UI, image/video, auth/user accounts.

## Acceptance criteria
See Phase 2 in `docs/ROADMAP.md`. Show: a curl SSE demo, an Arabic/French/English example each, a follow-up example, the eval report.

## When done
Phase Report, update `docs/PROGRESS.md` to AWAITING APPROVAL, STOP and ask:
"Phase 2 is complete. Approve moving to Phase 3? (reply "approved" or list changes)"
