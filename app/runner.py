"""Bot lifecycle: polling (local/Pi) or webhook (public HTTPS).

Telegram Bot API has no client WebSocket for updates — webhook is the
non-polling mode. Set BOT_MODE=webhook and WEBHOOK_HOST to an HTTPS URL.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from config import settings
from routers import router as main_router

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(main_router)
    return dp


async def run_polling(bot: Bot, dp: Dispatcher) -> None:
    logger.info("Starting bot in POLLING mode")
    await bot.delete_webhook(drop_pending_updates=False)
    await dp.start_polling(bot)


async def run_webhook(bot: Bot, dp: Dispatcher) -> None:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    if not settings.webhook_host:
        raise RuntimeError("WEBHOOK_HOST is required when BOT_MODE=webhook")

    webhook_url = f"{settings.webhook_host.rstrip('/')}{settings.webhook_path}"
    logger.info("Starting bot in WEBHOOK mode url=%s", webhook_url)

    async def on_startup(app: web.Application) -> None:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret or None,
            drop_pending_updates=False,
        )

    async def on_shutdown(app: web.Application) -> None:
        await bot.delete_webhook(drop_pending_updates=False)
        await bot.session.close()

    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret or None,
    ).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.webhook_listen_host, port=settings.webhook_port)
    await site.start()
    logger.info(
        "Webhook server listening on %s:%s path=%s",
        settings.webhook_listen_host,
        settings.webhook_port,
        settings.webhook_path,
    )

    stop = asyncio.Event()
    try:
        await stop.wait()
    finally:
        await runner.cleanup()


async def run() -> None:
    bot = create_bot()
    dp = create_dispatcher()
    mode = (settings.bot_mode or "polling").strip().lower()
    if mode == "webhook":
        await run_webhook(bot, dp)
    else:
        await run_polling(bot, dp)
