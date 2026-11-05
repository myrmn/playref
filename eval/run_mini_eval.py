"""Mini evaluation runner for PlayRef RAG retrieval & rerank pipeline."""

import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.table import Table

from backend.app.rag.rerank import reranker_service
from backend.app.rag.retrieve import retriever

console = Console()


async def run_eval(eval_path: str = "eval/mini_eval.jsonl", top_k: int = 6):
    console.print("[bold cyan]Running PlayRef Mini Evaluation (20 Questions)[/bold cyan]")
    console.print(f"Dataset: {eval_path} | Target: Recall@{top_k}")
    console.print("-" * 65)

    with open(eval_path, encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]

    passed = 0
    total = len(items)

    table = Table(title=f"Mini Eval Results (Recall@{top_k})", show_header=True)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Question", style="white", max_width=45)
    table.add_column("Expected", justify="center", style="yellow")
    table.add_column(f"Top {top_k} Laws", style="dim")
    table.add_column("Status", justify="center", style="bold")
    table.add_column("Time", justify="right")

    for item in items:
        qid = item["id"]
        query = item["query"]
        expected = item["expected_laws"]

        start = time.perf_counter()
        candidates = await retriever.retrieve(query=query, top_k=30)
        reranked = await reranker_service.rerank(query=query, candidates=candidates, top_k=top_k)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

        retrieved_laws = [sc.chunk.law_number for sc in reranked]
        # Check if at least one expected law is in top_k
        is_hit = any(exp in retrieved_laws for exp in expected)

        if is_hit:
            passed += 1
            status = "[green]PASS[/green]"
        else:
            status = "[red]FAIL[/red]"

        table.add_row(
            str(qid),
            query,
            str(expected),
            str(retrieved_laws),
            status,
            f"{elapsed_ms}ms",
        )

    console.print(table)
    recall_pct = round((passed / total) * 100, 1)
    console.print("-" * 65)
    console.print(
        f"Evaluation Summary: [bold]{passed}/{total}[/bold] passed -> [bold green]Recall@{top_k} = {recall_pct}%[/bold green]"
    )
    return passed, total, recall_pct


if __name__ == "__main__":
    asyncio.run(run_eval())
