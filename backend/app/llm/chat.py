"""Async Chat Completion Client for PlayRef."""

import json
import time
from collections.abc import AsyncGenerator
from typing import Any

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


class ChatClient:
    """Async OpenAI-compatible chat client."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
    ):
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _map_http_error(self, response: httpx.Response) -> None:
        """Map HTTP error status codes to typed exceptions."""
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
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = 2048,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Execute a non-streaming chat completion."""
        target_model = model or settings.model_chat
        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format:
            payload["response_format"] = response_format

        url = f"{self.base_url}/chat/completions"
        start = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=self.headers, json=payload)
        except httpx.TimeoutException as exc:
            logger.warning(f"Timeout calling chat model {target_model}: {exc}")
            raise APITimeoutError(f"Timeout communicating with {url}") from exc
        except httpx.RequestError as exc:
            logger.warning(f"Connection error calling chat model {target_model}: {exc}")
            raise APIConnectionError(f"Connection error with {url}") from exc

        self._map_http_error(response)

        data = response.json()
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"Chat completion done ({target_model}) in {duration_ms}ms",
            extra={"duration_ms": duration_ms, "stage": "chat_complete"},
        )

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ModelResponseError(f"Unexpected chat response format: {data}") from exc

    async def stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = 2048,
    ) -> AsyncGenerator[str, None]:
        """Execute a streaming chat completion yielding content deltas."""
        target_model = model or settings.model_chat
        payload: dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        url = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST", url, headers=self.headers, json=payload
                ) as response:
                    self._map_http_error(response)
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
        except httpx.TimeoutException as exc:
            raise APITimeoutError(f"Stream timeout with {url}") from exc
        except httpx.RequestError as exc:
            raise APIConnectionError(f"Stream connection error with {url}") from exc


chat_client = ChatClient()
