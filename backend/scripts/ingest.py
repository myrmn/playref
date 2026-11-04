"""Ingestion CLI script for IFAB Laws of the Game."""

import asyncio
import json
from pathlib import Path
import random
import sys
from typing import List

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from rich.console import Console
from rich.table import Table

from backend.app.config import settings
from backend.app.ingestion.chunker import LawChunker
from backend.app.ingestion.indexer import index_chunks
from backend.app.ingestion.models import LawChunk
from backend.app.ingestion.parser import PDFParser

console = Console()


async def run_ingestion(
    pdf_path: str = "data/raw/laws_of_the_game.pdf",
    output_jsonl: str = "data/processed/chunks.jsonl",
    recreate: bool = True,
):
    console.print(f"[bold cyan]PlayRef Laws Ingestion Pipeline[/bold cyan]")
    console.print(f"Source PDF: {pdf_path}")
    console.print(f"Laws Edition: {settings.laws_edition}")
    console.print("-" * 60)

    # 1. Parse PDF
    console.print("[yellow]1. Parsing PDF hierarchy...[/yellow]")
    parser = PDFParser(pdf_path)
    sections = parser.parse()
    console.print(f"[green]Parsed {len(sections)} sections and subsections.[/green]")

    # 2. Chunking
    console.print("[yellow]2. Generating structure-aware chunks (200-500 tokens)...[/yellow]")
    chunker = LawChunker(min_tokens=150, max_tokens=500, edition=settings.laws_edition)
    chunks = chunker.chunk_all(sections)
    console.print(f"[green]Created {len(chunks)} chunks.[/green]")

    # 3. Save to data/processed/chunks.jsonl
    out_file = Path(output_jsonl)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk.model_dump(), ensure_ascii=False) + "\n")
    console.print(f"[green]Saved chunks to {out_file}[/green]")

    # 4. Summary Statistics
    law_counts = {}
    total_tokens = 0
    for c in chunks:
        law_counts[c.law_number] = law_counts.get(c.law_number, 0) + 1
        total_tokens += c.token_count

    avg_tokens = round(total_tokens / len(chunks), 1) if chunks else 0

    table = Table(title="Ingestion Statistics", show_header=True)
    table.add_column("Law #", justify="right", style="cyan")
    table.add_column("Title / Topic", style="white")
    table.add_column("Chunks", justify="right", style="green")

    # Map titles
    law_titles = {}
    for c in chunks:
        if c.law_number not in law_titles:
            law_titles[c.law_number] = c.law_title

    for law_num in sorted(law_counts.keys()):
        title = law_titles.get(law_num, f"Law {law_num}")
        table.add_row(str(law_num), title, str(law_counts[law_num]))

    console.print(table)
    console.print(f"Total Laws / Sections: [bold]{len(law_counts)}[/bold]")
    console.print(f"Total Chunks: [bold]{len(chunks)}[/bold]")
    console.print(f"Average Tokens per Chunk: [bold]{avg_tokens}[/bold]")

    # 5. Index into Qdrant
    console.print("\n[yellow]3. Embedding and Indexing into Qdrant...[/yellow]")
    indexed_count = await index_chunks(chunks, batch_size=16, recreate=recreate)
    console.print(f"[bold green]Successfully indexed {indexed_count} chunks into Qdrant![/bold green]")

    # 6. Spot check: 10 random chunks
    console.print("\n[bold magenta]================ 10 RANDOM CHUNKS SPOT CHECK ================[/bold magenta]")
    sample_indices = sorted(random.sample(range(len(chunks)), min(10, len(chunks))))
    for i, idx in enumerate(sample_indices, 1):
        c = chunks[idx]
        console.print(f"\n[bold cyan]--- Spot Check Chunk #{i} (Index {idx}) ---[/bold cyan]")
        console.print(f"[bold]chunk_id:[/bold] {c.chunk_id}")
        console.print(f"[bold]law_number:[/bold] {c.law_number} ({c.law_title})")
        console.print(f"[bold]section_path:[/bold] {c.section_path}")
        console.print(f"[bold]parent_id:[/bold] {c.parent_id} | [bold]page:[/bold] {c.page} | [bold]tokens:[/bold] {c.token_count} | [bold]images:[/bold] {c.page_images}")
        console.print(f"[bold green]Clean text preview:[/bold green]\n{c.clean_text[:280]}...")


if __name__ == "__main__":
    asyncio.run(run_ingestion())

