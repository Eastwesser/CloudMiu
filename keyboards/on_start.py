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
    WEATHER = "Weather"
    YANDEX_GPT = "YandexGPT"
    KANDINSKY = "Kandinsky"
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


def get_on_start_kb() -> ReplyKeyboardMarkup:
    button_hello = KeyboardButton(
        text=ButtonText.HELLO
    )
    button_help = KeyboardButton(
        text=ButtonText.WHATS_NEXT
    )
    button_bye = KeyboardButton(
        text=ButtonText.BYE
    )

    buttons_row_1 = [button_hello, button_help]
    buttons_row_2 = [button_bye]

    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            buttons_row_1,
            buttons_row_2,
        ],
        resize_keyboard=True,
    )
    return markup_keyboard


def get_on_help_kb() -> ReplyKeyboardMarkup:
    button_weather = KeyboardButton(
        text=ButtonText.WEATHER
    )
    button_yandex_gpt = KeyboardButton(
        text=ButtonText.YANDEX_GPT
    )
    button_kandinsky = KeyboardButton(
        text=ButtonText.KANDINSKY
    )

    button_currency = KeyboardButton(
        text=ButtonText.CURRENCY
    )
    button_calculator = KeyboardButton(
        text=ButtonText.CALCULATOR
    )
    button_converter = KeyboardButton(
        text=ButtonText.CONVERTER
    )

    button_magnetic_storm = KeyboardButton(
        text=ButtonText.MAGNETIC_STORM
    )
    button_python_presentation = KeyboardButton(
        text=ButtonText.PYTHON_PRESENTATION
    )
    button_video_to_mp3 = KeyboardButton(
        text=ButtonText.VIDEO_TO_MP3
    )

    button_memes = KeyboardButton(
        text=ButtonText.MEMES
    )
    button_stickers = KeyboardButton(
        text=ButtonText.STICKERS
    )
    button_games = KeyboardButton(
        text=ButtonText.GAMES
    )

    buttons_row_1 = [button_weather, button_yandex_gpt, button_kandinsky]
    buttons_row_2 = [button_currency, button_calculator, button_converter]
    buttons_row_3 = [button_magnetic_storm, button_python_presentation, button_video_to_mp3]
    buttons_row_4 = [button_memes, button_stickers, button_games]

    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            buttons_row_1,
            buttons_row_2,
            buttons_row_3,
            buttons_row_4,
        ],
        resize_keyboard=True,
    )
    return markup_keyboard


def get_games_kb() -> ReplyKeyboardMarkup:
    button_rps = KeyboardButton(
        text=ButtonText.RPS
    )
    button_blackjack = KeyboardButton(
        text=ButtonText.BLACKJACK
    )
    button_blockme = KeyboardButton(
        text=ButtonText.BLOCK_ME
    )

    button_battleship = KeyboardButton(
        text=ButtonText.BATTLESHIP
    )
    button_five_cats = KeyboardButton(
        text=ButtonText.FIVE_CATS
    )
    button_emoji = KeyboardButton(
        text=ButtonText.EMOJI
    )

    buttons_row_1 = [button_rps, button_blackjack, button_blockme]
    buttons_row_2 = [button_battleship, button_five_cats, button_emoji]

    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[buttons_row_1,
                  buttons_row_2],
        resize_keyboard=True,
    )
    return markup_keyboard


def get_games_emoji_kb() -> ReplyKeyboardMarkup:
    button_dice = KeyboardButton(
        text=ButtonText.DICE
    )
    button_darts = KeyboardButton(
        text=ButtonText.DART
    )
    button_casino = KeyboardButton(
        text=ButtonText.CASINO
    )

    button_football = KeyboardButton(
        text=ButtonText.FOOTBALL
    )
    button_basketball = KeyboardButton(
        text=ButtonText.BASKETBALL
    )
    button_bowling = KeyboardButton(
        text=ButtonText.BOWLING
    )

    buttons_row_1 = [button_dice, button_darts, button_casino]
    buttons_row_2 = [button_football, button_basketball, button_bowling]

    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[buttons_row_1,
                  buttons_row_2],
        resize_keyboard=True,
    )
    return markup_keyboard


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
    builder.button(
        text=ButtonText.BYE,
    )
    builder.adjust(1)
    return builder.as_markup(
        input_field_placeholder="Actions:",
        resize_keyboard=True,
    )


def build_yes_or_no_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Yes")
    builder.button(text="No")
    # builder.adjust(10)
    return builder.as_markup(resize_keyboard=True)
