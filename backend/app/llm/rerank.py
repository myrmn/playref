"""Cross-encoder rerank client for PlayRef."""

import time
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel
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


class RerankResult(BaseModel):
    index: int
    score: float
    text: Optional[str] = None


class RerankClient:
    """Client for cross-encoder reranking."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
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
            raise AuthenticationError(f"Auth failed ({status}): {response.text}")
        if status == 429:
            raise RateLimitError(f"Rate limited (429): {response.text}")
        if status >= 500:
            raise ModelResponseError(f"Server error ({status}): {response.text}")
        if status >= 400:
            raise ModelResponseError(f"Client error ({status}): {response.text}")

    @retry(
        retry=retry_if_exception_type((APIConnectionError, APITimeoutError, RateLimitError)),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _post_rerank(self, payload: Dict[str, Any]) -> Dict[str, Any]:
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
        documents: List[str],
        top_n: Optional[int] = None,
    ) -> List[RerankResult]:
        """Rerank documents against a query.
        
        Gracefully falls back to original order if the reranker fails.
        """
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

            results: List[RerankResult] = []
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
            logger.error(
                f"Reranker failed with error ({exc}); degrading gracefully to retrieval order",
                exc_info=True,
            )
            # Fallback: preserve original order with mock score 1.0 - (rank * 0.01)
            return [
                RerankResult(index=i, score=round(1.0 - (i * 0.01), 3), text=documents[i])
                for i in range(min(top_k, len(documents)))
            ]


rerank_client = RerankClient()

