"""Embedding Client for PlayRef (Dense BGE-M3 + Local Sparse fallback)."""

import math
import re
import time
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple
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
    """Local sparse lexical vector encoder for hybrid retrieval fallback.
    
    Produces sparse vectors {indices: List[int], values: List[float]} 
    compatible with Qdrant SparseVector schema using Murmur/Python hashing.
    """

    def __init__(self, vocab_size: int = 100000):
        self.vocab_size = vocab_size

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase and extract alphanumeric words
        return re.findall(r"\b\w+\b", text.lower())

    def encode(self, text: str) -> Tuple[List[int], List[float]]:
        """Encode a single text into sparse indices and TF-IDF / term-frequency weights."""
        tokens = self._tokenize(text)
        if not tokens:
            return [0], [0.0]

        counts = Counter(tokens)
        max_tf = max(counts.values())

        indices_dict: Dict[int, float] = {}
        for token, count in counts.items():
            # Hash to index within vocab_size
            idx = abs(hash(token)) % self.vocab_size
            # Sublinear term frequency weighting: 1 + log(tf)
            weight = 1.0 + math.log(count)
            if idx in indices_dict:
                indices_dict[idx] = max(indices_dict[idx], weight)
            else:
                indices_dict[idx] = weight

        # Sort indices for Qdrant requirement
        sorted_items = sorted(indices_dict.items(), key=lambda x: x[0])
        indices = [k for k, _ in sorted_items]
        values = [round(v, 4) for _, v in sorted_items]
        return indices, values

    def encode_batch(self, texts: List[str]) -> List[Tuple[List[int], List[float]]]:
        """Encode a batch of texts."""
        return [self.encode(t) for t in texts]


sparse_encoder = BM25SparseEncoder()


class EmbeddingClient:
    """Client for generating dense embeddings via API and sparse embeddings locally."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.model_embedding
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

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
    async def embed_dense(self, texts: List[str]) -> List[List[float]]:
        """Generate dense embeddings for a list of strings."""
        if not texts:
            return []

        url = f"{self.base_url}/embeddings"
        payload: Dict[str, Any] = {
            "model": self.model,
            "input": texts,
        }
        start = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self.headers, json=payload)
        except httpx.TimeoutException as exc:
            raise APITimeoutError(f"Embeddings timeout with {url}") from exc
        except httpx.RequestError as exc:
            raise APIConnectionError(f"Embeddings connection error with {url}") from exc

        self._map_http_error(response)
        data = response.json()
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"Embedded {len(texts)} texts in {duration_ms}ms",
            extra={"duration_ms": duration_ms, "stage": "embed_dense"},
        )

        try:
            # Sort items by index to preserve order
            sorted_data = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_data]
        except (KeyError, IndexError) as exc:
            raise ModelResponseError(f"Invalid embedding response format: {data}") from exc

    async def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""
        results = await self.embed_dense([query])
        return results[0]

    def embed_sparse(self, text: str) -> Tuple[List[int], List[float]]:
        """Compute sparse lexical vector for a text."""
        return sparse_encoder.encode(text)


embedding_client = EmbeddingClient()
