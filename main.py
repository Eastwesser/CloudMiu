import logging

from fastapi import FastAPI

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import settings
from routers import router as main_router  # твои хендлеры

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(main_router)

# Инициализация FastAPI
app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(settings.webhook_url)
    logger.info(f"✅ Webhook установлен: {settings.webhook_url}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logger.info("🛑 Webhook удалён")


# Привязка aiogram к FastAPI
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=settings.webhook_path)
setup_application(app, dp, bot=bot)
