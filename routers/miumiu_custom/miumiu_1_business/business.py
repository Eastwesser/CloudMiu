import datetime
import json
import os
from datetime import datetime, timedelta
from typing import Dict
from typing import List

import httpx
import pytz
import requests
from aiogram import Bot, Router, F
from aiogram import types, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv

from keyboards.on_start import ButtonText

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
forecast_api = os.getenv('WEATHER_API_TOKEN')
nasa_api = os.getenv('NASA_API_TOKEN')
open_exchange = os.getenv('OPEN_EXCHANGE_TOKEN')
big_poco = os.getenv('YANDEX_ID_ADMIN')
yandex_api_key = os.getenv('YANDEX_API_KEY')

bot = Bot(token=bot_token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

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


storage = MemoryStorage()

city_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="/weather Москва")
    ]
])


@router.message(F.text == ButtonText.WEATHER)
async def handle_weather_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to ask me about the weather,\n"
             "click /weather_start any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("weather_start", prefix="/!%"))
async def weather_start(message: Message, state: FSMContext):
    await message.answer(
        text="Привет! Нажмите кнопку, чтобы выбрать погоду в Москве,\n"
             "либо введите вручную /weather Город,\n"
             "чтобы узнать температуру в другом городе!",
        reply_markup=city_keyboard,
    )
    await state.set_state(WeatherQuery.WaitingForCity)


@router.message(WeatherQuery.WaitingForCity, F.text.in_(city_keyboard))
async def ask_city(message: Message, state: FSMContext):
    await state.update_data(ask_city=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, введите название города:",
        reply_markup=city_keyboard,
    )
    await state.set_state(WeatherQuery.WaitingForCity)


@router.message(Command("weather"))
async def get_weather_command(message: types.Message):
    print("Weather command received!")
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) > 1:
        city = command_parts[1]
        print("City:", city)
        await get_weather(message, city)
    else:
        await message.reply("Please specify a city after the command.")


async def get_weather(message: types.Message, city: str):
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={forecast_api}&units=metric'
    )
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data['main']['temp']
        pressure_hPa = data['main']['pressure']
        pressure_mmHg = round(pressure_hPa * 0.750062, 2)

        pressure_messages = {
            pressure_mmHg > 755: 'Повышенное',
            730 < pressure_mmHg <= 755: 'Умеренное',
            pressure_mmHg <= 730: 'Пониженное'
        }

        pressure_message = next((msg for condition, msg in pressure_messages.items() if condition),
                                'Данные о давлении недоступны!')

        weather_kind = data['weather'][0]['main']

        timezone_offset = timedelta(seconds=data['timezone'])
        city_timezone = pytz.FixedOffset(int(timezone_offset.total_seconds() / 60))
        local_time = datetime.now(city_timezone)

        if 6 <= local_time.hour < 12:
            current_time_range = 'Утро'
        elif 12 <= local_time.hour < 18:
            current_time_range = 'День'
        elif 18 <= local_time.hour < 24:
            current_time_range = 'Вечер'
        else:
            current_time_range = 'Ночь'

        current_time_str = local_time.strftime('%H:%M')

        if isinstance(weather_stickers[weather_kind], dict):
            sticker_id = weather_stickers[weather_kind].get(current_time_range)
        else:
            sticker_id = weather_stickers[weather_kind]

        if sticker_id:
            await message.answer_sticker(sticker_id)

        await message.reply(
            f"Температура сейчас: {temp}°C\n"
            f"{pressure_message} давление: {pressure_mmHg} мм рт ст\n"
            f"Местное время суток: {current_time_range}, {current_time_str}\n"
            f"{weather_translations.get(weather_kind, 'Ясно')}"
        )

    else:
        print(f"Ошибка при запросе: {res.status_code}")
        await message.reply("Такого города нет. Введите существующий город, пожалуйста.")


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
async def handle_magnetic_storm_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to ask me about the solar magnetic storms,\n"
             "click /magnetic_storm any time to ask NASA! >:3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("magnetic_storm", prefix="!/"))
async def get_magnetic_storm_command(message: types.Message):
    # Pass the nasa_api token here
    await get_magnetic_storm_data(message, nasa_api)


# YandexGPT ============================================================================================================
class Danila(StatesGroup):
    Yandex_GPT = State()


yandex_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers_yandex_gpt = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {yandex_api_key}"
}


@router.message(F.text == ButtonText.YANDEX_GPT)
async def handle_yandexgpt_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to ask me about something,\n"
             "click /ask_miumiu_gpt any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("ask_miumiu_gpt", prefix="/!%"))
async def ask_miumiu_gpt(message: Message, state: FSMContext):
    await message.answer(
        "Привет! Задайте ваш вопрос :3\n"
        "Пожалуйста, не обижайте меня и не задавайте грубые вопросы 😸\n"
        "You may now ask your question /ᐠ｡ꞈ｡ᐟ\ﾉ\n"
        "Don't be mean and don't ask violent or forbidden questions :c",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.set_state(Danila.Yandex_GPT)


@router.message(Danila.Yandex_GPT)
async def handle_user_input(message: Message, state: FSMContext):
    await message.answer("Подождите пожалуйста, обрабатываю запрос ^w^")

    current_state = await state.get_state()

    print("Current State:", current_state)

    if current_state == Danila.Yandex_GPT:
        message_for_yandex = {
            "modelUri": f"gpt://{big_poco}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.4,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "user",
                    "text": message.text
                },
            ]
        }

        response_yandex_gpt = requests.post(yandex_url, headers=headers_yandex_gpt, json=message_for_yandex)
        result_yandex_gpt = response_yandex_gpt.json()

        print("Yandex GPT Response:", result_yandex_gpt)

        try:
            yandex_response = result_yandex_gpt["result"]["alternatives"][0]["message"]["text"]
            await message.answer(yandex_response)
        except KeyError:
            await message.answer("Error: Unable to fetch response.")
        finally:
            await state.clear()
    else:
        await message.answer("Please initiate the conversation with /ask_miumiu_gpt first.")

    await message.answer("Если нужно что-то ещё, смело нажимай /ask_miumiu_gpt :3")


# CURRENCY CONVERTER ===================================================================================================
class ConversionStates(StatesGroup):
    AWAITING_AMOUNT = State()
    AWAITING_CURRENCY_PAIR = State()


@router.message(F.text == ButtonText.CURRENCY)
async def handle_currency_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to ask me about the currency,\n"
             "click /convert_money any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("convert_money", prefix="/"))
async def start_conversion(message: Message, state: FSMContext):
    await message.answer("Welcome to the Currency Converter Bot!\n"
                         "Please enter the amount to convert:")
    await state.set_state(ConversionStates.AWAITING_AMOUNT)


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
            [KeyboardButton(text='RUB/CNY'), KeyboardButton(text='RUB/JPY'), KeyboardButton(text='/convert_money')]
        ])
    await message.answer('Please select the currency pair', reply_markup=keyboard_markup)

    await state.update_data(amount=amount)
    await state.set_state(ConversionStates.AWAITING_CURRENCY_PAIR)


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
                                 f'Press /convert_money here :3')
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
