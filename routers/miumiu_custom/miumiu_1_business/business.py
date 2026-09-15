import datetime
import json
from datetime import datetime, timedelta
from typing import Dict
from typing import List

import httpx
import pytz
import requests
from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import settings
from keyboards.on_start import ButtonText, get_on_help_kb, get_on_start_kb

forecast_api = settings.weather_api_token
nasa_api = settings.nasa_api_token
open_exchange = settings.open_exchange_token
big_poco = settings.yandex_id_admin
yandex_api_key = settings.yandex_api_key

data_amount = 0

router = Router(name=__name__)

weather_translations = {
    'Clouds': 'Облачно',
    'Rain': 'Дождь',
    'Snow': 'Снег',
    'Clear': 'Ясно',
    'Haze': 'Туманность',
    'Thunderstorm': 'Гроза',
}

weather_stickers = {
    'Clear': {
        'Утро': 'CAACAgIAAxkBAUDB12XhRMzJqlfh6bg0AU79cYy6Dj_IAALQTAACcSwJSzt9H5-I732HNAQ',
        'День': 'CAACAgIAAxkBAUDBumXhRLi-4D1H43ATD0L1sQ5HhlayAAL-RAAC8fcAAUvf1wyCaqkS_TQE',
        'Вечер': 'CAACAgIAAxkBAUDD2WXhSYxNazCT1hrLpiH3y_GnsLyUAAIYPAACCK4ISzqitpbMjvkxNAQ',
        'Ночь': 'CAACAgIAAxkBAUDB1WXhRMyBxsb7-_XlM4nIuZ4O0qF5AAIxQgACoYgISxirdYdDDa4oNAQ',
    },
    'Rain': 'CAACAgIAAxkBAUDBzmXhRMRBmY92FRMRI9JK_draMYp9AAKUSQACkYcJSw5Yj8ylF0UlNAQ',
    'Snow': 'CAACAgIAAxkBAUDB0GXhRMTa0qg4xyt7pe1vbm09yVgVAAIjSgACXqgAAUt2KFQ_2fGcvDQE',
    'Clouds': 'CAACAgIAAxkBAUDBzGXhRMI9efQqeoUPB0D4uc_7JzeIAAIVPgACECAAAUtq2Fb4XBOYljQE',
    'Haze': 'CAACAgIAAxkBAUQ2vWXu-ZD0GfGckxR7DftiETUJv1QPAALYRQACEhF5SwJG5A-JLtxBNAQ',
    'Thunderstorm': 'CAACAgIAAxkBAUQ3JWXu-33Dzxg33jkftlwk4Ua1g9FrAAKtQQACOb94Sw6ttB1BXQOCNAQ',
}


class WeatherQuery(StatesGroup):
    WaitingForCity = State()


class Questioning(StatesGroup):
    Asking = State()


city_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="/weather Москва"),
        KeyboardButton(text=ButtonText.BACK),
    ]
])


@router.message(F.text == ButtonText.WEATHER)
@router.message(Command("weather_start", prefix="/!%"))
async def weather_start(message: Message, state: FSMContext):
    await message.answer(
        text="Привет! Нажмите кнопку, чтобы выбрать погоду в Москве,\n"
             "либо введите вручную /weather Город,\n"
             "чтобы узнать температуру в другом городе!",
        reply_markup=city_keyboard,
    )
    await state.set_state(WeatherQuery.WaitingForCity)


@router.message(WeatherQuery.WaitingForCity, F.text == ButtonText.BACK)
async def weather_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(WeatherQuery.WaitingForCity, F.text)
async def ask_city(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text in {ButtonText.BACK, ButtonText.MAIN_MENU}:
        await state.clear()
        await message.answer("Back to menu :3", reply_markup=get_on_help_kb())
        return
    if text.startswith("/weather"):
        parts = text.split(maxsplit=1)
        city = parts[1] if len(parts) > 1 else "Москва"
    else:
        city = text
    await get_weather(message, city)
    await state.clear()


@router.message(Command("weather"))
async def get_weather_command(message: types.Message, state: FSMContext):
    command_parts = (message.text or "").split(maxsplit=1)
    if len(command_parts) > 1:
        await get_weather(message, command_parts[1])
        await state.clear()
        return
    await weather_start(message, state)


async def get_weather(message: types.Message, city: str):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={forecast_api}&units=metric"
    )
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(url)
    except httpx.HTTPError as exc:
        print(f"Weather HTTP error: {exc}")
        await message.reply("Не удалось получить погоду. Попробуйте позже.")
        return

    if res.status_code != 200:
        print(f"Ошибка при запросе: {res.status_code}")
        await message.reply(
            "Такого города нет. Введите существующий город, пожалуйста.",
            reply_markup=get_on_help_kb(),
        )
        return

    data = res.json()
    temp = data["main"]["temp"]
    pressure_hPa = data["main"]["pressure"]
    pressure_mmHg = round(pressure_hPa * 0.750062, 2)

    if pressure_mmHg > 755:
        pressure_message = "Повышенное"
    elif pressure_mmHg > 730:
        pressure_message = "Умеренное"
    else:
        pressure_message = "Пониженное"

    weather_kind = data["weather"][0]["main"]

    timezone_offset = timedelta(seconds=data["timezone"])
    city_timezone = pytz.FixedOffset(int(timezone_offset.total_seconds() / 60))
    local_time = datetime.now(city_timezone)

    if 6 <= local_time.hour < 12:
        current_time_range = "Утро"
    elif 12 <= local_time.hour < 18:
        current_time_range = "День"
    elif 18 <= local_time.hour < 24:
        current_time_range = "Вечер"
    else:
        current_time_range = "Ночь"

    current_time_str = local_time.strftime("%H:%M")

    sticker_entry = weather_stickers.get(weather_kind)
    sticker_id = None
    if isinstance(sticker_entry, dict):
        sticker_id = sticker_entry.get(current_time_range)
    elif isinstance(sticker_entry, str):
        sticker_id = sticker_entry

    if sticker_id:
        await message.answer_sticker(sticker_id)

    await message.reply(
        f"Температура сейчас: {temp}°C\n"
        f"{pressure_message} давление: {pressure_mmHg} мм рт ст\n"
        f"Местное время суток: {current_time_range}, {current_time_str}\n"
        f"{weather_translations.get(weather_kind, weather_kind)}",
        reply_markup=get_on_help_kb(),
    )


# NASA - MAGNETIC SOLAR STORMS =========================================================================================
async def fetch_geomagnetic_storm_data(nasa_api: str) -> List[Dict]:
    """Fetch geomagnetic storm data from NASA API."""
    url = "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/GST"
    params = {'mostRecent': 'true'}
    headers = {'Authorization': f'Bearer {nasa_api}'}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print("Error: HTTP status code", response.status_code)
                print("Requested URL:", response.url)
                return None
    except httpx.HTTPError as e:
        print("HTTP error fetching data:", e)
        return None


async def format_geomagnetic_storm_data(storm_info: List[Dict]) -> str:
    """Format geomagnetic storm data for display."""
    formatted_message = "Магнитные бури:\n\n"

    if storm_info:
        sorted_storms = sorted(storm_info, key=lambda x: x.get('startTime'), reverse=True)
        recent_storm = sorted_storms[0]

        gst_id = recent_storm.get('gstID')
        start_time = recent_storm.get('startTime')
        kp_index_data = recent_storm.get('allKpIndex', [{'kpIndex': 'N/A', 'source': 'N/A'}])[0]
        kp_index = kp_index_data.get('kpIndex', 'N/A')
        source = kp_index_data.get('source', 'N/A')
        link = recent_storm.get('link')

        formatted_storm = (
            f"ID бури: {gst_id}\n"
            f"Начало: {start_time}\n"
            f"Kp индекс: {kp_index}\n"
            f"Источник: {source}\n"
            f"Ссылка: {link}\n\n"
        )
        formatted_message += formatted_storm
    else:
        formatted_message += "Увы, нет данных о магнитных бурях."

    return formatted_message


async def send_long_message(message: types.Message, text: str):
    """Send a long message by splitting it into parts."""
    max_length = 4096
    if len(text) <= max_length:
        await message.reply(text)
    else:
        parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        for part in parts:
            await message.reply(part)


async def get_magnetic_storm_data(message: types.Message, nasa_api: str):
    geomagnetic_storm_info = await fetch_geomagnetic_storm_data(nasa_api)
    formatted_storm_message = await format_geomagnetic_storm_data(geomagnetic_storm_info)
    await send_long_message(message, formatted_storm_message)


@router.message(F.text == ButtonText.MAGNETIC_STORM)
@router.message(Command("magnetic_storm", prefix="!/"))
async def get_magnetic_storm_command(message: types.Message):
    await get_magnetic_storm_data(message, nasa_api)


# YandexGPT ============================================================================================================
class Danila(StatesGroup):
    Yandex_GPT = State()


yandex_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers_yandex_gpt = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {yandex_api_key}"
}


@router.message(F.text.in_({ButtonText.YANDEX_GPT, ButtonText.ALICE}))
@router.message(Command("ask_miumiu_gpt", prefix="/!%"))
async def ask_miumiu_gpt(message: Message, state: FSMContext):
    alice_kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(text=ButtonText.BACK)]],
    )
    await message.answer(
        "Привет! Задайте ваш вопрос :3\n"
        "Пожалуйста, не обижайте меня и не задавайте грубые вопросы 😸\n"
        "You may now ask your question /ᐠ｡ꞈ｡ᐟ\\ﾉ\n"
        "Don't be mean and don't ask violent or forbidden questions :c\n"
        f"(or tap {ButtonText.BACK} / /cancel)",
        reply_markup=alice_kb,
    )
    await state.set_state(Danila.Yandex_GPT)


@router.message(Danila.Yandex_GPT, F.text.in_({ButtonText.BACK, ButtonText.MAIN_MENU, "/cancel"}))
async def cancel_alice(message: Message, state: FSMContext):
    await state.clear()
    kb = get_on_start_kb() if message.text == ButtonText.MAIN_MENU else get_on_help_kb()
    await message.answer("Ок, выходим из чата с Алисой :3", reply_markup=kb)


@router.message(Danila.Yandex_GPT)
async def handle_user_input(message: Message, state: FSMContext):
    await message.answer("Подождите пожалуйста, обрабатываю запрос ^w^")

    message_for_yandex = {
        "modelUri": f"gpt://{big_poco}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.4,
            "maxTokens": "2000",
        },
        "messages": [
            {
                "role": "user",
                "text": message.text,
            },
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response_yandex_gpt = await client.post(
                yandex_url, headers=headers_yandex_gpt, json=message_for_yandex
            )
            result_yandex_gpt = response_yandex_gpt.json()
    except httpx.HTTPError as exc:
        print(f"Yandex GPT HTTP error: {exc}")
        await state.clear()
        await message.answer(
            "Не удалось связаться с Алисой. Попробуйте позже.",
            reply_markup=get_on_help_kb(),
        )
        return

    print("Yandex GPT Response:", result_yandex_gpt)

    try:
        yandex_response = result_yandex_gpt["result"]["alternatives"][0]["message"]["text"]
        await message.answer(yandex_response)
    except (KeyError, TypeError, IndexError):
        await message.answer("Error: Unable to fetch response.")
    finally:
        await state.clear()

    await message.answer(
        "Если нужно что-то ещё — нажми Alice / /ask_miumiu_gpt :3",
        reply_markup=get_on_help_kb(),
    )


# CURRENCY CONVERTER ===================================================================================================
class ConversionStates(StatesGroup):
    AWAITING_AMOUNT = State()
    AWAITING_CURRENCY_PAIR = State()


@router.message(F.text == ButtonText.CURRENCY)
@router.message(Command("convert_money", prefix="/"))
async def start_conversion(message: Message, state: FSMContext):
    amount_kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[KeyboardButton(text=ButtonText.BACK)]],
    )
    await message.answer(
        "Welcome to the Currency Converter Bot!\n"
        "Please enter the amount to convert:",
        reply_markup=amount_kb,
    )
    await state.set_state(ConversionStates.AWAITING_AMOUNT)


@router.message(StateFilter(ConversionStates.AWAITING_AMOUNT), F.text == ButtonText.BACK)
async def currency_amount_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(StateFilter(ConversionStates.AWAITING_AMOUNT))
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
    except ValueError:
        await message.answer('Please enter a valid number')
        return

    if amount <= 0:
        await message.answer('Please enter a number greater than 0')
        return

    keyboard_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='USD/EUR'), KeyboardButton(text='EUR/USD'), KeyboardButton(text='USD/GBP')],
            [KeyboardButton(text='USD/RUB'), KeyboardButton(text='EUR/RUB'), KeyboardButton(text='HUF/RUB')],
            [KeyboardButton(text='RSD/RUB'), KeyboardButton(text='AMD/RUB'), KeyboardButton(text='CNY/RUB')],
            [KeyboardButton(text='JPY/RUB'), KeyboardButton(text='RUB/USD'), KeyboardButton(text='RUB/EUR')],
            [KeyboardButton(text='RUB/HUF'), KeyboardButton(text='RUB/RSD'), KeyboardButton(text='RUB/AMD')],
            [KeyboardButton(text='RUB/CNY'), KeyboardButton(text='RUB/JPY')],
            [KeyboardButton(text=ButtonText.BACK)],
        ])
    await message.answer('Please select the currency pair', reply_markup=keyboard_markup)

    await state.update_data(amount=amount)
    await state.set_state(ConversionStates.AWAITING_CURRENCY_PAIR)


@router.message(StateFilter(ConversionStates.AWAITING_CURRENCY_PAIR), F.text == ButtonText.BACK)
async def currency_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(StateFilter(ConversionStates.AWAITING_CURRENCY_PAIR))
async def process_currency_pair(message: types.Message, state: FSMContext):
    currency_pairs = {
        'USD/EUR': ('USD', 'EUR'),
        'EUR/USD': ('EUR', 'USD'),
        'USD/GBP': ('USD', 'GBP'),
        'USD/RUB': ('USD', 'RUB'),
        'EUR/RUB': ('EUR', 'RUB'),
        'HUF/RUB': ('HUF', 'RUB'),
        'RSD/RUB': ('RSD', 'RUB'),
        'AMD/RUB': ('AMD', 'RUB'),
        'CNY/RUB': ('CNY', 'RUB'),
        'JPY/RUB': ('JPY', 'RUB'),
        'RUB/USD': ('RUB', 'USD'),
        'RUB/EUR': ('RUB', 'EUR'),
        'RUB/HUF': ('RUB', 'HUF'),
        'RUB/RSD': ('RUB', 'RSD'),
        'RUB/AMD': ('RUB', 'AMD'),
        'RUB/CNY': ('RUB', 'CNY'),
        'RUB/JPY': ('RUB', 'JPY'),
    }

    selected_currency_pair = message.text.upper()

    if selected_currency_pair in currency_pairs:
        amount_data = await state.get_data()
        amount = amount_data.get('amount')
        currency_from, currency_to = currency_pairs[selected_currency_pair]

        exchange_rates = await fetch_exchange_rates()
        if exchange_rates:
            conversion_rate = exchange_rates.get(currency_to) / exchange_rates.get(currency_from)
            result = amount * conversion_rate
            await message.answer(f'Result: {round(result, 2)}. You can enter the amount again!\n'
                                 f'Press /convert_money here :3',
                                 reply_markup=get_on_help_kb())
            await state.clear()
        else:
            await message.answer('Failed to fetch exchange rates. Please try again later.')
    else:
        await message.answer('Invalid currency pair. Please select from the options provided.')


async def fetch_exchange_rates():
    base_url = "https://openexchangerates.org/api/"
    endpoint = "latest.json"
    url = f"{base_url}{endpoint}?app_id={open_exchange}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['rates']
            else:
                return None
    except httpx.HTTPError as exc:
        print(f"HTTP error occurred: {exc}")
        return None
