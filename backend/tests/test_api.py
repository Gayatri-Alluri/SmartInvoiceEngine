import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_process_rejects_invalid_file_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/process",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.anyio
async def test_process_accepts_pdf():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/process",
            files={"file": ("invoice.pdf", b"%PDF-fake", "application/pdf")},
        )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "processing"


@pytest.mark.anyio
async def test_status_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/status/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_result_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/result/nonexistent-id")
    assert response.status_code == 404
