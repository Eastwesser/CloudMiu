"""Drawer mode — pluggable backends (mock / FusionBrain / Leonardo)."""

from __future__ import annotations

import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import settings
from keyboards.on_start import ButtonText, get_on_help_kb
from services.drawer import build_drawer
from services.drawer.base import DrawerError

logger = logging.getLogger(__name__)

router = Router(name=__name__)


class DrawerStates(StatesGroup):
    waiting_prompt = State()


class DrawerButtons:
    TEXT_TO_IMAGE = "Text to image"


def get_drawer_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=DrawerButtons.TEXT_TO_IMAGE)],
            [KeyboardButton(text=ButtonText.BACK)],
        ],
        resize_keyboard=True,
    )


def _backend_label() -> str:
    return (settings.drawer_backend or "mock").strip().lower()


@router.message(F.text.in_({ButtonText.DRAWER, ButtonText.KANDINSKY}))
@router.message(Command("start_drawer", "start_kandinsky", prefix="!/"))
async def start_drawer(message: types.Message) -> None:
    backend = _backend_label()
    await message.answer(
        "Welcome to <b>Drawer</b> mode!\n"
        f"Backend: <code>{backend}</code>"
        + (" (+ mock fallback)" if settings.drawer_fallback_mock and backend != "mock" else "")
        + "\n"
        "Press <b>Text to image</b>, then send a prompt.\n"
        "Please don't ask for violent or forbidden stuff — I have paws 😿",
        reply_markup=get_drawer_kb(),
    )


@router.message(F.text == DrawerButtons.TEXT_TO_IMAGE)
async def handle_text_to_image(message: Message, state: FSMContext) -> None:
    await state.set_state(DrawerStates.waiting_prompt)
    await message.answer(
        "Send the text you want me to paint.\n"
        "Remote APIs may take ~20–60s; mock is instant.\n"
        f"Or tap {ButtonText.BACK}."
    )


@router.message(DrawerStates.waiting_prompt, F.text == ButtonText.BACK)
async def drawer_back(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(DrawerStates.waiting_prompt, F.text)
async def process_prompt(message: types.Message, state: FSMContext) -> None:
    prompt = (message.text or "").strip()
    if not prompt:
        await message.answer("Empty prompt — try again with some words.")
        return

    await message.answer("🎨 Sketching… please wait.")
    drawer = build_drawer(settings)
    try:
        result = await drawer.draw(prompt)
        photo = BufferedInputFile(result.image_bytes, filename="drawer.png")
        caption = f"{result.caption_prefix} Prompt: {prompt[:180]}".strip()
        await message.answer_photo(photo, caption=caption)
    except DrawerError as exc:
        logger.exception("Drawer failed: %s", exc)
        await message.answer(
            "😿 Couldn't finish the drawing.\n"
            f"<code>{exc}</code>\n"
            "Try <code>DRAWER_BACKEND=mock</code> or FusionBrain keys."
        )
    except Exception:
        logger.exception("Unexpected drawer error")
        await message.answer("😿 Something went wrong while drawing. Try again later.")
    finally:
        await drawer.aclose()
        await state.clear()


@router.message(DrawerStates.waiting_prompt)
async def process_non_text(message: types.Message) -> None:
    await message.answer("I need a text prompt for drawing. Send words, not files.")
