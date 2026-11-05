# PlayRef Progress Tracker

The agent updates this file. The user can read it anytime.

**Current phase:** Phase 2: Production pipeline + API + evaluation
**Last updated:** 2026-11-05

## Phase status
| Phase | Status | Approved by user |
|---|---|---|
| 1 Core RAG (CLI) | APPROVED/DONE | yes |
| 2 Pipeline + API + eval | AWAITING APPROVAL | no |
| 3 Web UI | NOT STARTED | no |
| 4 Image upload | NOT STARTED | no |
| 5 Video | NOT STARTED | no |
| 6 Advanced | NOT STARTED | no |

Status values: NOT STARTED | IN PROGRESS | AWAITING APPROVAL | APPROVED/DONE

## Task checklist (current phase)
- [x] 1. Router (Llama-3.2-3B: intent + multilingual language detection, off-topic redirect)
- [x] 2. Query rewrite (Qwen3.6-35B-A3B: chat history aware standalone English rewrite + keywords)
- [x] 3. Generation upgrades (Multilingual reply, clarifying question on missing facts, SSE streaming)
- [x] 4. Situation->law Q&A curated layer (data/curated/situations.jsonl with 65 pairs, user review sample provided)
- [x] 5. FastAPI routes & models (POST /chat SSE, GET /conversations/{id}, POST /feedback, GET /laws, GET /chunks/{id}, GET /health)
- [x] 6. Persistence & rate limiting (Postgres/Supabase schema & models, Redis rate limiter/cache fallback, SQLite fallback)
- [x] 7. Golden eval set & evaluation runner (105 items, LLM judge, markdown reports in eval/reports/)
- [x] 8. Unit & integration tests (router, rewrite, citations, API SSE demo: 16/16 tests passing)

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-11-05 | Switch embeddings to local FastEmbed BGE-large (1024-dim) | Campus WAF on AIForge endpoint rate-limited repeated batch requests (Attack ID 20000008). Local inference avoids provider bans and runs offline with 0 latency. |
| 2026-11-05 | Graceful degradation on cross-encoder reranker | If the remote rerank endpoint times out or errors, RerankerService immediately falls back to hybrid retrieval order with synthetic scores without breaking generation. |
| 2026-11-05 | Singleton pattern on Qdrant local storage | QdrantLocal places file locks on data/qdrant_storage; singleton client ensures unified access across retriever, parent expander, and ingestion without lock contention. |
| 2026-11-05 | Law preamble isolation in chunker (`section_number="0"`) | Reset `current_raw_section = None` on new law headers so Law overview/preambles (e.g. scoring directly from goal kicks/throw-ins) do not leak into preceding laws. |
| 2026-11-05 | `lazy="selectin"` for SQLAlchemy async relationships | Eliminates `MissingGreenlet` exceptions during asynchronous history loading across SQLite and PostgreSQL. |

## Known issues / tech debt
- Remote Qdrant runs in local embedded mode (data/qdrant_storage) when Docker Desktop service is inactive; Docker Compose configuration is ready for production container deployment.

## Open questions for the user
- None. Ready for Phase 2 approval.
