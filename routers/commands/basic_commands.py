import os

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown
from dotenv import load_dotenv

from keyboards.inline_keyboards.info_kb import build_info_kb
from keyboards.on_start import (
    ButtonText,
    get_on_start_kb,
    get_on_help_kb,
    get_actions_kb,
)

bot_token = os.getenv('BOT_TOKEN')

load_dotenv()

router = Router(name=__name__)


@router.message(CommandStart())  # added in m1, renamed in m5
async def handle_start(message: types.Message):
    # url = "https://64.media.tumblr.com/e04c17953a3bf8678feb7bcb5b7fbcfe/813055467fd14c85-9c/s1280x1920/8b0d5f82035c6e26ce66f29d50415a7d8897d55e.gifv"
    welcome_sticker_id = "CAACAgIAAxkBAU0juGYWfesC5Y_5wM1gxbKqoEcp0LgbAAIzNgACYrv5SpdmcVJVwH4zNAQ"
    await message.answer_sticker(sticker=welcome_sticker_id)

    await message.answer(
        text=f"{markdown.hide_link(welcome_sticker_id)}Hello, {markdown.hbold(message.from_user.full_name)}!",
        parse_mode=ParseMode.HTML,
        reply_markup=get_on_start_kb(),
    )


@router.message(F.text == ButtonText.WHATS_NEXT)
@router.message(Command("help", prefix="!/"))  # added in m1, and prefix="!/" in m3
async def handle_help(message: types.Message):
    text = markdown.text(
        markdown.markdown_decoration.quote("I'm MiuMiu, your personal little helper!"),
        markdown.text(
            "Send me",
            markdown.markdown_decoration.bold(
                markdown.text(
                    markdown.underline("literally"),
                    "any",
                ),
            ),
            markdown.markdown_decoration.quote("message!"),
        ),
        sep="\n",
    )
    await message.answer(
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_on_help_kb()
    )


@router.message(Command("more", prefix="!/"))
async def handle_more(message: types.Message):
    markup = get_actions_kb()
    await message.answer(
        text="Choose action",
        reply_markup=markup,
    )


@router.message(Command("info", prefix="!/"))
async def handle_info_command(message: types.Message):
    markup = build_info_kb()
    await message.answer(
        text="Ссылки и прочие ресурсы:",
        reply_markup=markup,
    )
