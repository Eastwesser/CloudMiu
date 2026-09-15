"""Shared reply-keyboard navigation: Back / Main menu / Back to games."""

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from keyboards.on_start import (
    ButtonText,
    get_games_kb,
    get_on_help_kb,
    get_on_start_kb,
)

router = Router(name=__name__)


@router.message(F.text == ButtonText.BACK)
async def nav_back_to_help(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(F.text == ButtonText.MAIN_MENU)
async def nav_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Main menu :3", reply_markup=get_on_start_kb())


@router.message(F.text == ButtonText.BACK_TO_GAMES)
async def nav_back_to_games(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Games menu :3", reply_markup=get_games_kb())
