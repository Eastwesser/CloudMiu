from aiogram import F, Router, types
from aiogram.enums import ChatAction
from aiogram.types import ReplyKeyboardRemove

from keyboards.on_start import (
    get_games_kb,
    get_games_emoji_kb,
    ButtonText,
)

router = Router(name=__name__)


@router.message(F.text == ButtonText.GAMES)
async def handle_games_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to play with me,\n"
             "Click on these games any time! :3",
        reply_markup=get_games_kb()
    )


@router.message(F.text == ButtonText.EMOJI)
async def handle_emoji_message(message: types.Message):
    await message.answer(
        text="Meow! If you want play emoji,\n"
             "Click emoji kb any time! :3",
        reply_markup=get_games_emoji_kb()
    )


@router.message(F.text == ButtonText.BYE)
async def handle_bye_message(message: types.Message):
    await message.answer(
        text="See you later! Click /start any time! =)",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


# ECHO BOT
@router.message()
async def echo_message(message: types.Message):
    if message.poll:
        await message.forward(chat_id=message.chat.id)
        return
    await message.answer(
        text="Wait a second...",
        parse_mode=None,
    )

    if message.sticker:
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.CHOOSE_STICKER,
        )
    try:
        await message.copy_to(chat_id=message.chat.id)

    except TypeError:
        await message.reply(text="Something new 🙂")
