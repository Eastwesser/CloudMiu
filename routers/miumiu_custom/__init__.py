from aiogram import Router

router = Router(name=__name__)


def include_business_router():
    from .miumiu_1_business import router as business_router
    router.include_router(business_router)


def include_photobot_router():
    from .miumiu_2_photobot import router as photobot_router
    router.include_router(photobot_router)


def include_mathix_router():
    from .miumiu_3_mathix import router as mathix_router
    router.include_router(mathix_router)


def include_games_router():
    from .miumiu_4_games import router as games_router
    router.include_router(games_router)
