from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".venv/.env",  # путь к твоему .env
        env_file_encoding="utf-8",
    )

    bot_token: str
    webhook_host: str
    webhook_path: str
    webhook_url: HttpUrl
    weather_api_token: str
    nasa_api_token: str
    open_exchange_token: str
    yandex_id_admin: str
    yandex_api_key: str
    fusion_brain_token: str
    fb_key: str
    admin_ids: frozenset[int] = frozenset({42, 5756911009})


settings = Settings()
