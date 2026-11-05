"""Data models for ingestion and chunking."""

from pydantic import BaseModel, Field


class LawChunk(BaseModel):
    chunk_id: str
    law_number: int
    law_title: str
    section_path: str
    edition: str = "2026/27"
    page: int
    source: str = "IFAB Laws of the Game"
    lang: str = "en"
    parent_id: str | None = None
    page_images: list[int] = Field(default_factory=list)
    clean_text: str  # Original text for display & citation
    text_for_embedding: str  # Section path prepended to text
    token_count: int = 0
