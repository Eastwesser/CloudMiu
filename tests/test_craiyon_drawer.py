from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from config import Settings
from services.drawer import build_drawer
from services.drawer.craiyon import CraiyonAdTimeDrawer
from services.drawer.mock import MockDrawer


@pytest.mark.asyncio
async def test_craiyon_login_and_generate_flow() -> None:
    drawer = CraiyonAdTimeDrawer(
        "http://adtime.test:8042",
        "user@test.com",
        "secret",
        model_version="craiyon-v3",
    )

    class FakeResp:
        def __init__(self, status: int, payload):
            self.status = status
            self._payload = payload

        async def text(self):
            return str(self._payload)

        async def json(self, content_type=None):
            return self._payload

        async def read(self):
            return b"\x89PNG fake"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    class FakeSession:
        def __init__(self):
            self.closed = False

        def post(self, url, **kwargs):
            if url.endswith("/login"):
                return FakeResp(200, {"token": {"access_token": "tok-1"}})
            if url.endswith("/generate"):
                assert kwargs["headers"]["Authorization"] == "Bearer tok-1"
                assert kwargs["json"]["model_version"] == "craiyon-v3"
                return FakeResp(200, {"id": "abc", "result_url": "http://cdn/x.png"})
            raise AssertionError(url)

        def get(self, url, **kwargs):
            assert url == "http://cdn/x.png"
            return FakeResp(200, {})

        async def close(self):
            self.closed = True

    drawer._session = FakeSession()
    drawer._owns_session = False
    result = await drawer.draw("a gift box")
    assert result.provider == "craiyon"
    assert result.image_bytes.startswith(b"\x89PNG")
    assert "Craiyon" in result.caption_prefix


def test_build_auto_prefers_craiyon() -> None:
    s = Settings(
        bot_token="x",
        drawer_backend="auto",
        craiyon_base_url="http://127.0.0.1:8042",
        craiyon_username="u",
        craiyon_password="p",
        fusion_brain_token="fb",
        fb_key="k",
        drawer_fallback_mock=False,
    )
    d = build_drawer(s)
    assert isinstance(d, CraiyonAdTimeDrawer)


def test_build_craiyon_missing_creds_falls_to_mock() -> None:
    s = Settings(bot_token="x", drawer_backend="craiyon", craiyon_base_url="")
    d = build_drawer(s)
    assert isinstance(d, MockDrawer)
