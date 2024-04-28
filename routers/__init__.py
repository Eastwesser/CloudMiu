__all__ = ("router",)  # THIS IS THE MAIN ROUTER

from aiogram import Router

from .admin_handlers import router as admin_router
from .callback_handlers import router as callback_router
from .commands import router as commands_router
from .miumiu_custom.miumiu_1_business import router as business_router
from .miumiu_custom.miumiu_2_photobot import router as photobot_router
from .miumiu_custom.miumiu_3_mathix import router as mathix_router
from .miumiu_custom.miumiu_4_games import router as games_router
from .common import router as common_router
from .media_handlers import router as media_router

router = Router(name=__name__)

router.include_routers(callback_router,
                       commands_router,
                       business_router,
                       photobot_router,
                       mathix_router,
                       games_router,
                       media_router,
                       # add your router here (if you want)
                       admin_router,
                       )

# the router below has to be the final, echo-bot command!!!
router.include_router(common_router)  # THIS ECHO BOT MUST BE THE LAST!!!
