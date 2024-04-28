from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .actions_kb import random_num_updated_cb_data


class RandomNumAction(Enum):
    dice = "dice"
    modal = "modal"


class RandomNumCbData(CallbackData, prefix='random_num'):
    action: RandomNumAction


def build_info_kb() -> InlineKeyboardMarkup:
    tg_channel_button = InlineKeyboardButton(
        text="👨‍💻 Канал",
        url="https://t.me/S1nRay",
    )
    tg_chat_button = InlineKeyboardButton(
        text="💬 Чат",
        url="https://t.me/S1nRay_Chat",
    )
    bot_source_button = InlineKeyboardButton(
        text="💾 My GitHub",
        url="https://github.com/Eastwesser",
    )
    button_random_site = InlineKeyboardButton(
        text="Random number message",
        callback_data=random_num_updated_cb_data,
    )
    button_random_num = InlineKeyboardButton(
        text="🎲 Random number",
        callback_data=RandomNumCbData(action=RandomNumAction.dice).pack(),
    )
    random_num_modal_cb_data_bts = InlineKeyboardButton(
        text="🎏 Random modal",
        callback_data=RandomNumCbData(action=RandomNumAction.modal).pack(),
    )
    row_tg = [tg_channel_button, tg_chat_button]
    row_randoms = [button_random_num, random_num_modal_cb_data_bts]
    rows = [
        row_tg,
        row_randoms,
        [bot_source_button],
        [button_random_site],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
