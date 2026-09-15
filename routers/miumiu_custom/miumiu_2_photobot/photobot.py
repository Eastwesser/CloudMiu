import os
import random
from pathlib import Path
from typing import Dict, Set

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from keyboards.inline_keyboards.actions_kb import build_actions_kb
from keyboards.on_start import ButtonText, get_on_help_kb

router = Router(name=__name__)


# MEME BOX =============================================================================================================
MEME_DIR = Path(__file__).resolve().parent / "meme_box"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
GIF_EXTS = {".gif"}
VIDEO_EXTS = {".mp4", ".webm", ".mov"}
MEDIA_EXTS = IMAGE_EXTS | GIF_EXTS | VIDEO_EXTS

# Per-user: filenames already sent (no duplicates until deck is exhausted)
_seen_memes: Dict[int, Set[str]] = {}


def list_meme_files() -> list[Path]:
    if not MEME_DIR.is_dir():
        return []
    files = [
        p
        for p in MEME_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in MEDIA_EXTS
    ]
    # Prefer numeric names (1.jpg … 224.mp4) for stable ordering when reshuffling
    def sort_key(p: Path):
        return (0, int(p.stem)) if p.stem.isdigit() else (1, p.name.lower())

    return sorted(files, key=sort_key)


def meme_reset_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Start over 🔄", callback_data="memes_reset")]
        ]
    )


async def send_meme_file(message: types.Message, path: Path) -> None:
    media = FSInputFile(path)
    caption = f"Here you are ^w^ ({path.name})"
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        await message.reply_photo(media, caption=caption)
    elif ext in GIF_EXTS:
        await message.reply_animation(media, caption=caption)
    elif ext in VIDEO_EXTS:
        await message.reply_video(media, caption=caption)
    else:
        await message.reply_document(media, caption=caption)


async def deliver_next_meme(message: types.Message, user_id: int) -> None:
    files = list_meme_files()
    if not files:
        await message.reply("No memes found :(")
        return

    seen = _seen_memes.setdefault(user_id, set())
    unseen = [p for p in files if p.name not in seen]

    if not unseen:
        total = len(files)
        await message.reply(
            f"No new memes left, pal :3\n"
            f"You've seen all {total} of them.\n"
            f"Tap below to start the deck from scratch.",
            reply_markup=meme_reset_kb(),
        )
        return

    pick = random.choice(unseen)
    seen.add(pick.name)
    left = len(unseen) - 1
    await send_meme_file(message, pick)
    if left == 0:
        await message.answer(
            "That was the last fresh meme in the deck! "
            "Next request will offer a restart.",
            reply_markup=meme_reset_kb(),
        )


@router.message(F.text == ButtonText.MEMES)
@router.message(Command("memes", prefix="!/"))
async def give_random_meme(message: types.Message):
    await deliver_next_meme(message, message.from_user.id)


@router.message(Command("memes_reset", prefix="!/"))
async def reset_memes_cmd(message: types.Message):
    _seen_memes.pop(message.from_user.id, None)
    await message.answer("Meme deck reset — fresh shuffle coming up :3")
    await deliver_next_meme(message, message.from_user.id)


@router.callback_query(F.data == "memes_reset")
async def reset_memes_cb(callback: types.CallbackQuery):
    _seen_memes.pop(callback.from_user.id, None)
    await callback.answer("Deck reset!")
    await deliver_next_meme(callback.message, callback.from_user.id)


@router.message(Command("actions", prefix="!/"))
async def send_actions_message_w_kb(message: types.Message):
    await message.answer(
        text="Your actions:",
        reply_markup=build_actions_kb(),
    )


# STICKER BOT ==========================================================================================================
class StickerButtonText:
    COOL_SERVAL = "Cool serval"
    NIKA = "Eustoma"
    ROCKET_KITTY = "Rocket-cat"
    RED_FOXIE = "Red fox"
    KITTY = "Cutie kitten"
    FOX = "Chonky Fox"
    GENSHIN = "Genshin Impact"
    TIK_TOK = "Tiktok animals"
    HSR = "HSR"
    MANGA = "Manga"


async def send_sticker(message: types.Message, sticker_id: str):
    await message.answer_sticker(sticker_id)


@router.message(F.text == ButtonText.STICKERS)
@router.message(Command("sticker_kb", prefix="!/"))
async def send_keyboard_command(message: types.Message):
    markup = get_sticker_kb()
    await message.answer("Choose a sticker:", reply_markup=markup)


def get_sticker_kb() -> ReplyKeyboardMarkup:
    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=StickerButtonText.COOL_SERVAL),
                KeyboardButton(text=StickerButtonText.NIKA),
                KeyboardButton(text=StickerButtonText.ROCKET_KITTY),
            ],
            [
                KeyboardButton(text=StickerButtonText.RED_FOXIE),
                KeyboardButton(text=StickerButtonText.KITTY),
                KeyboardButton(text=StickerButtonText.FOX),
            ],
            [
                KeyboardButton(text=StickerButtonText.GENSHIN),
                KeyboardButton(text=StickerButtonText.TIK_TOK),
                KeyboardButton(text=StickerButtonText.HSR),
            ],
            [
                KeyboardButton(text=StickerButtonText.MANGA),
                KeyboardButton(text=ButtonText.BACK),
            ],
        ],
        resize_keyboard=True,
    )
    return markup_keyboard


@router.message(F.text == ButtonText.BACK)
async def back_to_menu(message: types.Message):
    await message.answer("Back to help menu :3", reply_markup=get_on_help_kb())


@router.message(F.text == StickerButtonText.COOL_SERVAL)
async def cool_serv_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSIGY063zYcJsNIAwHRE9NnjiLjzWmAAJKSQAC4AfxSkws0ZUa6nFtNAQ')

@router.message(F.text == StickerButtonText.NIKA)
async def eustoma_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSAmY06vl7dAsZCAKHmSqN5FH9d5PYAAISUAAClT8RSGf6RXnVmT2nNAQ')

@router.message(F.text == StickerButtonText.ROCKET_KITTY)
async def rocket_kitty_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSDmY06yAl2_skuYkJi9Vz8fRrlLb6AAKoSAACWHM5SUoG_rkCAUQAATQE')

@router.message(F.text == StickerButtonText.RED_FOXIE)
async def red_fox_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSC2Y06xS5BOYGOg3FdBu39cHMjjatAAL_GwAC11hpSDnOE4z7Np33NAQ')

@router.message(F.text == StickerButtonText.KITTY)
async def cutie_kitty_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSBWY06wdjNO71aHgvFkTUgaAzgw7_AAJjKQACkpAZS_BALMjD9j1gNAQ')

@router.message(F.text == StickerButtonText.FOX)
async def chonky_fox_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSE2Y06z9rV1zG9p8NU3cwXVKJvM6qAAIHAwACz7vUDpXjgMoqn_mKNAQ')

@router.message(F.text == StickerButtonText.GENSHIN)
async def genshin_handler(message: types.Message):
    await send_sticker(message, 'CAACAgUAAxkBAVPSHmY0620IpHcCQrD8ZkLl6Q0mKD5UAALxDAACjIaBVVP5YlW7vh92NAQ')

@router.message(F.text == StickerButtonText.TIK_TOK)
async def tik_tok_animals_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSGmY061-ICZ4RrxvlgLeHi6KkUWd5AAIqRwACYdpoSKsAAQ2QWBSuaDQE')

@router.message(F.text == StickerButtonText.HSR)
async def hsr_handler(message: types.Message):
    await send_sticker(message, 'CAACAgIAAxkBAVPSFmY061WAA6rHHWhdvUxCv7u7ig9PAAK_MAAC6dvJSH8MV1OceRHLNAQ')

@router.message(F.text == StickerButtonText.MANGA)
async def manga_handler(message: types.Message):
    await send_sticker(message, 'CAACAgEAAxkBAVPR_mY06uLrPTII3Y8iZyRbGU7VAAH9WAACqwoAApl_iAIiidAVEPqjMTQE')


# PYTHON PRESENTATION ==================================================================================================
@router.message(F.text == ButtonText.PYTHON_PRESENTATION)
@router.message(Command("presentation", prefix="!/"))
async def send_presentation(message: types.Message):
    presentations_dir = os.path.join(os.path.dirname(__file__), "presentations")

    if not os.path.exists(presentations_dir):
        await message.answer("Sorry, the presentations are not available at the moment.")
        return

    presentations = [f for f in os.listdir(presentations_dir) if f.endswith(".pptx")]

    if not presentations:
        await message.answer("Sorry, there are no presentations available at the moment.")
        return

    presentation_path = os.path.join(presentations_dir, presentations[0])
    await message.answer_document(types.FSInputFile(presentation_path, presentations[0]))
