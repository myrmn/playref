"""In-memory metrics collector and observability engine for PlayRef."""

import os
import threading
import time
from collections import deque
from typing import Any

try:
    import psutil
except ImportError:
    psutil = None

try:
    import tiktoken

    _enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    _enc = None


def count_tokens(text: str) -> int:
    """Accurately count tokens using cl100k_base, with fallback to character heuristic."""
    if not text:
        return 0
    if _enc is not None:
        try:
            return len(_enc.encode(text))
        except Exception:
            pass
    # Rough fallback: ~4 characters per token
    return max(1, len(text) // 4)


class MetricsCollector:
    """Thread-safe collector for request timings, cache hits, token usage, and system memory."""

    def __init__(self, max_history: int = 1000):
        self._lock = threading.RLock()
        self.max_history = max_history

        # Latency series per stage (in milliseconds)
        self.stage_latencies: dict[str, deque[float]] = {
            "router": deque(maxlen=max_history),
            "rewrite": deque(maxlen=max_history),
            "embed": deque(maxlen=max_history),
            "retrieve": deque(maxlen=max_history),
            "rerank": deque(maxlen=max_history),
            "generate": deque(maxlen=max_history),
            "ttft": deque(maxlen=max_history),
            "total": deque(maxlen=max_history),
        }

        # Cache counters
        self.cache_hits_exact = 0
        self.cache_hits_semantic = 0
        self.cache_misses = 0

        # Embedding / Fallback counters
        self.embedding_api_calls = 0
        self.embedding_api_failures = 0
        self.fallback_activations = 0

        # Token counters
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

        # Request status
        self.total_requests = 0
        self.successful_requests = 0
        self.error_requests = 0

        # System memory tracking
        self.peak_rss_bytes = 0

        # Detailed recent request logs
        self.recent_requests: deque[dict[str, Any]] = deque(maxlen=50)

    def _read_rss_bytes(self) -> int:
        rss_bytes = 0
        if psutil is not None:
            try:
                rss_bytes = psutil.Process().memory_info().rss
            except Exception:
                pass
        return rss_bytes

    def get_process_rss_mb(self) -> float:
        """Return current process RSS in Megabytes."""
        rss_bytes = self._read_rss_bytes()
        with self._lock:
            if rss_bytes > self.peak_rss_bytes:
                self.peak_rss_bytes = rss_bytes
        return round(rss_bytes / (1024 * 1024), 2)

    def get_peak_rss_mb(self) -> float:
        """Return peak process RSS observed so far in Megabytes."""
        with self._lock:
            rss_bytes = self._read_rss_bytes()
            if rss_bytes > self.peak_rss_bytes:
                self.peak_rss_bytes = rss_bytes
            return round(self.peak_rss_bytes / (1024 * 1024), 2)

    def record_cache_hit(self, hit_type: str = "exact") -> None:
        with self._lock:
            if hit_type == "exact":
                self.cache_hits_exact += 1
            elif hit_type == "semantic":
                self.cache_hits_semantic += 1

    def record_cache_miss(self) -> None:
        with self._lock:
            self.cache_misses += 1

    def record_embedding_event(self, event_type: str) -> None:
        with self._lock:
            if event_type == "api_call":
                self.embedding_api_calls += 1
            elif event_type == "api_failure":
                self.embedding_api_failures += 1
            elif event_type == "fallback_activation":
                self.fallback_activations += 1

    def record_tokens(self, prompt_tokens: int, completion_tokens: int) -> None:
        with self._lock:
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens

    def record_request(
        self,
        request_id: str,
        stage_timings: dict[str, float],
        cache_hit: str = "none",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        embedding_event: str | None = None,
        status_code: int = 200,
        error: str | None = None,
    ) -> None:
        current_rss = self.get_process_rss_mb()

        with self._lock:
            self.total_requests += 1
            if 200 <= status_code < 400:
                self.successful_requests += 1
            else:
                self.error_requests += 1

            for stage, duration in stage_timings.items():
                if stage in self.stage_latencies:
                    self.stage_latencies[stage].append(duration)

            if cache_hit == "exact":
                self.cache_hits_exact += 1
            elif cache_hit == "semantic":
                self.cache_hits_semantic += 1
            elif cache_hit == "miss":
                self.cache_misses += 1

            if embedding_event == "api_call":
                self.embedding_api_calls += 1
            elif embedding_event == "api_failure":
                self.embedding_api_failures += 1
            elif embedding_event == "fallback_activation":
                self.fallback_activations += 1

            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens

            summary = {
                "request_id": request_id,
                "timestamp": time.time(),
                "status_code": status_code,
                "cache_hit": cache_hit,
                "total_ms": stage_timings.get("total", 0.0),
                "ttft_ms": stage_timings.get("ttft"),
                "stage_timings": stage_timings,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "rss_mb": current_rss,
                "error": error,
            }
            self.recent_requests.append(summary)

    @staticmethod
    def _percentile(values: list[float], pct: float) -> float:
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * (pct / 100.0))
        idx = min(idx, len(sorted_vals) - 1)
        return round(sorted_vals[idx], 2)

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            total_cache_queries = (
                self.cache_hits_exact + self.cache_hits_semantic + self.cache_misses
            )
            cache_hit_rate = (
                round(
                    ((self.cache_hits_exact + self.cache_hits_semantic) / total_cache_queries)
                    * 100,
                    2,
                )
                if total_cache_queries > 0
                else 0.0
            )

            latency_stats = {}
            for stage, queue in self.stage_latencies.items():
                vals = list(queue)
                if vals:
                    latency_stats[stage] = {
                        "count": len(vals),
                        "min_ms": round(min(vals), 2),
                        "max_ms": round(max(vals), 2),
                        "avg_ms": round(sum(vals) / len(vals), 2),
                        "p50_ms": self._percentile(vals, 50),
                        "p95_ms": self._percentile(vals, 95),
                        "p99_ms": self._percentile(vals, 99),
                    }
                else:
                    latency_stats[stage] = {
                        "count": 0,
                        "min_ms": 0.0,
                        "max_ms": 0.0,
                        "avg_ms": 0.0,
                        "p50_ms": 0.0,
                        "p95_ms": 0.0,
                        "p99_ms": 0.0,
                    }

            rss_bytes = self._read_rss_bytes()
            if rss_bytes > self.peak_rss_bytes:
                self.peak_rss_bytes = rss_bytes
            current_rss = round(rss_bytes / (1024 * 1024), 2)
            peak_rss = round(self.peak_rss_bytes / (1024 * 1024), 2)

            return {
                "system": {
                    "current_rss_mb": current_rss,
                    "peak_rss_mb": peak_rss,
                    "pid": os.getpid(),
                },
                "requests": {
                    "total": self.total_requests,
                    "successful": self.successful_requests,
                    "error": self.error_requests,
                    "error_rate_pct": (
                        round((self.error_requests / self.total_requests) * 100, 2)
                        if self.total_requests > 0
                        else 0.0
                    ),
                },
                "cache": {
                    "exact_hits": self.cache_hits_exact,
                    "semantic_hits": self.cache_hits_semantic,
                    "misses": self.cache_misses,
                    "total_lookups": total_cache_queries,
                    "hit_rate_pct": cache_hit_rate,
                },
                "embedding": {
                    "api_calls": self.embedding_api_calls,
                    "api_failures": self.embedding_api_failures,
                    "fallback_activations": self.fallback_activations,
                },
                "tokens": {
                    "total_prompt_tokens": self.total_prompt_tokens,
                    "total_completion_tokens": self.total_completion_tokens,
                    "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
                    "avg_tokens_per_request": (
                        round(
                            (self.total_prompt_tokens + self.total_completion_tokens)
                            / max(1, self.successful_requests),
                            1,
                        )
                    ),
                },
                "latencies": latency_stats,
                "recent_requests": list(self.recent_requests)[-10:],
            }

    def reset(self) -> None:
        """Reset counters and latency series (useful for benchmarks/tests)."""
        with self._lock:
            for queue in self.stage_latencies.values():
                queue.clear()
            self.cache_hits_exact = 0
            self.cache_hits_semantic = 0
            self.cache_misses = 0
            self.embedding_api_calls = 0
            self.embedding_api_failures = 0
            self.fallback_activations = 0
            self.total_prompt_tokens = 0
            self.total_completion_tokens = 0
            self.total_requests = 0
            self.successful_requests = 0
            self.error_requests = 0
            self.recent_requests.clear()


metrics_collector = MetricsCollector()
