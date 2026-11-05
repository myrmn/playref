"""Unit tests for QueryRewriter."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.app.rag.rewrite import QueryRewriter


@pytest.mark.asyncio
async def test_rewrite_follow_up():
    rewriter = QueryRewriter()
    mock_json = """{
        "standalone_query": "What is the restart if handball occurs outside the penalty box?",
        "keywords": ["handball", "penalty box", "outside", "direct free kick"],
        "law_hint": 12
    }"""
    with patch(
        "backend.app.rag.rewrite.chat_client.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = mock_json

        history = [
            {
                "role": "user",
                "content": "What happens if a defender deliberately handles the ball?",
            },
            {
                "role": "assistant",
                "content": "If inside the penalty area, a penalty kick is awarded.",
            },
        ]

        result = await rewriter.rewrite(query="What if it was outside the box?", history=history)

        assert "handball" in result.standalone_query.lower()
        assert "outside" in result.standalone_query.lower()
        assert result.law_hint == 12
        assert len(result.keywords) >= 3


@pytest.mark.asyncio
async def test_rewrite_multilingual_translation():
    rewriter = QueryRewriter()
    mock_json = """{
        "standalone_query": "Can a goal be scored directly from a corner kick into the opponent goal?",
        "keywords": ["corner kick", "goal", "directly"],
        "law_hint": 17
    }"""
    with patch(
        "backend.app.rag.rewrite.chat_client.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = mock_json

        result = await rewriter.rewrite(query="هل يمكن تسجيل هدف مباشر من ركنية؟", history=[])

        assert "corner kick" in result.standalone_query.lower()
        assert result.law_hint == 17
