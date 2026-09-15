from __future__ import annotations

import pytest

from config import Settings
from services.drawer import build_drawer
from services.drawer.base import DrawerError, DrawResult
from services.drawer.mock import MockDrawer, render_prompt_png
from services.drawer import FallbackDrawer


def test_mock_png_is_valid_png() -> None:
    data = render_prompt_png("orange cat with paws", 64, 64)
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(data) > 100


@pytest.mark.asyncio
async def test_mock_drawer_draw() -> None:
    drawer = MockDrawer(width=64, height=64)
    result = await drawer.draw("hello")
    assert isinstance(result, DrawResult)
    assert result.provider == "mock"
    assert result.image_bytes.startswith(b"\x89PNG")


def test_build_drawer_mock() -> None:
    s = Settings(bot_token="x", drawer_backend="mock")
    d = build_drawer(s)
    assert isinstance(d, MockDrawer)


def test_build_drawer_unknown() -> None:
    s = Settings(bot_token="x", drawer_backend="nope")
    with pytest.raises(DrawerError, match="Unknown"):
        build_drawer(s)


@pytest.mark.asyncio
async def test_fallback_uses_mock_on_primary_fail() -> None:
    class Boom:
        name = "boom"

        async def draw(self, prompt: str):
            raise DrawerError("blocked")

        async def aclose(self):
            return None

    fb = FallbackDrawer(Boom(), MockDrawer(32, 32))  # type: ignore[arg-type]
    result = await fb.draw("x")
    assert result.image_bytes.startswith(b"\x89PNG")
    assert "fallback" in result.caption_prefix.lower() or "mock" in result.caption_prefix.lower()


@pytest.mark.asyncio
async def test_build_auto_without_keys_uses_pollinations() -> None:
    s = Settings(
        bot_token="x",
        drawer_backend="auto",
        drawer_fallback_mock=False,
        fusion_brain_token="",
        fb_key="",
        leonardo_api_key="",
    )
    from services.drawer.pollinations import PollinationsDrawer

    d = build_drawer(s)
    assert isinstance(d, PollinationsDrawer)
