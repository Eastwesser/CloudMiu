from aiogram import Router

from . import photobot

router = Router()

router.include_router(photobot.router)
