# PlayRef Progress Tracker

The agent updates this file. The user can read it anytime.

**Current phase:** Optimization: Harden and Speed Up (512 MB VPS)
**Last updated:** 2026-11-06

## Phase status
| Phase | Status | Approved by user |
|---|---|---|
| 1 Core RAG (CLI) | APPROVED/DONE | yes |
| 2 Pipeline + API + eval | APPROVED/DONE | yes |
| 3 Web UI | APPROVED/DONE | yes |
| Optimization | IN PROGRESS | no |
| 4 Image upload | NOT STARTED | no |
| 5 Video | NOT STARTED | no |
| 6 Advanced | NOT STARTED | no |

Status values: NOT STARTED | IN PROGRESS | AWAITING APPROVAL | APPROVED/DONE

## Task checklist (current phase: Optimization)
- [x] Step 0: Baseline and observability
- [ ] Step 1: Server-side quota and rate limiting
- [ ] Step 2: Cache correctness
- [ ] Step 3: Embedding fallback
- [ ] Step 4: Vector store simplification and index hygiene
- [ ] Step 5: Latency reductions
- [ ] Step 6: Semantic cache
- [ ] Step 7: Server hardening and static FAQ pages

## Optimization Phase Baselines & Progress

### Step 0 Baseline Metrics (50 queries from `eval/golden.jsonl`, concurrency 2)
- **Date:** 2026-11-06
- **Test execution:** `py scripts/load_test.py --num-requests 50 --concurrency 2 --in-process`
- **Total Requests:** 50 (50 successful, 0 failed, 0.0% error rate)
- **Total Wall Clock:** 136.71s (0.37 req/s)
- **Client Latency:**
  - Min: 16.15 ms (Cache Hit)
  - Max: 11,762.29 ms
  - Avg: 5,462.06 ms
  - p50: 7,384.65 ms
  - p95: 9,683.86 ms
  - p99: 11,762.29 ms
  - TTFT p50: 7,384.65 ms
- **Server Stage Breakdown (ms):**
  - Router: p50: 1,177.2 ms | p95: 2,245.6 ms | avg: 1,247.21 ms
  - Rewrite: p50: 1,335.2 ms | p95: 2,423.2 ms | avg: 1,422.00 ms
  - Embed: p50: 0.9 ms | p95: 2.0 ms | avg: 0.93 ms
  - Retrieve: p50: 8.9 ms | p95: 86.4 ms | avg: 13.91 ms
  - Rerank: p50: 1,008.8 ms | p95: 1,452.2 ms | avg: 1,007.14 ms
  - Generate: p50: 4,162.3 ms | p95: 5,933.9 ms | avg: 4,223.75 ms
- **Memory RSS:**
  - Initial RSS: 218.47 MB
  - Final Current RSS: 250.73 MB
  - Peak Observed RSS: 295.17 MB (strictly within 300 MB limit)
- **Cache Performance (Cold Start + 15 Replayed Queries):**
  - Exact Hits: 16
  - Semantic Hits: 0
  - Misses: 34
  - Hit Rate: 32.0%
- **Token Consumption:**
  - Prompt Tokens: 11,277
  - Completion Tokens: 45,138
  - Total Tokens: 56,415
  - Avg Tokens/Req: 1,128.3 tokens

## Decisions log
| Date | Decision | Reason |
|---|---|---|
| 2026-11-06 | Observability engine `backend/app/metrics.py` & `/admin/stats` | Added low-overhead in-memory tracking of stage latencies, memory RSS, token counts, and cache performance protected by `ADMIN_API_KEY`. |
| 2026-11-06 | `threading.RLock()` for thread-safe metrics | Avoids internal self-deadlocking when reading metrics from multiple nested inspection calls. |
| 2026-11-06 | Non-blocking Redis fallback in rate limiter | Marks Redis as unavailable after first connection failure to prevent 4s timeout penalties on every subsequent incoming request. |
| 2026-11-06 | Explicit SQLite connection in local `.env` | Prevents 8s connection timeout attempts towards Postgres when running locally. |
| 2026-11-05 | Switch embeddings to local FastEmbed BGE-large (1024-dim) | Campus WAF on AIForge endpoint rate-limited repeated batch requests (Attack ID 20000008). Local inference avoids provider bans and runs offline with 0 latency. |
| 2026-11-05 | Graceful degradation on cross-encoder reranker | If the remote rerank endpoint times out or errors, RerankerService immediately falls back to hybrid retrieval order with synthetic scores without breaking generation. |
| 2026-11-05 | Singleton pattern on Qdrant local storage | QdrantLocal places file locks on data/qdrant_storage; singleton client ensures unified access across retriever, parent expander, and ingestion without lock contention. |
| 2026-11-05 | Law preamble isolation in chunker (`section_number="0"`) | Reset `current_raw_section = None` on new law headers so Law overview/preambles (e.g. scoring directly from goal kicks/throw-ins) do not leak into preceding laws. |
| 2026-11-05 | `lazy="selectin"` for SQLAlchemy async relationships | Eliminates `MissingGreenlet` exceptions during asynchronous history loading across SQLite and PostgreSQL. |
| 2026-11-05 | Next.js App Router for frontend in `frontend/` | Meets project spec & engineering rules with native SSR/client boundary, TypeScript, Tailwind CSS, Lucide icons, and zero-dependency SSE parsing. |
| 2026-11-05 | Dynamic RTL switching via `document.documentElement.dir` | Dynamically flips document layout, drawer slide animations, and Cairo font for Arabic (`ar`) while preserving LTR for English and French. |
| 2026-11-05 | Hermetic Qdrant mocking in unit tests | Avoids unit test failures when local vector storage has not yet undergone full ingestion by mocking `scroll()` and `count()` in `test_api.py`. |

## Next Steps & How to Resume
- **Current Position:** Optimization Phase, **Step 0 is complete**. Ready to start **Step 1: Server-side quota and rate limiting**.
- **When resuming:**
  1. Review Step 0 baseline metrics in this document and [`docs/OPTIMIZATION_PROGRESS.md`](file:///c:/Users/Mohamed%20Islem/Desktop/playref/docs/OPTIMIZATION_PROGRESS.md).
  2. Run `py -m pytest backend/tests/ -v` to ensure all 17 tests pass.
  3. Approve starting **Step 1** (Server-side HMAC/JWT session cookies, per-IP sliding rate limits, real Supabase JWT auth verification, member caps, and emergency global token budget).

## Known issues / tech debt
- Remote Qdrant runs in local embedded mode (data/qdrant_storage) when Docker Desktop service is inactive; Docker Compose configuration is ready for production container deployment.

## Open questions for the user
- Step 0 complete. Awaiting user approval to begin Step 1.
