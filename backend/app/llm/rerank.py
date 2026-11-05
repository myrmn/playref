"""Cross-encoder rerank client for PlayRef with graceful fallback."""

import time
from typing import Any

import httpx
from pydantic import BaseModel

from backend.app.config import settings
from backend.app.llm.errors import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    ModelResponseError,
    RateLimitError,
)
from backend.app.logger import logger


class RerankResult(BaseModel):
    index: int
    score: float
    text: str | None = None


class RerankClient:
    """Client for cross-encoder reranking."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 3.0,
    ):
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.model_rerank
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _map_http_error(self, response: httpx.Response) -> None:
        status = response.status_code
        if status in (401, 403):
            raise AuthenticationError(f"Auth failed ({status}): {response.text[:100]}")
        if status == 429:
            raise RateLimitError(f"Rate limited (429): {response.text[:100]}")
        if status >= 500:
            raise ModelResponseError(f"Server error ({status}): {response.text[:100]}")
        if status >= 400:
            raise ModelResponseError(f"Client error ({status}): {response.text[:100]}")

    async def _post_rerank(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/rerank"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self.headers, json=payload)
        except httpx.TimeoutException as exc:
            raise APITimeoutError(f"Rerank timeout with {url}") from exc
        except httpx.RequestError as exc:
            raise APIConnectionError(f"Rerank connection error with {url}") from exc

        self._map_http_error(response)
        return response.json()

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int | None = None,
    ) -> list[RerankResult]:
        """Rerank documents against a query. Falls back to original order on failure."""
        if not documents:
            return []

        top_k = top_n or len(documents)
        payload = {
            "model": self.model,
            "query": query,
            "documents": documents,
            "top_n": top_k,
        }

        start = time.perf_counter()
        try:
            data = await self._post_rerank(payload)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                f"Reranked {len(documents)} docs in {duration_ms}ms",
                extra={"duration_ms": duration_ms, "stage": "rerank"},
            )

            results: list[RerankResult] = []
            for item in data.get("results", []):
                doc_text = None
                if isinstance(item.get("document"), dict):
                    doc_text = item["document"].get("text")
                elif isinstance(item.get("document"), str):
                    doc_text = item.get("document")

                results.append(
                    RerankResult(
                        index=item["index"],
                        score=item["relevance_score"],
                        text=doc_text,
                    )
                )
            return results[:top_k]

        except Exception as exc:
            logger.warning(
                f"Reranker unavailable ({exc}); falling back gracefully to retrieval order"
            )
            # Fallback: preserve original order with synthetic rank score
            return [
                RerankResult(index=i, score=round(1.0 - (i * 0.01), 3), text=documents[i])
                for i in range(min(top_k, len(documents)))
            ]


rerank_client = RerankClient()
