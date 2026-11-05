"""Unit tests for RAG pipeline, reranker fallback, and JSON parsing."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.app.ingestion.models import LawChunk
from backend.app.rag.generate import GroundedGenerator
from backend.app.rag.rerank import RerankerService
from backend.app.rag.retrieve import ScoredChunk


@pytest.fixture
def sample_candidates():
    chunks = [
        LawChunk(
            chunk_id=f"chunk-{i}",
            law_number=12,
            law_title="Fouls and Misconduct",
            section_path="1. Direct free kick",
            page=100 + i,
            clean_text=f"Rule text {i}",
            text_for_embedding=f"Embedding text {i}",
        )
        for i in range(10)
    ]
    return [
        ScoredChunk(chunk=c, score=1.0 / (i + 1), retrieval_method="rrf")
        for i, c in enumerate(chunks)
    ]


@pytest.mark.asyncio
async def test_reranker_fallback_on_failure(sample_candidates):
    service = RerankerService(top_k=5)

    with patch(
        "backend.app.rag.rerank.rerank_client.rerank", new_callable=AsyncMock
    ) as mock_rerank:
        mock_rerank.side_effect = Exception("API connection failure")

        reranked = await service.rerank(query="test", candidates=sample_candidates, top_k=5)
        # Verify graceful degradation to top 5 candidates in original order
        assert len(reranked) == 5
        assert reranked[0].chunk.chunk_id == "chunk-0"
        assert reranked[4].chunk.chunk_id == "chunk-4"


@pytest.mark.asyncio
async def test_generator_json_parse_and_retry():
    generator = GroundedGenerator()
    chunk = LawChunk(
        chunk_id="chunk-1",
        law_number=11,
        law_title="Offside",
        section_path="1. Offside position",
        page=109,
        clean_text="It is not an offence to be in an offside position.",
        text_for_embedding="Offside",
    )
    scored = [ScoredChunk(chunk=chunk, score=0.9)]

    # Mock chat_client to return invalid JSON first, then valid JSON on retry
    valid_json = """{
        "short_answer": "Being in an offside position is not an offence.",
        "applicable_laws": [{"citation": "Law 11 - Offside", "chunk_id": "chunk-1", "quote_or_summary": "Not an offence"}],
        "interpretations": [],
        "what_would_change_the_decision": [],
        "assumptions": [],
        "needs_more_info": false,
        "clarifying_question": null,
        "language": "en"
    }"""

    with patch(
        "backend.app.rag.generate.chat_client.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.side_effect = ["Invalid json string", valid_json]

        answer = await generator.generate(query="Is being offside a foul?", scored_chunks=scored)
        assert mock_complete.call_count == 2
        assert "not an offence" in answer.short_answer.lower()
        assert len(answer.applicable_laws) == 1
        assert answer.applicable_laws[0].chunk_id == "chunk-1"
