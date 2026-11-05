"""Embedding Client for PlayRef (Local FastEmbed BGE + API fallback + BM25 Sparse)."""

import math
import re
import time
from collections import Counter

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.config import settings
from backend.app.llm.errors import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    ModelResponseError,
    RateLimitError,
)
from backend.app.logger import logger


class BM25SparseEncoder:
    """Local sparse lexical vector encoder for hybrid retrieval fallback."""

    def __init__(self, vocab_size: int = 100000):
        self.vocab_size = vocab_size

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def encode(self, text: str) -> tuple[list[int], list[float]]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0], [0.0]

        counts = Counter(tokens)
        indices_dict: dict[int, float] = {}
        for token, count in counts.items():
            idx = abs(hash(token)) % self.vocab_size
            weight = 1.0 + math.log(count)
            if idx in indices_dict:
                indices_dict[idx] = max(indices_dict[idx], weight)
            else:
                indices_dict[idx] = weight

        sorted_items = sorted(indices_dict.items(), key=lambda x: x[0])
        indices = [k for k, _ in sorted_items]
        values = [round(v, 4) for _, v in sorted_items]
        return indices, values

    def encode_batch(self, texts: list[str]) -> list[tuple[list[int], list[float]]]:
        return [self.encode(t) for t in texts]


sparse_encoder = BM25SparseEncoder()


class EmbeddingClient:
    """Client for generating dense embeddings (local FastEmbed or remote API) and sparse vectors."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        provider: str | None = None,
        timeout: float = 60.0,
    ):
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.model_embedding
        self.provider = (provider or settings.embedding_provider).lower()
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self._local_model = None

    def _get_local_model(self):
        if self._local_model is None:
            from fastembed import TextEmbedding

            # bge-large-en-v1.5 produces exact 1024-dim dense embeddings matching BGE-M3 dimension
            logger.info("Initializing local FastEmbed BGE model (1024-dim)...")
            self._local_model = TextEmbedding(model_name="BAAI/bge-large-en-v1.5")
        return self._local_model

    def _fallback_dense_embed(self, text: str, dim: int = 1024) -> list[float]:
        """Deterministic 1024-dim cosine-normalized representation for robust offline execution."""
        import hashlib
        vec = [0.0] * dim
        tokens = re.findall(r"\b\w+\b", text.lower())
        if not tokens:
            return vec
        counts = Counter(tokens)
        for token, count in counts.items():
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 16) & 1) else -1.0
            vec[idx] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        return vec

    def _map_http_error(self, response: httpx.Response) -> None:
        status = response.status_code
        if status in (401,):
            raise AuthenticationError(f"Auth failed ({status}): {response.text}")
        if status in (403, 429):
            raise RateLimitError(f"Rate limited or WAF blocked ({status}): {response.text[:150]}")
        if status >= 500:
            raise ModelResponseError(f"Server error ({status}): {response.text}")
        if status >= 400:
            raise ModelResponseError(f"Client error ({status}): {response.text}")

    @retry(
        retry=retry_if_exception_type((APIConnectionError, APITimeoutError, RateLimitError)),
        wait=wait_exponential(multiplier=2, min=3, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _embed_dense_api(self, texts: list[str]) -> list[list[float]]:
        url = f"{self.base_url}/embeddings"
        payload = {"model": self.model, "input": texts}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=self.headers, json=payload)
        self._map_http_error(response)
        data = response.json()
        sorted_data = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in sorted_data]

    async def embed_dense(self, texts: list[str]) -> list[list[float]]:
        """Generate dense embeddings via local model or API."""
        if not texts:
            return []

        start = time.perf_counter()

        if self.provider in ("local", "fastembed", "bge"):
            model = self._get_local_model()
            # FastEmbed embed returns an iterator of numpy arrays
            vecs = [v.tolist() for v in model.embed(texts)]
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                f"Locally embedded {len(texts)} texts in {duration_ms}ms",
                extra={"duration_ms": duration_ms, "stage": "embed_dense_local"},
            )
            return vecs

        # Fallback to remote API with graceful local fallback if blocked by WAF
        try:
            vecs = await self._embed_dense_api(texts)
        except Exception as exc:
            logger.warning(
                f"Remote embedding endpoint failed or blocked by WAF ({exc}). Falling back to local deterministic embeddings."
            )
            vecs = [self._fallback_dense_embed(t, dim=settings.embedding_dim) for t in texts]

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"Embedded {len(texts)} texts in {duration_ms}ms",
            extra={"duration_ms": duration_ms, "stage": "embed_dense"},
        )
        return vecs

    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query string."""
        results = await self.embed_dense([query])
        return results[0]

    def embed_sparse(self, text: str) -> tuple[list[int], list[float]]:
        """Compute sparse lexical vector for a text."""
        return sparse_encoder.encode(text)


embedding_client = EmbeddingClient()
