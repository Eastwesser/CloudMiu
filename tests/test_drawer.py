from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Chat, Message, User

from routers.miumiu_custom.miumiu_2_photobot import drawer
from services.drawer.base import DrawResult


def _message(text: str = "a cute cat") -> MagicMock:
    msg = MagicMock(spec=Message)
    msg.text = text
    msg.answer = AsyncMock()
    msg.answer_photo = AsyncMock()
    msg.from_user = User(id=1, is_bot=False, first_name="T")
    msg.chat = Chat(id=1, type="private")
    return msg


@pytest.mark.asyncio
async def test_process_prompt_with_mock_backend(monkeypatch) -> None:
    monkeypatch.setattr(drawer.settings, "drawer_backend", "mock")
    monkeypatch.setattr(drawer.settings, "drawer_fallback_mock", True)

    fake = MagicMock()
    fake.draw = AsyncMock(
        return_value=DrawResult(image_bytes=b"\x89PNG", caption_prefix="[mock]", provider="mock")
    )
    fake.aclose = AsyncMock()
    monkeypatch.setattr(drawer, "build_drawer", lambda _s: fake)

    state = AsyncMock(spec=FSMContext)
    state.clear = AsyncMock()
    msg = _message("orange cat")

    await drawer.process_prompt(msg, state)

    fake.draw.assert_awaited_with("orange cat")
    msg.answer_photo.assert_awaited()
    state.clear.assert_awaited()
    fake.aclose.assert_awaited()


@pytest.mark.asyncio
async def test_start_drawer_sends_keyboard() -> None:
    msg = _message()
    await drawer.start_drawer(msg)
    msg.answer.assert_awaited()
    kwargs = msg.answer.await_args.kwargs
    assert kwargs.get("reply_markup") is not None


def test_drawer_kb_button() -> None:
    kb = drawer.get_drawer_kb()
    assert kb.keyboard[0][0].text == drawer.DrawerButtons.TEXT_TO_IMAGE
