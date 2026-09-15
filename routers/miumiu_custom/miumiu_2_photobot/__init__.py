from aiogram import Router

from . import drawer, photobot

router = Router(name="photobot_pkg")
router.include_router(drawer.router)
router.include_router(photobot.router)
