import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv_path = os.path.join(os.getcwd(), ".venv", ".env")

load_dotenv(dotenv_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
    )

    bot_token: str = os.getenv('BOT_TOKEN')
    weather_api_token: str = os.getenv('WEATHER_API_TOKEN')
    nasa_api_token: str = os.getenv('NASA_API_TOKEN')
    open_exchange_token: str = os.getenv('OPEN_EXCHANGE_TOKEN')
    yandex_id_admin: str = os.getenv('YANDEX_ID_ADMIN')
    yandex_api_key: str = os.getenv('YANDEX_API_KEY')
    fusion_brain_token: str = os.getenv('FUSION_BRAIN_TOKEN')
    fb_key: str = os.getenv('FB_KEY')
    admin_ids: frozenset[int] = frozenset({42, 5756911009})


settings = Settings()
