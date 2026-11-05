"""Citation validation and Answer models for PlayRef."""

import re

from pydantic import BaseModel, Field

from backend.app.ingestion.models import LawChunk
from backend.app.logger import logger


class ApplicableLaw(BaseModel):
    citation: str = Field(description="e.g. Law 12 - Handball")
    chunk_id: str = Field(description="Exact chunk_id from retrieved context")
    quote_or_summary: str = Field(description="Direct quote or summary of relevant rule")


class PlayRefAnswer(BaseModel):
    short_answer: str = Field(description="Direct, concise summary of the situation")
    applicable_laws: list[ApplicableLaw] = Field(default_factory=list)
    interpretations: list[str] = Field(
        default_factory=list, description="Possible interpretations and referee discretion points"
    )
    what_would_change_the_decision: list[str] = Field(
        default_factory=list, description="Factors that would alter the sanction or restart"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Assumptions made about the situation"
    )
    needs_more_info: bool = Field(default=False)
    clarifying_question: str | None = Field(default=None)
    language: str = Field(default="en")


class CitationValidator:
    """Validates citations against the retrieved chunks set.

    Product rules:
    - No law number may appear in a citation unless it exists in the retrieved context.
    - Every chunk_id must match a chunk in the retrieved set; otherwise strip it.
    """

    @staticmethod
    def validate(answer: PlayRefAnswer, retrieved_chunks: list[LawChunk]) -> PlayRefAnswer:
        valid_chunk_ids = {c.chunk_id for c in retrieved_chunks}
        valid_law_numbers = {c.law_number for c in retrieved_chunks}

        validated_laws: list[ApplicableLaw] = []

        for law in answer.applicable_laws:
            # 1. Validate chunk_id
            if law.chunk_id not in valid_chunk_ids:
                logger.warning(
                    f"Citation validation dropped invalid chunk_id: '{law.chunk_id}' (not in retrieved set)"
                )
                continue

            # 2. Validate law number mentioned in citation text
            m = re.search(r"Law\s*(\d+)", law.citation, re.IGNORECASE)
            if m:
                cited_law_num = int(m.group(1))
                if cited_law_num not in valid_law_numbers:
                    logger.warning(
                        f"Citation validation dropped hallucinated Law {cited_law_num}: not in retrieved context laws {valid_law_numbers}"
                    )
                    continue

            validated_laws.append(law)

        answer.applicable_laws = validated_laws
        return answer
