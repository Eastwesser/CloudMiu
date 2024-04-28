from aiogram import Router

from . import business

router = Router()

router.include_router(business.router)
