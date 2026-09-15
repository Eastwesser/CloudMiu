from __future__ import annotations

import config
from keyboards.on_start import ButtonText, get_on_help_kb


def test_default_bot_mode_polling(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "tok")
    monkeypatch.setenv("BOT_MODE", "polling")
    monkeypatch.delenv("WEBHOOK_HOST", raising=False)
    config.clear_settings_cache()
    s = config.get_settings()
    assert s.bot_mode == "polling"
    assert s.leonardo_model == "phoenix-v1.0"


def test_leonardo_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "tok")
    monkeypatch.setenv("LEONARDO_API_KEY", "leo-secret")
    monkeypatch.setenv("LEONARDO_MODEL", "flux-schnell")
    monkeypatch.setenv("LEONARDO_MODE", "QUALITY")
    config.clear_settings_cache()
    s = config.get_settings()
    assert s.leonardo_api_key == "leo-secret"
    assert s.leonardo_model == "flux-schnell"
    assert s.leonardo_mode == "QUALITY"


def test_help_keyboard_has_drawer() -> None:
    kb = get_on_help_kb()
    labels = {btn.text for row in kb.keyboard for btn in row}
    assert ButtonText.DRAWER in labels
    assert ButtonText.ALICE in labels
    assert ButtonText.MAIN_MENU in labels


def test_games_and_emoji_have_back() -> None:
    from keyboards.on_start import get_games_kb, get_games_emoji_kb

    games = {btn.text for row in get_games_kb().keyboard for btn in row}
    emoji = {btn.text for row in get_games_emoji_kb().keyboard for btn in row}
    assert ButtonText.BACK in games
    assert ButtonText.BACK in emoji
    assert ButtonText.BACK_TO_GAMES in emoji
