"""Unit tests for FastAPI endpoints."""

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


@pytest.fixture(autouse=True)
def mock_qdrant_for_api_tests(monkeypatch):
    """Mock Qdrant client to ensure hermetic unit tests."""
    mock_client = MagicMock()
    mock_points = [
        MagicMock(payload={"law_number": i, "law_title": f"Law {i} Title"})
        for i in range(1, 18)
    ]
    mock_chunk = MagicMock(
        payload={
            "chunk_id": "law12-s1-001",
            "law_number": 12,
            "law_title": "Fouls and Misconduct",
            "section_path": "1. Direct free kick > Handball",
            "page": 104,
            "edition": "2026/27",
            "clean_text": "A direct free kick is awarded if a player commits...",
        }
    )

    def fake_scroll(collection_name, scroll_filter=None, limit=100, offset=None, with_payload=True):
        if scroll_filter is not None:
            return ([mock_chunk], None)
        return (mock_points, None)

    mock_client.scroll.side_effect = fake_scroll
    mock_client.count.return_value = MagicMock(count=17)
    monkeypatch.setattr("backend.app.api.routes.get_qdrant_client", lambda: mock_client)


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "2026/27" in data["edition"]


@pytest.mark.asyncio
async def test_list_laws():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/laws")
        assert r.status_code == 200
        laws = r.json()
        assert len(laws) >= 17
        assert any(law["law_number"] == 12 for law in laws)


@pytest.mark.asyncio
async def test_get_chunk():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/chunks/law12-s1-001")
        assert r.status_code == 200
        data = r.json()
        assert data["law_number"] == 12
        assert "Direct free kick" in data["section_path"]
