"""Structure-aware chunking for PlayRef."""

import re

import tiktoken

from backend.app.config import settings
from backend.app.ingestion.models import LawChunk
from backend.app.ingestion.parser import RawSection


def clean_str(text: str) -> str:
    """Normalize unicode whitespace and invisible characters."""
    text = text.replace("\u2002", " ").replace("\u2003", " ").replace("\x07", "")
    text = text.replace("\t", " ")
    text = re.sub(r" +", " ", text)
    return text.strip()


def slugify(text: str) -> str:
    """Create a URL/ID safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


class LawChunker:
    """Splits RawSections into 200-500 token chunks respecting section boundaries."""

    def __init__(
        self,
        min_tokens: int = 150,
        max_tokens: int = 500,
        edition: str = settings.laws_edition,
    ):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.edition = edition
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def chunk_section(self, section: RawSection) -> list[LawChunk]:
        """Convert a single RawSection into one or more LawChunks."""
        clean_paragraphs = [clean_str(p) for p in section.paragraphs if clean_str(p)]
        if not clean_paragraphs:
            return []

        # Determine section slug for chunk_id
        sec_num_slug = f"s{section.section_number}"
        sub_slug = slugify(section.sub_section) if section.sub_section else ""
        if sub_slug:
            base_id = f"law{section.law_number}-{sec_num_slug}-{sub_slug}"
        else:
            base_id = f"law{section.law_number}-{sec_num_slug}"

        # Combine paragraphs into chunks adhering to max_tokens
        chunks: list[LawChunk] = []
        current_paragraphs: list[str] = []
        current_tokens = 0
        chunk_idx = 1

        for para in clean_paragraphs:
            p_tokens = self.count_tokens(para)

            if current_tokens + p_tokens > self.max_tokens and current_paragraphs:
                # Flush current chunk
                chunk_text = "\n\n".join(current_paragraphs)
                token_count = self.count_tokens(chunk_text)
                chunk_id = f"{base_id}-{chunk_idx:03d}"
                text_for_embedding = f"{section.law_title} > {section.section_path}\n\n{chunk_text}"

                chunks.append(
                    LawChunk(
                        chunk_id=chunk_id,
                        law_number=section.law_number,
                        law_title=section.law_title,
                        section_path=section.section_path,
                        edition=self.edition,
                        page=section.page,
                        source="IFAB Laws of the Game",
                        lang="en",
                        parent_id=section.parent_id,
                        page_images=section.page_images,
                        clean_text=chunk_text,
                        text_for_embedding=text_for_embedding,
                        token_count=token_count,
                    )
                )
                chunk_idx += 1
                current_paragraphs = [para]
                current_tokens = p_tokens
            else:
                current_paragraphs.append(para)
                current_tokens += p_tokens

        # Flush final chunk
        if current_paragraphs:
            chunk_text = "\n\n".join(current_paragraphs)
            token_count = self.count_tokens(chunk_text)
            chunk_id = f"{base_id}-{chunk_idx:03d}"
            text_for_embedding = f"{section.law_title} > {section.section_path}\n\n{chunk_text}"

            chunks.append(
                LawChunk(
                    chunk_id=chunk_id,
                    law_number=section.law_number,
                    law_title=section.law_title,
                    section_path=section.section_path,
                    edition=self.edition,
                    page=section.page,
                    source="IFAB Laws of the Game",
                    lang="en",
                    parent_id=section.parent_id,
                    page_images=section.page_images,
                    clean_text=chunk_text,
                    text_for_embedding=text_for_embedding,
                    token_count=token_count,
                )
            )

        return chunks

    def chunk_all(self, sections: list[RawSection]) -> list[LawChunk]:
        """Process all raw sections into chunks."""
        all_chunks: list[LawChunk] = []
        for sec in sections:
            all_chunks.extend(self.chunk_section(sec))
        return all_chunks
