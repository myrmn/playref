"""Load testing and baseline benchmarking script for PlayRef.

Replays queries from eval/golden.jsonl with configurable concurrency and repeats,
measuring end-to-end latency, stage breakdown, token usage, cache hit rate, and peak RSS.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def load_dataset(path: str, count: int = 50) -> list[dict[str, Any]]:
    """Load queries from golden.jsonl with simulated repeats."""
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = root_dir / path

    if not file_path.exists():
        print(f"Error: Dataset file not found at {file_path}")
        sys.exit(1)

    items = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))

    if not items:
        print("Error: Dataset is empty")
        sys.exit(1)

    # Replay pattern: take distinct questions, then mix in repeats
    # For count=50: 35 distinct + 15 repeats of the top 10 questions
    base_count = min(len(items), int(count * 0.7))
    repeat_count = count - base_count

    selected = items[:base_count]
    repeats = [items[i % min(10, len(items))] for i in range(repeat_count)]
    combined = selected + repeats
    return combined[:count]


def percentile(vals: list[float], pct: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    idx = int(len(s) * (pct / 100.0))
    idx = min(idx, len(s) - 1)
    return round(s[idx], 2)


async def send_request(
    client: httpx.AsyncClient,
    base_url: str,
    query_item: dict[str, Any],
    sem: asyncio.Semaphore,
    stream: bool = False,
) -> dict[str, Any]:
    question = query_item.get("question", "")
    lang = query_item.get("lang", "en")

    payload = {
        "query": question,
        "language": lang,
        "stream": stream,
    }

    async with sem:
        t0 = time.perf_counter()
        status_code = 0
        error = None
        ttft = None

        try:
            if stream:
                async with client.stream(
                    "POST",
                    f"{base_url}/chat",
                    json=payload,
                    timeout=60.0,
                ) as resp:
                    status_code = resp.status_code
                    async for chunk in resp.aiter_text():
                        if ttft is None and "event: delta" in chunk:
                            ttft = round((time.perf_counter() - t0) * 1000, 2)
            else:
                resp = await client.post(
                    f"{base_url}/chat",
                    json=payload,
                    timeout=60.0,
                )
                status_code = resp.status_code
        except Exception as exc:
            error = str(exc)
            status_code = 500

        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        if ttft is None:
            ttft = total_ms

        return {
            "question": question[:40],
            "lang": lang,
            "status_code": status_code,
            "total_ms": total_ms,
            "ttft_ms": ttft,
            "error": error,
        }


async def run_benchmark(
    base_url: str,
    golden_path: str,
    num_requests: int,
    concurrency: int,
    stream: bool,
    admin_key: str,
    reset_stats: bool = True,
    in_process: bool = False,
) -> dict[str, Any]:
    queries = load_dataset(golden_path, num_requests)
    headers = {"X-Admin-Key": admin_key}

    transport = None
    if in_process:
        from backend.app.main import app
        transport = httpx.ASGITransport(app=app)
        base_url = "http://test"

    async with httpx.AsyncClient(transport=transport, timeout=30.0) as admin_client:
        # Check health
        try:
            h_resp = await admin_client.get(f"{base_url}/health")
            if h_resp.status_code != 200:
                print(f"Server health check failed: {h_resp.status_code} {h_resp.text}")
                sys.exit(1)
        except Exception as exc:
            print(f"Could not connect to {base_url}/health: {exc}")
            print("Please ensure the backend server is running (e.g. uvicorn backend.app.main:app) or run with --in-process.")
            sys.exit(1)

        # Reset server stats if requested
        if reset_stats:
            await admin_client.post(f"{base_url}/admin/stats/reset", headers=headers)

        # Fetch initial stats
        pre_stats_resp = await admin_client.get(f"{base_url}/admin/stats", headers=headers)
        pre_stats = pre_stats_resp.json() if pre_stats_resp.status_code == 200 else {}

    print(f"\n==================================================================")
    print(f"  PLAYREF LOAD TEST & BASELINE BENCHMARK")
    print(f"==================================================================")
    print(f"  Target URL:        {base_url} {'(In-Process ASGI)' if in_process else '(External HTTP)'}")
    print(f"  Dataset:           {golden_path} ({len(queries)} queries)")
    print(f"  Concurrency:       {concurrency}")
    print(f"  Stream mode:       {stream}")
    print(f"  Initial RSS:       {pre_stats.get('system', {}).get('current_rss_mb', 'N/A')} MB")
    print(f"==================================================================\n")

    sem = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(max_connections=concurrency * 2, max_keepalive_connections=concurrency)

    t_start = time.perf_counter()
    async with httpx.AsyncClient(transport=transport, limits=limits) as test_client:
        tasks = [
            send_request(test_client, base_url, q, sem, stream=stream)
            for q in queries
        ]
        results = await asyncio.gather(*tasks)

    elapsed_wall = round(time.perf_counter() - t_start, 2)

    # Fetch post-test server metrics
    async with httpx.AsyncClient(transport=transport, timeout=30.0) as admin_client:
        post_stats_resp = await admin_client.get(f"{base_url}/admin/stats", headers=headers)
        server_stats = post_stats_resp.json() if post_stats_resp.status_code == 200 else {}

    # Client-side calculations
    latencies = [r["total_ms"] for r in results]
    ttfts = [r["ttft_ms"] for r in results]
    errors = [r for r in results if r["status_code"] != 200]
    error_rate = round((len(errors) / len(results)) * 100, 2)

    p50_total = percentile(latencies, 50)
    p95_total = percentile(latencies, 95)
    p99_total = percentile(latencies, 99)
    avg_total = round(sum(latencies) / len(latencies), 2)
    min_total = round(min(latencies), 2)
    max_total = round(max(latencies), 2)

    p50_ttft = percentile(ttfts, 50)
    p95_ttft = percentile(ttfts, 95)

    sys_info = server_stats.get("system", {})
    cache_info = server_stats.get("cache", {})
    token_info = server_stats.get("tokens", {})
    server_lats = server_stats.get("latencies", {})

    print("\n------------------- LOAD TEST RESULTS -------------------")
    print(f"Total Requests:     {len(results)}")
    print(f"Successful:         {len(results) - len(errors)}")
    print(f"Failed:             {len(errors)} ({error_rate}% error rate)")
    print(f"Total Wall Clock:   {elapsed_wall}s ({round(len(results) / elapsed_wall, 2)} req/s)")
    print(f"\n--- CLIENT LATENCIES (ms) ---")
    print(f"Min: {min_total} ms | Max: {max_total} ms | Avg: {avg_total} ms")
    print(f"p50: {p50_total} ms | p95: {p95_total} ms | p99: {p99_total} ms")
    print(f"TTFT p50: {p50_ttft} ms | TTFT p95: {p95_ttft} ms")

    print(f"\n--- SERVER STAGE BREAKDOWN (ms) ---")
    for stage in ["router", "rewrite", "embed", "retrieve", "rerank", "generate"]:
        info = server_lats.get(stage, {})
        print(
            f"  {stage.capitalize():<10} p50: {info.get('p50_ms', 0):>7} ms | "
            f"p95: {info.get('p95_ms', 0):>7} ms | "
            f"avg: {info.get('avg_ms', 0):>7} ms"
        )

    print(f"\n--- MEMORY & SYSTEM ---")
    print(f"  Current RSS:      {sys_info.get('current_rss_mb', 'N/A')} MB")
    print(f"  Peak RSS:         {sys_info.get('peak_rss_mb', 'N/A')} MB")

    print(f"\n--- CACHE PERFORMANCE ---")
    print(f"  Exact Hits:       {cache_info.get('exact_hits', 0)}")
    print(f"  Semantic Hits:    {cache_info.get('semantic_hits', 0)}")
    print(f"  Misses:           {cache_info.get('misses', 0)}")
    print(f"  Hit Rate:         {cache_info.get('hit_rate_pct', 0)}%")

    print(f"\n--- TOKEN USAGE ---")
    print(f"  Total Tokens:     {token_info.get('total_tokens', 0)}")
    print(f"  Prompt Tokens:    {token_info.get('total_prompt_tokens', 0)}")
    print(f"  Completion Toks:  {token_info.get('total_completion_tokens', 0)}")
    print(f"  Avg Toks/Req:     {token_info.get('avg_tokens_per_request', 0)}")
    print("---------------------------------------------------------\n")

    return {
        "wall_clock_s": elapsed_wall,
        "total_requests": len(results),
        "error_rate_pct": error_rate,
        "client_latencies": {
            "min_ms": min_total,
            "max_ms": max_total,
            "avg_ms": avg_total,
            "p50_ms": p50_total,
            "p95_ms": p95_total,
            "p99_ms": p99_total,
            "ttft_p50_ms": p50_ttft,
            "ttft_p95_ms": p95_ttft,
        },
        "server_stats": server_stats,
    }


def main():
    parser = argparse.ArgumentParser(description="PlayRef Load Testing Tool")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API base URL")
    parser.add_argument(
        "--golden-path", default="eval/golden.jsonl", help="Path to golden.jsonl"
    )
    parser.add_argument(
        "--num-requests", type=int, default=50, help="Number of requests to replay"
    )
    parser.add_argument(
        "--concurrency", type=int, default=2, help="Concurrency level"
    )
    parser.add_argument(
        "--stream", action="store_true", help="Send requests with stream=True"
    )
    parser.add_argument(
        "--admin-key", default="playref-admin-secret", help="Admin API Key"
    )
    parser.add_argument(
        "--no-reset", action="store_true", help="Do not reset server stats before run"
    )
    parser.add_argument(
        "--in-process", action="store_true", help="Run directly against ASGI app in-process"
    )
    args = parser.parse_args()

    asyncio.run(
        run_benchmark(
            base_url=args.base_url.rstrip("/"),
            golden_path=args.golden_path,
            num_requests=args.num_requests,
            concurrency=args.concurrency,
            stream=args.stream,
            admin_key=args.admin_key,
            reset_stats=not args.no_reset,
            in_process=args.in_process,
        )
    )


if __name__ == "__main__":
    main()
