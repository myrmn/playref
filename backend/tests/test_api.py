"""Unit tests for FastAPI endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


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
