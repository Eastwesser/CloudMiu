from __future__ import annotations

import pytest

from config import Settings
from services.drawer import build_drawer
from services.drawer.pollinations import PollinationsDrawer


def test_pollinations_url_encoding() -> None:
    d = PollinationsDrawer(width=64, height=64, model="flux")
    url = d._build_url("orange cat / paws")
    assert "image.pollinations.ai/prompt/" in url
    assert "width=64" in url
    assert "model=flux" in url


@pytest.mark.asyncio
async def test_pollinations_draw_mocked() -> None:
    d = PollinationsDrawer(width=64, height=64)

    class FakeResp:
        status = 200

        async def text(self):
            return ""

        async def read(self):
            return b"\xff\xd8\xff" + b"0" * 200  # fake jpeg

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    class FakeSession:
        closed = False

        def get(self, url, **kwargs):
            assert "/prompt/" in url
            return FakeResp()

        async def close(self):
            return None

    d._session = FakeSession()
    d._owns_session = False
    result = await d.draw("a cute cat")
    assert result.provider == "pollinations"
    assert len(result.image_bytes) > 100


def test_build_default_is_pollinations() -> None:
    s = Settings(bot_token="x", drawer_backend="pollinations", drawer_fallback_mock=False)
    assert isinstance(build_drawer(s), PollinationsDrawer)


def test_build_auto_starts_with_pollinations() -> None:
    s = Settings(
        bot_token="x",
        drawer_backend="auto",
        drawer_fallback_mock=False,
        fusion_brain_token="",
        fb_key="",
        leonardo_api_key="",
    )
    d = build_drawer(s)
    assert isinstance(d, PollinationsDrawer)
