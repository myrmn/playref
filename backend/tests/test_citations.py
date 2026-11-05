"""Unit tests for citation validation."""

import pytest

from backend.app.ingestion.models import LawChunk
from backend.app.rag.citations import ApplicableLaw, CitationValidator, PlayRefAnswer


@pytest.fixture
def sample_retrieved_chunks():
    return [
        LawChunk(
            chunk_id="law12-s1-001",
            law_number=12,
            law_title="Fouls and Misconduct",
            section_path="1. Direct free kick",
            page=115,
            clean_text="A direct free kick is awarded if a player commits a foul.",
            text_for_embedding="Law 12 > 1. Direct free kick\n\nA direct free kick...",
        ),
        LawChunk(
            chunk_id="law16-s1-001",
            law_number=16,
            law_title="The Goal Kick",
            section_path="1. Procedure",
            page=145,
            clean_text="A goal kick is awarded when the whole of the ball passes over the goal line.",
            text_for_embedding="Law 16 > 1. Procedure\n\nA goal kick...",
        ),
    ]


def test_citation_validator_keeps_valid(sample_retrieved_chunks):
    answer = PlayRefAnswer(
        short_answer="Valid response",
        applicable_laws=[
            ApplicableLaw(
                citation="Law 12 - Direct free kick",
                chunk_id="law12-s1-001",
                quote_or_summary="Direct free kick offence",
            )
        ],
    )

    validated = CitationValidator.validate(answer, sample_retrieved_chunks)
    assert len(validated.applicable_laws) == 1
    assert validated.applicable_laws[0].chunk_id == "law12-s1-001"


def test_citation_validator_drops_invalid_chunk_id(sample_retrieved_chunks):
    answer = PlayRefAnswer(
        short_answer="Response with hallucinated chunk",
        applicable_laws=[
            ApplicableLaw(
                citation="Law 12 - Direct free kick",
                chunk_id="law12-hallucinated-999",
                quote_or_summary="Fake rule",
            ),
            ApplicableLaw(
                citation="Law 16 - Goal Kick",
                chunk_id="law16-s1-001",
                quote_or_summary="Real rule",
            ),
        ],
    )

    validated = CitationValidator.validate(answer, sample_retrieved_chunks)
    assert len(validated.applicable_laws) == 1
    assert validated.applicable_laws[0].chunk_id == "law16-s1-001"


def test_citation_validator_drops_unretrieved_law_number(sample_retrieved_chunks):
    answer = PlayRefAnswer(
        short_answer="Response citing Law 11 when only 12 and 16 were retrieved",
        applicable_laws=[
            ApplicableLaw(
                citation="Law 11 - Offside",
                chunk_id="law12-s1-001",  # Chunk is retrieved, but cited Law 11 is not in context!
                quote_or_summary="Mismatched law citation",
            )
        ],
    )

    validated = CitationValidator.validate(answer, sample_retrieved_chunks)
    assert len(validated.applicable_laws) == 0
