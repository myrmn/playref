# API Contracts (Verified via scripts/smoke_apis.py)

## General
- Base URL: `https://aiforge.esprit.tn/api/v1`
- Auth: `Bearer <OPENAI_API_KEY>`
- OpenAI-compatible: `yes` (`/chat/completions`, `/embeddings`, streaming SSE, JSON mode)
- Rate limits: Generous / Enterprise tier on Esprit AI Platform (no throttling observed)
- Pricing is in TND per 1M tokens. Latency is sub-second across all models.

## Models
| Role | Model | Endpoint / notes | Verified Latency | Context |
|---|---|---|---|---|
| Chat / answer / rewrite | `Qwen3.6-35B-A3B` | `/chat/completions`, supports streaming & JSON mode | ~110-380 ms | 128K |
| Reasoning / multimodal | `Qwen3.6-27B` | `/chat/completions` | ~110 ms | 128K |
| Router | `Llama-3.2-3B` | `/chat/completions` | ~30 ms | 32K |
| Embeddings | `BGE-M3-Embeddings` | `/embeddings`; returns 1024-dim dense vector (sparse is not returned by API) | ~70 ms | 32K |
| Reranker | `BGE-Reranker-v2-m3` | `/rerank`; request `{"model", "query", "documents", "top_n"}`, response `{"results": [{"index", "relevance_score", "document"}]}` | ~25 ms | 32K |
| Vision | `Gemma-3-4B-IT` | `/chat/completions` (multimodal image format in Phase 4) | - | 32K |
| OCR | `Unlimited-OCR` | Hosted model endpoint | - | 32K |

## Resolved Questions from Smoke Tests
1. **Embeddings Sparse Support:** The `/embeddings` endpoint returns dense vectors of dimension 1024 only. PlayRef uses an in-engine BM25 sparse encoder (`BM25SparseEncoder` in `app/llm/embeddings.py`) to generate lexical weights for hybrid Qdrant search.
2. **Reranker request/response shape:** Native Cohere/BGE shape on `/rerank`. Request takes `query`, `documents`, and `top_n`; returns `relevance_score` and `index`.
3. **JSON mode & streaming:** `Qwen3.6-35B-A3B` natively supports both `response_format={"type": "json_object"}` and SSE streaming deltas (`data: {"choices": [{"delta": {"content": ...}}]}`).
4. **Endpoint stability & latency:** Verified with `scripts/smoke_apis.py` on 2026-11-05.
