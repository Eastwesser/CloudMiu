from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonPollType,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ButtonText:
    HELLO = "Hello!"
    WHATS_NEXT = "What's next?"
    BYE = "Goodbye!"
    BACK = "⬅️ Back"
    MAIN_MENU = "🏠 Main menu"
    BACK_TO_GAMES = "⬅️ Games"
    WEATHER = "Weather"
    YANDEX_GPT = "YandexGPT"
    ALICE = "Alice"  # same chat as YandexGPT (user-facing name)
    DRAWER = "Drawer"
    KANDINSKY = "Kandinsky"  # legacy label; still accepted by drawer router
    CURRENCY = "Currency"
    CALCULATOR = "Calculator"
    CONVERTER = "Converter"
    MAGNETIC_STORM = "Magnetic Storm"
    PYTHON_PRESENTATION = "Python Presentation"
    VIDEO_TO_MP3 = "Video to MP3"
    MEMES = "Memes"
    STICKERS = "Stickers"
    GAMES = "Games"
    RPS = "Rock Paper Scissors"
    BLACKJACK = "Blackjack"
    BLOCK_ME = "BlockMe!"
    BATTLESHIP = "Battleship"
    FIVE_CATS = "5 Cats"
    EMOJI = "Emoji"
    DICE = "Dice"
    DART = "Darts"
    CASINO = "Casino"
    FOOTBALL = "Football"
    BASKETBALL = "Basketball"
    BOWLING = "Bowling"


def _back_row(*texts: str) -> list[KeyboardButton]:
    return [KeyboardButton(text=t) for t in texts]


def get_on_start_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ButtonText.HELLO),
                KeyboardButton(text=ButtonText.WHATS_NEXT),
            ],
            [KeyboardButton(text=ButtonText.BYE)],
        ],
        resize_keyboard=True,
    )


def get_on_help_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ButtonText.WEATHER),
                KeyboardButton(text=ButtonText.ALICE),
                KeyboardButton(text=ButtonText.DRAWER),
            ],
            [
                KeyboardButton(text=ButtonText.CURRENCY),
                KeyboardButton(text=ButtonText.CALCULATOR),
                KeyboardButton(text=ButtonText.CONVERTER),
            ],
            [
                KeyboardButton(text=ButtonText.MAGNETIC_STORM),
                KeyboardButton(text=ButtonText.PYTHON_PRESENTATION),
            ],
            [
                KeyboardButton(text=ButtonText.MEMES),
                KeyboardButton(text=ButtonText.STICKERS),
                KeyboardButton(text=ButtonText.GAMES),
            ],
            _back_row(ButtonText.MAIN_MENU),
        ],
        resize_keyboard=True,
    )


def get_games_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ButtonText.RPS),
                KeyboardButton(text=ButtonText.BLACKJACK),
                KeyboardButton(text=ButtonText.BLOCK_ME),
            ],
            [
                KeyboardButton(text=ButtonText.BATTLESHIP),
                KeyboardButton(text=ButtonText.FIVE_CATS),
                KeyboardButton(text=ButtonText.EMOJI),
            ],
            _back_row(ButtonText.BACK),
        ],
        resize_keyboard=True,
    )


def get_games_emoji_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ButtonText.DICE),
                KeyboardButton(text=ButtonText.DART),
                KeyboardButton(text=ButtonText.CASINO),
            ],
            [
                KeyboardButton(text=ButtonText.FOOTBALL),
                KeyboardButton(text=ButtonText.BASKETBALL),
                KeyboardButton(text=ButtonText.BOWLING),
            ],
            _back_row(ButtonText.BACK_TO_GAMES, ButtonText.BACK),
        ],
        resize_keyboard=True,
    )


def get_actions_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="🌍 Send Location",
        request_location=True,
    )
    builder.button(
        text="📱 Send My Phone",
        request_contact=True,
    )
    builder.button(
        text="📊 Send Poll",
        request_poll=KeyboardButtonPollType(),
    )
    builder.button(
        text="❓ Send Quiz",
        request_poll=KeyboardButtonPollType(type="quiz"),
    )
    builder.button(
        text="❔ Regular Quiz",
        request_poll=KeyboardButtonPollType(type="regular"),
    )
    builder.button(text=ButtonText.BACK)
    builder.button(text=ButtonText.BYE)
    builder.adjust(1)
    return builder.as_markup(
        input_field_placeholder="Actions:",
        resize_keyboard=True,
    )


def build_yes_or_no_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Yes")
    builder.button(text="No")
    builder.button(text=ButtonText.BACK)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
