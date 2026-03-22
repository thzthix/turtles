import io

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_ai.models.test import TestModel

from turtle_agent.agent import create_agent
from turtle_agent.server import app

FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


@pytest.fixture
def patch_agent(monkeypatch):
    test_agent = create_agent(model=TestModel(call_tools=[]))
    monkeypatch.setattr("turtle_agent.server.get_agent", lambda: test_agent)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestAnalyzeEndpoint:
    @pytest.mark.anyio
    async def test_valid_image_returns_success(self, client, patch_agent) -> None:
        response = await client.post(
            "/analyze",
            files={"file": ("turtle.png", io.BytesIO(FAKE_PNG), "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] is not None
        assert body["error"] is None

    @pytest.mark.anyio
    async def test_valid_image_returns_species(self, client, patch_agent) -> None:
        response = await client.post(
            "/analyze",
            files={"file": ("turtle.jpg", io.BytesIO(FAKE_PNG), "image/jpeg")},
        )
        body = response.json()
        assert "species" in body["data"]
        assert "gender" in body["data"]
        assert "species_confidence" in body["data"]
        assert "gender_confidence" in body["data"]
        assert "distinguishing_features" in body["data"]
        assert "description" in body["data"]

    @pytest.mark.anyio
    async def test_webp_accepted(self, client, patch_agent) -> None:
        response = await client.post(
            "/analyze",
            files={"file": ("turtle.webp", io.BytesIO(FAKE_PNG), "image/webp")},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True


class TestImageValidation:
    @pytest.mark.anyio
    async def test_invalid_media_type_rejected(self, client) -> None:
        response = await client.post(
            "/analyze",
            files={"file": ("turtle.gif", io.BytesIO(FAKE_PNG), "image/gif")},
        )
        assert response.status_code == 400
        body = response.json()["detail"]
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_IMAGE"

    @pytest.mark.anyio
    async def test_oversized_image_rejected(self, client, patch_agent) -> None:
        large_data = b"\x00" * (5 * 1024 * 1024 + 1)
        response = await client.post(
            "/analyze",
            files={"file": ("big.png", io.BytesIO(large_data), "image/png")},
        )
        assert response.status_code == 400
        body = response.json()["detail"]
        assert body["success"] is False
        assert body["error"]["code"] == "IMAGE_TOO_LARGE"

    @pytest.mark.anyio
    async def test_exactly_5mb_accepted(self, client, patch_agent) -> None:
        exact_data = b"\x00" * (5 * 1024 * 1024)
        response = await client.post(
            "/analyze",
            files={"file": ("exact.png", io.BytesIO(exact_data), "image/png")},
        )
        assert response.status_code == 200


class TestErrorHandling:
    @pytest.mark.anyio
    async def test_no_file_returns_422(self, client) -> None:
        response = await client.post("/analyze")
        assert response.status_code == 422
