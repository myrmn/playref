"""API Smoke Test for PlayRef Model Endpoints.

Verifies chat, streaming, JSON mode, embeddings, and reranking on the configured provider.
"""

import asyncio
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import httpx
from rich.console import Console
from rich.table import Table

from backend.app.config import settings

console = Console()


async def test_chat_endpoint(client: httpx.AsyncClient, model: str) -> Dict[str, Any]:
    """Test standard chat completion."""
    start = time.perf_counter()
    try:
        r = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Reply with 'OK'."}],
                "max_tokens": 10,
                "temperature": 0.0,
            },
        )
        latency = round((time.perf_counter() - start) * 1000, 1)
        if r.status_code == 200:
            data = r.json()
            content = data["choices"][0]["message"]["content"].strip()
            return {"status": "PASS", "latency_ms": latency, "detail": f"Output: '{content}'"}
        return {"status": "FAIL", "latency_ms": latency, "detail": f"HTTP {r.status_code}: {r.text[:100]}"}
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {"status": "ERROR", "latency_ms": latency, "detail": str(exc)[:100]}


async def test_chat_json_mode(client: httpx.AsyncClient, model: str) -> Dict[str, Any]:
    """Test JSON mode on chat completion."""
    start = time.perf_counter()
    try:
        r = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a JSON assistant."},
                    {"role": "user", "content": "Return a JSON object with key 'success' set to true."},
                ],
                "response_format": {"type": "json_object"},
                "max_tokens": 50,
                "temperature": 0.0,
            },
        )
        latency = round((time.perf_counter() - start) * 1000, 1)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"].strip()
            parsed = json.loads(content)
            if parsed.get("success") is True:
                return {"status": "PASS", "latency_ms": latency, "detail": "Valid JSON output verified"}
            return {"status": "PARTIAL", "latency_ms": latency, "detail": f"Parsed: {parsed}"}
        return {"status": "FAIL", "latency_ms": latency, "detail": f"HTTP {r.status_code}: {r.text[:100]}"}
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {"status": "ERROR", "latency_ms": latency, "detail": str(exc)[:100]}


async def test_chat_streaming(client: httpx.AsyncClient, model: str) -> Dict[str, Any]:
    """Test streaming generation."""
    start = time.perf_counter()
    tokens = []
    try:
        async with client.stream(
            "POST",
            "/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Count from 1 to 3."}],
                "stream": True,
                "max_tokens": 20,
            },
        ) as response:
            if response.status_code != 200:
                return {
                    "status": "FAIL",
                    "latency_ms": round((time.perf_counter() - start) * 1000, 1),
                    "detail": f"HTTP {response.status_code}",
                }
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    d = line[6:].strip()
                    if d == "[DONE]":
                        break
                    try:
                        chunk = json.loads(d)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            tokens.append(delta)
                    except Exception:
                        continue
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {
            "status": "PASS",
            "latency_ms": latency,
            "detail": f"Streamed {len(tokens)} chunks: '{''.join(tokens).strip()}'",
        }
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {"status": "ERROR", "latency_ms": latency, "detail": str(exc)[:100]}


async def test_embeddings(client: httpx.AsyncClient, model: str) -> Dict[str, Any]:
    """Test embedding endpoint, dimension, and sparse support."""
    start = time.perf_counter()
    try:
        r = await client.post(
            "/embeddings",
            json={
                "model": model,
                "input": ["Law 12 Fouls and Misconduct"],
            },
        )
        latency = round((time.perf_counter() - start) * 1000, 1)
        if r.status_code == 200:
            data = r.json()
            item = data["data"][0]
            emb = item["embedding"]
            dim = len(emb)
            has_sparse = "sparse" in item or "sparse_embedding" in item
            detail = f"Dense dim: {dim}, Sparse returned: {has_sparse}"
            return {"status": "PASS", "latency_ms": latency, "detail": detail}
        return {"status": "FAIL", "latency_ms": latency, "detail": f"HTTP {r.status_code}: {r.text[:100]}"}
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {"status": "ERROR", "latency_ms": latency, "detail": str(exc)[:100]}


async def test_rerank(client: httpx.AsyncClient, model: str) -> Dict[str, Any]:
    """Test rerank endpoint and response format."""
    start = time.perf_counter()
    try:
        r = await client.post(
            "/rerank",
            json={
                "model": model,
                "query": "What is offside?",
                "documents": [
                    "A player is in an offside position if nearer to the opponents' goal line than both the ball and second-last opponent.",
                    "Goalkeepers must wear colors distinct from outfield players.",
                ],
                "top_n": 2,
            },
        )
        latency = round((time.perf_counter() - start) * 1000, 1)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            top_score = results[0]["relevance_score"] if results else 0.0
            top_idx = results[0]["index"] if results else -1
            detail = f"Top doc idx: {top_idx} (score: {top_score:.4f}), results count: {len(results)}"
            return {"status": "PASS", "latency_ms": latency, "detail": detail}
        return {"status": "FAIL", "latency_ms": latency, "detail": f"HTTP {r.status_code}: {r.text[:100]}"}
    except Exception as exc:
        latency = round((time.perf_counter() - start) * 1000, 1)
        return {"status": "ERROR", "latency_ms": latency, "detail": str(exc)[:100]}


async def run_smoke_tests():
    console.print(f"[bold cyan]PlayRef Model Smoke Tests[/bold cyan]")
    console.print(f"Base URL: {settings.llm_base_url}")
    console.print(f"Auth Key: {'*' * 8}...{'*' * 4} (configured)")
    console.print("-" * 60)

    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    async with httpx.AsyncClient(base_url=settings.llm_base_url, headers=headers, timeout=30.0) as client:
        tests = [
            ("Chat (Main)", settings.model_chat, test_chat_endpoint(client, settings.model_chat)),
            ("Chat (Fast/Router)", settings.model_fast, test_chat_endpoint(client, settings.model_fast)),
            ("Chat (Reasoning)", settings.model_reasoning, test_chat_endpoint(client, settings.model_reasoning)),
            ("JSON Mode", settings.model_chat, test_chat_json_mode(client, settings.model_chat)),
            ("Streaming", settings.model_chat, test_chat_streaming(client, settings.model_chat)),
            ("Embeddings", settings.model_embedding, test_embeddings(client, settings.model_embedding)),
            ("Reranker", settings.model_rerank, test_rerank(client, settings.model_rerank)),
        ]

        table = Table(title="Model Smoke Test Results", show_header=True)
        table.add_column("Capability", style="bold white")
        table.add_column("Model / Endpoint", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency (ms)", justify="right")
        table.add_column("Verified Details")

        all_passed = True
        for name, model_name, coro in tests:
            res = await coro
            status_style = "green" if res["status"] == "PASS" else "red"
            if res["status"] != "PASS":
                all_passed = False
            table.add_row(
                name,
                model_name,
                f"[{status_style}]{res['status']}[/{status_style}]",
                str(res["latency_ms"]),
                res["detail"],
            )

        console.print(table)
        if all_passed:
            console.print("[bold green]All model endpoints and capabilities verified successfully![/bold green]")
        else:
            console.print("[bold red]One or more smoke tests failed![/bold red]")


if __name__ == "__main__":
    asyncio.run(run_smoke_tests())
