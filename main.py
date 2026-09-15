import asyncio
import logging
from pathlib import Path

import psutil

from app.runner import run
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def log_memory_usage() -> None:
    process = psutil.Process()
    mem_info = process.memory_info()
    logger.info("Memory usage: %.2f MB", mem_info.rss / (1024 * 1024))


if __name__ == "__main__":
    try:
        if not settings.bot_token:
            raise SystemExit(
                "BOT_TOKEN is missing in .env "
                f"(expected at {Path(__file__).resolve().parent / '.env'})"
            )
        if ":" not in settings.bot_token:
            raise SystemExit(
                "BOT_TOKEN looks invalid (expected format: 123456:AA…). "
                "Get a fresh token from @BotFather → /token or /revoke."
            )
        logger.info("Starting MiuMiu (mode=%s)...", settings.bot_mode)
        logger.info(
            "Using .env next to config; BOT_TOKEN id prefix=%s…",
            settings.bot_token.split(":", 1)[0],
        )
        log_memory_usage()
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt.")
        log_memory_usage()
    except Exception as exc:
        # aiogram may not be imported at top if token missing — keep soft
        name = type(exc).__name__
        if "Unauthorized" in name or "Unauthorized" in str(exc):
            raise SystemExit(
                "Telegram rejected BOT_TOKEN (Unauthorized).\n"
                "Fix: open @BotFather → your bot → API Token → copy into .env "
                "as BOT_TOKEN=... (no quotes), save, run again.\n"
                f"Detail: {exc}"
            ) from exc
        raise
