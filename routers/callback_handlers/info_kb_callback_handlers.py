from random import randint

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.inline_keyboards.info_kb import (
    RandomNumCbData,
    RandomNumAction,
)

router = Router(name=__name__)


@router.callback_query(
    RandomNumCbData.filter(F.action == RandomNumAction.dice),
)
async def handle_random_num_dice_cb(callback_query: CallbackQuery):
    await callback_query.answer(
        text=f"Your random dice: {randint(1, 21)}",
    )


@router.callback_query(
    RandomNumCbData.filter(F.action == RandomNumAction.modal),
)
async def handle_random_num_modal_cb(callback_query: CallbackQuery):
    await callback_query.answer(
        text=f"Random number: {randint(1, 100)}",
        show_alert=True,
    )
