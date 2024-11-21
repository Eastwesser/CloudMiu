import asyncio
import logging
import psutil

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from routers import router as main_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_memory_usage():
    process = psutil.Process()
    mem_info = process.memory_info()
    logger.info(f'Memory usage: {mem_info.rss / (1024 * 1024):.2f} MB')


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    log_memory_usage()
    await dp.start_polling(bot)
    log_memory_usage()


if __name__ == '__main__':
    try:
        logger.info('Starting the bot...')
        log_memory_usage()
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped by keyboard interrupt.')
        log_memory_usage()
