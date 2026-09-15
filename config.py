from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8-sig",  # tolerate Windows Notepad BOM
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str = ""
    weather_api_token: str = ""
    nasa_api_token: str = ""
    open_exchange_token: str = ""
    yandex_id_admin: str = ""
    yandex_api_key: str = ""

    # Drawer: mock | pollinations | fusionbrain | craiyon | leonardo | auto
    drawer_backend: str = "pollinations"
    drawer_fallback_mock: bool = True

    # Pollinations.AI (free, no key required — optional token for higher limits)
    pollinations_base_url: str = "https://image.pollinations.ai"
    pollinations_model: str = "flux"
    pollinations_token: str = ""  # optional; free signup at auth.pollinations.ai

    # Craiyon via compatible host only (official craiyon.com has NO public API)
    craiyon_base_url: str = ""
    craiyon_username: str = ""
    craiyon_password: str = ""
    craiyon_model_version: str = "craiyon-v3"

    # Legacy FusionBrain / Kandinsky
    fusion_brain_token: str = ""
    fb_key: str = ""

    # Leonardo.AI (when reachable + paid/credit)
    leonardo_api_key: str = ""
    leonardo_model: str = "phoenix-v1.0"
    leonardo_mode: str = "FAST"
    leonardo_width: int = 1024
    leonardo_height: int = 1024

    # polling | webhook  (Telegram has no Bot-API WebSocket for updates)
    bot_mode: str = "polling"
    webhook_host: str = ""  # e.g. https://bot.example.com
    webhook_path: str = "/telegram/webhook"
    webhook_secret: str = ""
    webhook_listen_host: str = "0.0.0.0"
    webhook_port: int = 8080

    admin_ids: frozenset[int] = frozenset({42, 5756911009})

    @field_validator(
        "bot_token",
        "weather_api_token",
        "nasa_api_token",
        "open_exchange_token",
        "yandex_id_admin",
        "yandex_api_key",
        "pollinations_token",
        "fusion_brain_token",
        "fb_key",
        "leonardo_api_key",
        mode="before",
    )
    @classmethod
    def strip_secrets(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip().strip('"').strip("'")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()


# Back-compat for existing imports: `from config import settings`
settings = get_settings()
