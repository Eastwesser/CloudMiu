from aiogram import Router

from . import mathix

router = Router()

router.include_router(mathix.router)
