"""Command-line interface for PlayRef RAG Assistant."""

import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from backend.app.config import settings
from backend.app.rag.generate import generator
from backend.app.rag.rerank import reranker_service
from backend.app.rag.retrieve import retriever

app = typer.Typer(help="PlayRef Football Laws of the Game CLI")
console = Console()


async def ask_pipeline(
    query: str,
    debug: bool = False,
    law_filter: int | None = None,
    language: str = "en",
):
    total_start = time.perf_counter()

    # 1. Hybrid Retrieval
    t0 = time.perf_counter()
    candidates = await retriever.retrieve(
        query=query,
        top_k=settings.retrieve_top_k,
        law_number_filter=law_filter,
    )
    retrieve_ms = round((time.perf_counter() - t0) * 1000, 1)

    # 2. Cross-Encoder Rerank
    t1 = time.perf_counter()
    reranked = await reranker_service.rerank(
        query=query,
        candidates=candidates,
        top_k=settings.rerank_top_k,
    )
    rerank_ms = round((time.perf_counter() - t1) * 1000, 1)

    # 3. Grounded Generation
    t2 = time.perf_counter()
    answer = await generator.generate(
        query=query,
        scored_chunks=reranked,
        language=language,
    )
    generate_ms = round((time.perf_counter() - t2) * 1000, 1)
    total_ms = round((time.perf_counter() - total_start) * 1000, 1)

    # Output Presentation
    console.print()
    console.print(Panel(f"[bold cyan]QUESTION:[/bold cyan] {query}", border_style="cyan"))

    console.print(
        Panel(
            f"[bold white]{answer.short_answer}[/bold white]",
            title="[bold green]Short Answer[/bold green]",
            border_style="green",
        )
    )

    if answer.applicable_laws:
        table = Table(title="Applicable Laws & Official Citations", show_header=True)
        table.add_column("Citation", style="bold yellow")
        table.add_column("Chunk ID", style="dim")
        table.add_column("Rule Quote / Summary", style="white")

        for law in answer.applicable_laws:
            table.add_row(law.citation, law.chunk_id, law.quote_or_summary)
        console.print(table)
    else:
        console.print(
            "[dim italic]No specific applicable laws cited in retrieved context.[/dim italic]"
        )

    if answer.interpretations:
        console.print(
            "\n[bold magenta]Possible Interpretations & Referee Discretion:[/bold magenta]"
        )
        for item in answer.interpretations:
            console.print(f" • {item}")

    if answer.what_would_change_the_decision:
        console.print("\n[bold yellow]What Would Change the Decision / Restart:[/bold yellow]")
        for item in answer.what_would_change_the_decision:
            console.print(f" • {item}")

    if answer.assumptions:
        console.print("\n[bold blue]Assumptions Made:[/bold blue]")
        for item in answer.assumptions:
            console.print(f" • {item}")

    if answer.needs_more_info and answer.clarifying_question:
        console.print(
            Panel(
                f"[bold red]Clarifying Question:[/bold red] {answer.clarifying_question}",
                border_style="red",
            )
        )

    # Debug Panel
    if debug:
        console.print("\n" + "=" * 70)
        console.print("[bold cyan]DEBUG PIPELINE DETAILS[/bold cyan]")
        console.print(
            f"Timing: Retrieval: [bold]{retrieve_ms}ms[/bold] | Rerank: [bold]{rerank_ms}ms[/bold] | Generate: [bold]{generate_ms}ms[/bold] | Total: [bold]{total_ms}ms[/bold]"
        )

        d_table = Table(title="Top Retrieved & Reranked Context Chunks", show_header=True)
        d_table.add_column("Rank", justify="right")
        d_table.add_column("Chunk ID", style="cyan")
        d_table.add_column("Law", justify="right")
        d_table.add_column("Section Path")
        d_table.add_column("Score", justify="right")
        d_table.add_column("Tokens", justify="right")

        for i, sc in enumerate(reranked, 1):
            c = sc.chunk
            d_table.add_row(
                str(i),
                c.chunk_id,
                f"Law {c.law_number}",
                c.section_path,
                str(sc.score),
                str(c.token_count),
            )
        console.print(d_table)


@app.command()
def main(
    query: str = typer.Argument(..., help="The football rule question to ask"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Display timing and chunk scores"),
    law: int | None = typer.Option(None, "--law", "-l", help="Filter retrieval by Law number"),
    lang: str = typer.Option("en", "--lang", help="Answer language"),
):
    """Ask a question about the IFAB Laws of the Game."""
    asyncio.run(ask_pipeline(query=query, debug=debug, law_filter=law, language=lang))


if __name__ == "__main__":
    app()
