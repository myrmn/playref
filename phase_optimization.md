# OPTIMIZATION PHASE: Harden and Speed Up (512 MB VPS)

Follow `AGENTS.md` strictly. This is a hardening phase on the existing build. Set `docs/PROGRESS.md`: "Optimization" = IN PROGRESS. Re-read `AGENTS.md`, `docs/PROGRESS.md` and the optimization strategy doc (3-tier embedding, Q&A cache, guest quota).

## Goal
Fix the weaknesses found in the review of the current cost/compute strategy, then add the performance upgrades. Do it in small steps, **measure before and after every step**, and run the gate after each step (report, then ask approval).

## Ground rules
- Do not add heavy dependencies. Target: total backend RAM stays under ~300 MB under load.
- One step at a time. After each step: tests, before/after numbers, short report, then ask: `Step N is complete. Approve Step N+1? (reply "approved" or list changes)`.
- Never claim a speedup or saving without a measurement. Put numbers in `docs/PROGRESS.md`.
- Keep all behavior behind config flags in `app/config.py` so each feature can be switched off.

---

## Step 0: Baseline and observability (do this first)

1. Add per-request metrics (JSON logs, and a `/metrics` or `/admin/stats` endpoint protected by an admin key):
   - latency per stage: router, rewrite, embed, retrieve, rerank, generate, total, plus time-to-first-token
   - cache hit/miss (exact and semantic), embedding API failures, fallback activations
   - tokens in/out per request
   - process RSS memory
2. Write `scripts/load_test.py` (async, configurable concurrency) replaying 50 questions from `eval/golden.jsonl`, with repeats, and report p50/p95 latency, error rate, peak RSS.
3. Run it and record the **baseline** in `docs/PROGRESS.md`.

Acceptance: baseline numbers recorded; stats endpoint works.

---

## Step 1: Server-side quota and rate limiting (security first)

Problem: the 5-question guest quota lives only in `localStorage`, so it is bypassable and does not protect the server or tokens.

Implement:
1. **Anonymous session token**: on first request, backend issues a signed (HMAC/JWT) httpOnly cookie with a random session id. Server-side counter per session id (Redis, or SQLite/Supabase if Redis is not available) enforces the 5 free questions. The frontend counter becomes display-only, driven by a server response header or field (`X-Quota-Remaining`).
2. **Per-IP and per-session rate limits** (e.g. 10 requests/minute, plus a daily cap per IP) with proper `429` + `Retry-After`. Read the real client IP behind the proxy (trusted `X-Forwarded-For` only from the reverse proxy / Cloudflare).
3. **Real auth validation**: verify a Supabase JWT server-side (signature, expiry, audience) on every authenticated request. Never trust `playref_user` or any client-sent identity.
4. **Member limits**: "unlimited" becomes a generous daily cap (default 100/day, configurable). **Demo login** accounts get a small cap (default 10/day) and expire.
5. **Global daily token budget**: when exceeded, the system degrades to **cache-only mode** (serve cached/curated answers, otherwise a friendly "high demand, try later" message). Admin can raise the cap by env var.
6. Optional but recommended: Cloudflare Turnstile verification on the first anonymous request (flag `TURNSTILE_ENABLED`).
7. Frontend: show quota from server values, handle `401/402/429` states gracefully (AuthModal for quota reached, countdown for rate limit).

Tests: quota cannot be bypassed by clearing cookies/localStorage without getting new limited sessions per IP; forged cookie rejected; expired JWT rejected; rate limit returns 429; budget exhaustion switches to cache-only.

---

## Step 2: Cache correctness (`backend/app/rag/cache.py`)

Problems found: key collisions/misses, lost meaning in normalization, caching things that should not be cached, no invalidation.

Implement:
1. **Normalization v2**:
   - lowercase, strip punctuation and accents consistently, language-aware stop words (EN/FR/AR)
   - **never strip** negations and positional/condition words: not, no, never, before, after, inside, outside, in, out, if, deliberate, accidental, and their FR/AR equivalents; keep numbers (e.g. "Law 12", "6 seconds")
   - **dedupe tokens** and sort, so "goal goal kick" and "goal kick" produce the same key
   - unit tests for pairs that must match (paraphrases) and pairs that must NOT match ("handball inside the box" vs "handball outside the box")
2. **Richer cache key**: hash of `normalized_query + lang + LAWS_EDITION + PROMPT_VERSION + GEN_MODEL`. Changing any of them invalidates automatically. Add `PROMPT_VERSION` to config.
3. **Cache only eligible answers**:
   - intent is a standalone `rules_question` (not scenario, not follow-up, not media)
   - no conversation history dependency
   - all citations validated, `needs_more_info == false`, no clarifying question
   - never cache error/abstain/off-topic outputs (unless explicitly curated)
4. **Eviction and feedback**: a thumbs-down or "wrong_law_cited" feedback on a cached answer deletes or quarantines that entry and increments a counter. Add TTL (default 30 days) and `last_hit_at`.
5. **Curated FAQ layer**: new table/flag `source = curated | generated`. Create `data/curated/faq.jsonl` with 40 reviewed FAQs (question variants in EN/FR/AR, answer JSON with citations, `reviewed_by`, `edition`). Provide `scripts/load_faq.py`. Curated entries are never evicted by feedback automatically (they are flagged for my review instead). **Ask me to review the first 10 before loading.**
6. **Single-flight**: if N identical uncached requests arrive at the same time, run one pipeline and share the result (in-process dict of `asyncio.Future` keyed by cache key; clean up on error/timeout).
7. Put a tiny in-process LRU (e.g. 200 entries) in front of the DB, and measure real hit latency against the DB (do not assume 5 ms if the DB is remote).

Tests: normalization pairs, key invalidation on edition/prompt change, ineligible answers not cached, feedback eviction, single-flight with 20 concurrent calls producing exactly 1 LLM call.

---

## Step 3: Embedding fallback (replace the fake dense fallback)

Problem: the hashed bag-of-words "Tier B" vector lives in a different space than the stored BGE-M3 vectors, so dense similarity against them is meaningless. Only the lexical half is valid.

Implement:
1. **Remove dense Tier B search.** When the remote embedding call fails, fall back to **sparse/BM25-only retrieval**. Keep BM25 index in memory (build at startup from `data/processed/chunks.jsonl`; a few hundred chunks is tiny).
2. **Resilient remote client** (`app/llm/`): one shared `httpx.AsyncClient` (keep-alive, connection limits), timeouts, retries with exponential backoff + jitter, a **circuit breaker** (open after N consecutive failures, half-open probe after cooldown), and a **client-side token bucket** to stay under the provider's WAF/rate limit.
3. Log every fallback activation with the reason; expose the counter in stats.
4. Store the **embedding model name and dimension** in Qdrant collection metadata (or a manifest file) and **assert at startup** that the configured model matches; fail fast with a clear error otherwise.
5. Evaluate fallback quality: run the eval set in forced-fallback mode (`FORCE_EMBED_FALLBACK=1`) and report recall@6 vs normal mode. Document the number honestly.
6. Decision to bring me: if fallback recall is poor, propose an optional small quantized multilingual embedding model (~100-150 MB) as a real offline fallback. It requires re-indexing with the same model, so do NOT implement without my approval.

Tests: remote failure triggers BM25-only; circuit breaker opens/closes; retries bounded; model mismatch at startup raises.

---

## Step 4: Vector store simplification and index hygiene

1. Check the actual vector count and index size. If it is a few hundred vectors, propose (with measurements) replacing QdrantLocal with **numpy cosine + in-memory BM25**, or keep Qdrant if hybrid search in local mode is verified working. Show RSS before/after and retrieval latency before/after; wait for my decision before switching.
2. Audit chunking: the current index has about 100 chunks for a ~230-page source, which suggests oversized chunks. Report the token-length distribution per chunk; if many exceed ~500 tokens, propose a re-chunk and re-index plan and measure recall@6 before/after on the eval set. Do not re-index without my approval.
3. Pick **one** relational store (SQLite or Supabase) and remove the other from docs/config. Report where the cache lives and its real round-trip latency.

---

## Step 5: Latency reductions (measure each one separately)

Apply one at a time with before/after p50/p95 on `scripts/load_test.py`:
1. **Disable thinking mode** for router, rewrite and generation if the API supports it (verify with a smoke test).
2. **Merge router + rewrite into one LLM call** returning `{intent, lang, standalone_query, keywords}`. Skip the rewrite entirely for first-turn messages that are already standalone; BGE-M3 is cross-lingual.
3. **Concurrency**: run independent steps in parallel with `asyncio.gather` (e.g. embedding while language/intent is determined, cache lookups while embedding).
4. **Rerank budget**: rerank top 15 instead of 30, and skip rerank when the top hybrid score margin is clearly decisive (tune threshold on the eval set; report any recall loss).
5. **Stream the short answer first** (time-to-first-token), then the structured payload.

Each change must keep eval metrics within tolerance (recall@6, citation accuracy, faithfulness must not drop by more than the threshold we agree on; propose one).

---

## Step 6: Semantic cache

1. Reuse the query embedding already computed in the pipeline (no extra API call). Maintain a small cache vector collection (or in-memory matrix) of **eligible** answered questions.
2. Lookup before retrieval; threshold default 0.95, configurable. If hit -> serve cached answer; if miss -> reuse the same vector for retrieval.
3. Same eligibility, key (edition/prompt/model) and eviction rules as Step 2. Never serve a semantic hit across languages unless the cached entry exists for that language.
4. Evaluate false-positive risk: build 30 near-miss pairs (e.g. inside/outside the box, direct vs indirect free kick) and show none of them collide at the chosen threshold. Report the threshold table.

---

## Step 7: Server hardening and static FAQ pages

1. **VPS hardening** (scripts/docs, not code churn): single uvicorn worker, concurrency semaphore on the pipeline, `MALLOC_ARENA_MAX=2`, systemd unit with `MemoryMax` and restart policy, swap file as a safety net, ensure PyMuPDF/ingestion is never imported at runtime, log rotation. Put it in `docs/DEPLOY_LOW_MEMORY.md` with exact commands.
2. **Cloudflare** in front of the VPS: write the setup checklist (proxy, rate-limit rules, bot protection, caching of static assets) in the same doc.
3. **Static FAQ pages** on the Vercel frontend: generate `/faq/[slug]` pages at build time from `data/curated/faq.jsonl` (question, answer card, citations, "Ask a follow-up in the chat" button, proper title/meta tags and JSON-LD FAQ schema). Zero backend load.
4. Final load test: compare against the baseline from Step 0 and update the RAM/latency table in the strategy doc with **measured** numbers only.

---

## Final report (after Step 7)
- Before/after table: p50/p95 latency (cache miss, exact hit, semantic hit), peak RSS, error rate, tokens/request, cache hit rate on the replayed traffic.
- Eval metrics before/after.
- What was not implemented and why.
- Updated checklist in the strategy doc, with unverified claims removed or marked as estimates.

Update `docs/PROGRESS.md` and STOP.
