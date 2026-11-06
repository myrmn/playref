# PlayRef Optimization Phase: Implementation & Benchmark Progress

> **Phase:** Optimization: Harden and Speed Up (512 MB VPS)  
> **Target Hardware:** 512 MB RAM / 1 vCPU VPS  
> **Status:** Step 0 Complete | Step 1 Awaiting Approval  
> **Last Updated:** 2026-11-06  

---

## 1. Overview & Approach

In accordance with `AGENTS.md` and the optimization roadmap, we are executing a phased hardening sequence to ensure high throughput, zero out-of-memory crashes on a 512 MB RAM VPS, and minimal LLM token consumption.

Every optimization is:
1. Measured before and after.
2. Controllable via flags in `backend/app/config.py`.
3. Verified against the 17 unit tests and the 50-query golden benchmark (`eval/golden.jsonl`).

---

## 2. Step 0 Delivered: Baseline & Observability

### 2.1 Metrics & Observability Engine (`backend/app/metrics.py`)
* Created a thread-safe, low-overhead in-memory metrics collector utilizing `threading.RLock()`.
* **Stage Latency Tracking:** Records min, max, avg, p50, p95, and p99 for all pipeline stages:
  * `router`, `rewrite`, `embed`, `retrieve`, `rerank`, `generate`, and `ttft` (time-to-first-token).
* **Token Tracking:** Real-time token usage calculation using `tiktoken` (`cl100k_base`).
* **Memory Tracking:** Live process RSS and peak RSS memory via `psutil`.
* **Cache Metrics:** Exact hits, semantic hits, and misses.
* **Embedding Events:** API calls, API failures, and deterministic fallback activations.

### 2.2 Security & Admin Endpoints (`backend/app/api/routes.py`)
* Added `/admin/stats` and `/metrics` protected by `X-Admin-Key` header or `?admin_key=` query parameter.
* Added `/admin/stats/reset` (POST) to allow reset between test runs.
* Configured `settings.admin_api_key` in `backend/app/config.py`.
* Added structured JSON logging on every `/chat` completion with request ID, duration, TTFT, stage timings, token breakdown, and RSS memory.

### 2.3 Load Testing Tool (`scripts/load_test.py`)
* Built an async load test suite replaying queries from `eval/golden.jsonl`.
* Configurable concurrency, request count, streaming mode, and in-process ASGI / external HTTP execution.
* Automatically captures client-side latencies and correlates with server-side stage metrics and RSS memory.

### 2.4 Immediate Runtime Fixes Applied
1. **Redis Connection Stall Elimination:**
   * *Problem:* When Redis is not running locally, `aioredis.ping()` was attempted on every request with a 4-second socket timeout.
   * *Fix:* Marked Redis as attempted on first check in `backend/app/db/rate_limiter.py`. Latency on cache hits dropped from ~4.3s to **~16ms**.
2. **Postgres Connection Stall Elimination:**
   * *Problem:* `DATABASE_URL` defaulted to Postgres, waiting 8 seconds for a connection timeout before falling back to SQLite.
   * *Fix:* Set explicit SQLite URI in local `.env` (`DATABASE_URL=sqlite+aiosqlite:///data/playref.db`), eliminating the 8-second startup stall.
3. **Re-entrant Lock Fix in Metrics:**
   * *Problem:* Calling `get_stats()` held an internal lock and invoked `get_process_rss_mb()`, which attempted to acquire the same lock.
   * *Fix:* Replaced `threading.Lock` with `threading.RLock` and factored out un-locked RSS reads.

---

## 3. Step 0 Measured Baseline (50 Queries, Concurrency = 2)

```
==================================================================
  PLAYREF LOAD TEST & BASELINE BENCHMARK
==================================================================
  Target URL:        http://test (In-Process ASGI)
  Dataset:           eval/golden.jsonl (50 queries)
  Concurrency:       2
  Stream mode:       False
  Initial RSS:       218.47 MB
==================================================================

Total Requests:     50
Successful:         50
Failed:             0 (0.0% error rate)
Total Wall Clock:   136.71s (0.37 req/s)

--- CLIENT LATENCIES (ms) ---
Min: 16.15 ms (Cache Hit) | Max: 11,762.29 ms | Avg: 5,462.06 ms
p50: 7,384.65 ms | p95: 9,683.86 ms | p99: 11,762.29 ms
TTFT p50: 7,384.65 ms

--- SERVER STAGE BREAKDOWN (ms) ---
  Router     p50:  1,177.2 ms | p95:  2,245.6 ms | avg: 1,247.21 ms
  Rewrite    p50:  1,335.2 ms | p95:  2,423.2 ms | avg: 1,422.00 ms
  Embed      p50:      0.9 ms | p95:      2.0 ms | avg:    0.93 ms
  Retrieve   p50:      8.9 ms | p95:     86.4 ms | avg:   13.91 ms
  Rerank     p50:  1,008.8 ms | p95:  1,452.2 ms | avg: 1,007.14 ms
  Generate   p50:  4,162.3 ms | p95:  5,933.9 ms | avg: 4,223.75 ms

--- MEMORY & SYSTEM ---
  Current RSS:      250.73 MB
  Peak RSS:         295.17 MB (Strictly under 300 MB budget)

--- CACHE PERFORMANCE ---
  Exact Hits:       16 (32.0% hit rate on initial cold run + 15 repeats)
  Misses:           34

--- TOKEN USAGE ---
  Prompt Tokens:    11,277
  Completion Toks:  45,138
  Total Tokens:     56,415
  Avg Toks/Req:     1,128.3
```

---

## 4. Next Optimization Steps Ahead

1. **Step 1: Server-side Quota & Rate Limiting:**
   * Signed HTTP-only session tokens for guests (5 free queries enforced server-side).
   * Per-IP sliding window rate limiting (10 req/min).
   * Real Supabase JWT validation server-side.
   * Member daily caps (100/day) and demo login expiration.
   * Global token emergency budget fallback to cache-only mode.
2. **Step 2: Cache Correctness:**
   * Normalization v2 (preserves conditions/positions, deduplicates tokens).
   * Key invalidation hashes with `PROMPT_VERSION` and `LAWS_EDITION`.
   * Single-flight execution for concurrent identical queries.
3. **Step 3: Embedding Fallback:**
   * BM25-only sparse retrieval fallback when embedding API is down.
   * Resilient HTTP client with circuit breaker.
4. **Step 4: Vector Store & Index Hygiene:**
   * Index audit and relational store finalization.
5. **Step 5: Latency Reductions:**
   * Thinking-mode toggles, router + rewrite merger, rerank budget tuning.
6. **Step 6: Semantic Cache:**
   * Vector-similarity query cache (threshold $\ge 0.95$).
7. **Step 7: Production Hardening:**
   * Single-worker Uvicorn configuration, swap file, Cloudflare checklists.
