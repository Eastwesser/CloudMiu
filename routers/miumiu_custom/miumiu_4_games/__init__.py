from aiogram import Router

from . import games

router = Router()

router.include_router(games.router)
