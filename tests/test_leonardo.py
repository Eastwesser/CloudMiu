from __future__ import annotations

import pytest

from services.leonardo import LeonardoClient, LeonardoError


def test_missing_api_key_raises() -> None:
    with pytest.raises(LeonardoError, match="LEONARDO_API_KEY"):
        LeonardoClient("")


@pytest.mark.parametrize(
    "payload,expected_status,expected_urls",
    [
        (
            {
                "generations_by_pk": {
                    "status": "PENDING",
                    "generated_images": [],
                }
            },
            "PENDING",
            [],
        ),
        (
            {
                "generations_by_pk": {
                    "status": "COMPLETE",
                    "generated_images": [{"id": "1", "url": "https://cdn.example/a.png"}],
                }
            },
            "COMPLETE",
            ["https://cdn.example/a.png"],
        ),
        (
            {
                "generation": {
                    "status": "COMPLETE",
                    "images": ["https://cdn.example/b.jpg"],
                }
            },
            "COMPLETE",
            ["https://cdn.example/b.jpg"],
        ),
    ],
)
def test_extract_status_and_urls(payload, expected_status, expected_urls) -> None:
    status, urls = LeonardoClient._extract_status_and_urls(payload)
    assert status == expected_status
    assert urls == expected_urls


@pytest.mark.asyncio
async def test_create_generation_parses_v2_id(monkeypatch) -> None:
    client = LeonardoClient("test-key", poll_delay=0)

    class FakeResp:
        status = 200

        async def text(self):
            return '{"generationId":"gen-123"}'

        async def json(self, content_type=None):
            return {"generationId": "gen-123"}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    class FakeSession:
        def post(self, *args, **kwargs):
            return FakeResp()

        @property
        def closed(self):
            return False

        async def close(self):
            return None

    client._session = FakeSession()
    client._owns_session = False
    assert await client.create_generation("a cat") == "gen-123"


@pytest.mark.asyncio
async def test_create_generation_http_error() -> None:
    client = LeonardoClient("test-key")

    class FakeResp:
        status = 401

        async def text(self):
            return "unauthorized"

        async def json(self, content_type=None):
            return {}

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    class FakeSession:
        def post(self, *args, **kwargs):
            return FakeResp()

        @property
        def closed(self):
            return False

    client._session = FakeSession()
    client._owns_session = False
    with pytest.raises(LeonardoError, match="401"):
        await client.create_generation("x")


@pytest.mark.asyncio
async def test_wait_for_images_success() -> None:
    client = LeonardoClient("test-key", poll_attempts=3, poll_delay=0)
    calls = {"n": 0}

    async def fake_get(_gid: str):
        calls["n"] += 1
        if calls["n"] < 2:
            return {"generations_by_pk": {"status": "PENDING", "generated_images": []}}
        return {
            "generations_by_pk": {
                "status": "COMPLETE",
                "generated_images": [{"url": "https://cdn.example/done.png"}],
            }
        }

    client.get_generation = fake_get  # type: ignore[method-assign]
    urls = await client.wait_for_images("gid")
    assert urls == ["https://cdn.example/done.png"]
    assert calls["n"] == 2


@pytest.mark.asyncio
async def test_wait_for_images_failed_status() -> None:
    client = LeonardoClient("test-key", poll_attempts=2, poll_delay=0)

    async def fake_get(_gid: str):
        return {"generations_by_pk": {"status": "FAILED", "generated_images": []}}

    client.get_generation = fake_get  # type: ignore[method-assign]
    with pytest.raises(LeonardoError, match="failed"):
        await client.wait_for_images("gid")


@pytest.mark.asyncio
async def test_text_to_image_end_to_end_mocked() -> None:
    client = LeonardoClient("test-key", poll_delay=0)

    async def fake_create(prompt: str) -> str:
        assert prompt == "orange cat"
        return "gid-1"

    async def fake_wait(gid: str) -> list[str]:
        assert gid == "gid-1"
        return ["https://cdn.example/cat.png"]

    client.create_generation = fake_create  # type: ignore[method-assign]
    client.wait_for_images = fake_wait  # type: ignore[method-assign]
    assert await client.text_to_image("orange cat") == ["https://cdn.example/cat.png"]
