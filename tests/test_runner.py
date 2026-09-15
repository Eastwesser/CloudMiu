from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app import runner


@pytest.mark.asyncio
async def test_run_selects_polling(monkeypatch) -> None:
    monkeypatch.setattr(runner.settings, "bot_mode", "polling")
    bot = MagicMock()
    dp = MagicMock()
    monkeypatch.setattr(runner, "create_bot", lambda: bot)
    monkeypatch.setattr(runner, "create_dispatcher", lambda: dp)
    poll = AsyncMock()
    monkeypatch.setattr(runner, "run_polling", poll)
    hook = AsyncMock()
    monkeypatch.setattr(runner, "run_webhook", hook)

    await runner.run()

    poll.assert_awaited_once_with(bot, dp)
    hook.assert_not_awaited()


@pytest.mark.asyncio
async def test_run_selects_webhook(monkeypatch) -> None:
    monkeypatch.setattr(runner.settings, "bot_mode", "webhook")
    bot = MagicMock()
    dp = MagicMock()
    monkeypatch.setattr(runner, "create_bot", lambda: bot)
    monkeypatch.setattr(runner, "create_dispatcher", lambda: dp)
    poll = AsyncMock()
    monkeypatch.setattr(runner, "run_polling", poll)
    hook = AsyncMock()
    monkeypatch.setattr(runner, "run_webhook", hook)

    await runner.run()

    hook.assert_awaited_once_with(bot, dp)
    poll.assert_not_awaited()


@pytest.mark.asyncio
async def test_webhook_requires_host(monkeypatch) -> None:
    monkeypatch.setattr(runner.settings, "webhook_host", "")
    bot = MagicMock()
    dp = MagicMock()
    with pytest.raises(RuntimeError, match="WEBHOOK_HOST"):
        await runner.run_webhook(bot, dp)
