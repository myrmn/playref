"""Unit tests for QueryRouter."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.app.rag.router import QueryRouter


@pytest.mark.asyncio
async def test_router_valid_classification():
    router = QueryRouter()
    mock_json = """{
        "intent": "rules_question",
        "lang": "fr",
        "is_off_topic": false,
        "redirect_message": null
    }"""
    with patch(
        "backend.app.rag.router.chat_client.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = mock_json
        result = await router.route("Quelle est la règle du hors-jeu ?")

        assert result.intent == "rules_question"
        assert result.lang == "fr"
        assert result.is_off_topic is False


@pytest.mark.asyncio
async def test_router_off_topic_redirect():
    router = QueryRouter()
    mock_json = """{
        "intent": "off_topic",
        "lang": "en",
        "is_off_topic": true,
        "redirect_message": "I only answer football rules."
    }"""
    with patch(
        "backend.app.rag.router.chat_client.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = mock_json
        result = await router.route("How do I bake bread?")

        assert result.intent == "off_topic"
        assert result.is_off_topic is True
        assert "football" in result.redirect_message.lower()


@pytest.mark.asyncio
async def test_router_fallback_on_malformed_json():
    router = QueryRouter()
    with patch(
        "backend.app.rag.router.chat_client.complete", new_callable=AsyncMock
    ) as mock_complete:
        mock_complete.return_value = "Non-json string"
        result = await router.route("Any question")

        # Graceful fallback check
        assert result.intent == "scenario"
        assert result.lang == "en"
        assert result.is_off_topic is False
