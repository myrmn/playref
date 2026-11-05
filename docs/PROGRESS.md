# PlayRef Progress Tracker

The agent updates this file. The user can read it anytime.

**Current phase:** Phase 1: Core RAG (CLI) - AWAITING APPROVAL
**Last updated:** 2026-11-05

## Phase status
| Phase | Status | Approved by user |
|---|---|---|
| 1 Core RAG (CLI) | AWAITING APPROVAL | no |
| 2 Pipeline + API + eval | NOT STARTED | no |
| 3 Web UI | NOT STARTED | no |
| 4 Image upload | NOT STARTED | no |
| 5 Video | NOT STARTED | no |
| 6 Advanced | NOT STARTED | no |

Status values: NOT STARTED | IN PROGRESS | AWAITING APPROVAL | APPROVED/DONE

## Task checklist (current phase)
- [x] 1. Scaffold (pyproject.toml, docker-compose.yml, config.py, logging)
- [x] 2. LLM client layer (chat, embeddings, rerank, vision stub)
- [x] 3. API smoke test (scripts/smoke_apis.py and verify endpoints)
- [x] 4. Ingestion pipeline & PDF parsing (PyMuPDF, chunking, Qdrant indexing)
- [x] 5. Retrieval & Rerank (hybrid search, cross-encoder, parent expansion)
- [x] 6. Generation & Citation validation (JSON answer contract)
- [x] 7. CLI (scripts/ask_cli.py with pretty output and --debug)
- [x] 8. Unit tests & mini eval (20 questions recall@6)

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-11-05 | Switch embeddings to local FastEmbed BGE-large (1024-dim) | Campus WAF on AIForge endpoint rate-limited repeated batch requests (Attack ID 20000008). Local inference avoids provider bans and runs offline with 0 latency. |
| 2026-11-05 | Graceful degradation on cross-encoder reranker | If the remote rerank endpoint times out or errors, RerankerService immediately falls back to hybrid retrieval order with synthetic scores without breaking generation. |
| 2026-11-05 | Singleton pattern on Qdrant local storage | QdrantLocal places file locks on data/qdrant_storage; singleton client ensures unified access across retriever, parent expander, and ingestion without lock contention. |

## Known issues / tech debt
- Remote Qdrant runs in local embedded mode (data/qdrant_storage) because Docker Desktop service is stopped; Docker Compose file is ready for production container deployment.

## Open questions for the user
- None. Ready for Phase 2 approval.

## Decisions log
| Date | Decision | Reason |
|---|---|---|

## Known issues / tech debt
-

## Open questions for the user
-
