import os

from aiogram import Bot
from aiogram import Router, F
from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv

from keyboards.on_start import ButtonText

bot_token = os.getenv('BOT_TOKEN')

load_dotenv()

bot = Bot(token=bot_token)
dp = Dispatcher()

router = Router(name=__name__)


# CALCULATOR ===========================================================================================================
@router.message(F.text == ButtonText.CALCULATOR)
async def handle_calculator_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to count with me,\n"
             "click /calculator any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("calculator", prefix="/!%"))
async def send_welcome(message: types.Message):
    await message.reply(
        "Hi!\nI'm a calculator bot. "
        "\nYou can perform calculations by sending me commands like: "
        "\n/add 5 3, "
        "\n/subtract 7 2, "
        "\n/multiply 4 6, "
        "\n/divide 8 2."
        "\nPlease, use only integer numbers!"
    )


# Function to create a row of calculator operation buttons
def make_row_calculator_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(
        keyboard=[row],
        resize_keyboard=True,
    )


# Command handler for /calculator
@router.message(Command("calculator", prefix="/!%"))
async def send_welcome(message: types.Message):
    calculator_operations = [
        "/add",
        "/subtract",
        "/multiply",
        "/divide",
    ]
    keyboard = make_row_calculator_keyboard(calculator_operations)
    await message.reply("Choose a calculator operation:", reply_markup=keyboard)


# Command handler for each operation
@router.message(Command("add", prefix="/!%"))
async def add(message: types.Message):
    await process_operation(message, '+')


@router.message(Command("subtract", prefix="/!%"))
async def subtract(message: types.Message):
    await process_operation(message, '-')


@router.message(Command("multiply", prefix="/!%"))
async def multiply(message: types.Message):
    await process_operation(message, '*')


@router.message(Command("divide", prefix="/!%"))
async def divide(message: types.Message):
    await process_operation(message, '/')


# Function to process the operation and provide the result
async def process_operation(message: types.Message, operator: str):
    try:
        command, num1, num2 = message.text.split()
        num1 = float(num1)
        num2 = float(num2)
    except ValueError:
        await message.reply("Invalid input. Please provide two numbers UwU")
        return

    result = None
    if operator == '+':
        result = round(num1 + num2)
    elif operator == '-':
        result = round(num1 - num2)
    elif operator == '*':
        result = round(num1 * num2)
    elif operator == '/':
        if num2 != 0:
            result = num1 / num2
        else:
            await message.reply("Division by zero is not allowed.")
            return

    await message.reply(f"Result: {result}")


# CONVERTER ============================================================================================================
conversion_functions = {
    "/inches_to_cm": lambda x: x * 2.54,
    "/cm_to_inches": lambda x: x / 2.54,

    "/miles_to_km": lambda x: x * 1.60934,
    "/km_to_miles": lambda x: x / 1.60934,

    "/pounds_to_kg": lambda x: x * 0.453592,
    "/kg_to_pounds": lambda x: x / 0.453592,

    "/fahrenheit_to_celsius": lambda x: (x - 32) * 5 / 9,
    "/celsius_to_fahrenheit": lambda x: (x * 9 / 5) + 32,

    "/ounces_to_ml": lambda x: x * 29.5735,
    "/ml_to_ounces": lambda x: x / 29.5735,

    "/gallons_to_liters": lambda x: x * 3.78541,
    "/liters_to_gallons": lambda x: x / 3.78541,

    "/feet_to_meters": lambda x: x * 0.3048,
    "/meters_to_feet": lambda x: x / 0.3048,

    "/yards_to_meters": lambda x: x * 0.9144,
    "/meters_to_yards": lambda x: x / 0.9144,

    "/cups_to_liters": lambda x: x * 0.236588,
    "/liters_to_cups": lambda x: x / 0.236588,
}


def create_keyboard(commands):
    buttons_row_1 = [
        InlineKeyboardButton(
            text="INCHES",
            callback_data="/inches_options"
        ),

        InlineKeyboardButton(
            text="MILES",
            callback_data="/miles_options"
        ),

        InlineKeyboardButton(
            text="POUNDS",
            callback_data="/pounds_options"
        ),

    ]
    buttons_row_2 = [
        InlineKeyboardButton(
            text="F°",
            callback_data="/fahrenheit_options"
        ),

        InlineKeyboardButton(
            text="OUNCES",
            callback_data="/ounces_options"
        ),

        InlineKeyboardButton(
            text="GALLONS",
            callback_data="/gallons_options"
        ),

    ]
    buttons_row_3 = [
        InlineKeyboardButton(
            text="FEET",
            callback_data="/feet_options"
        ),

        InlineKeyboardButton(
            text="YARDS",
            callback_data="/yards_options"
        ),

        InlineKeyboardButton(
            text="CUPS",
            callback_data="/cups_options"
        ),

    ]
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons_row_1,
        buttons_row_2,
        buttons_row_3,
    ])


additional_keyboards = {
    "/inches_options": [
        InlineKeyboardButton(
            text="Inches to Centimeters",
            callback_data="/inches_to_cm"
        ),

        InlineKeyboardButton(
            text="Centimeters to Inches",
            callback_data="/cm_to_inches"
        ),

    ],
    "/miles_options": [
        InlineKeyboardButton(
            text="Miles to Kilometers",
            callback_data="/miles_to_km"
        ),

        InlineKeyboardButton(
            text="Kilometers to Miles",
            callback_data="/km_to_miles"
        ),

    ],
    "/pounds_options": [
        InlineKeyboardButton(
            text="Pounds to Kilograms",
            callback_data="/pounds_to_kg"
        ),

        InlineKeyboardButton(
            text="Kilograms to Pounds",
            callback_data="/kg_to_pounds"
        ),

    ],
    "/fahrenheit_options": [
        InlineKeyboardButton(
            text="Fahrenheit to Celsius",
            callback_data="/fahrenheit_to_celsius"
        ),

        InlineKeyboardButton(
            text="Celsius to Fahrenheit",
            callback_data="/celsius_to_fahrenheit"
        ),

    ],
    "/ounces_options": [
        InlineKeyboardButton(
            text="Ounces to Milliliters",
            callback_data="/ounces_to_ml"
        ),

        InlineKeyboardButton(
            text="Milliliters to Ounces",
            callback_data="/ml_to_ounces"
        ),

    ],
    "/gallons_options": [
        InlineKeyboardButton(
            text="Gallons to Liters",
            callback_data="/gallons_to_liters"
        ),

        InlineKeyboardButton(
            text="Liters to Gallons",
            callback_data="/liters_to_gallons"
        ),

    ],
    "/feet_options": [
        InlineKeyboardButton(
            text="Feet to Meters",
            callback_data="/feet_to_meters"
        ),

        InlineKeyboardButton(
            text="Meters to Feet",
            callback_data="/meters_to_feet"
        ),

    ],
    "/yards_options": [
        InlineKeyboardButton(
            text="Yards to Meters",
            callback_data="/yards_to_meters"
        ),

        InlineKeyboardButton(
            text="Meters to Yards",
            callback_data="/meters_to_yards"
        ),

    ],
    "/cups_options": [
        InlineKeyboardButton(
            text="Cups to Liters",
            callback_data="/cups_to_liters"
        ),

        InlineKeyboardButton(
            text="Liters to Cups",
            callback_data="/liters_to_cups"
        ),
    ],
}


@router.message(F.text == ButtonText.CONVERTER)
async def handle_converter_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to use converter,\n"
             "click /converter any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("converter", prefix="/!%"))
async def converter_menu(message: types.Message):
    keyboard = create_keyboard(list(additional_keyboards.keys()))
    await message.reply("Choose a conversion:", reply_markup=keyboard)


last_conversion_command = None


@router.callback_query(lambda c: c.data in additional_keyboards or c.data in conversion_functions)
async def handle_conversion_query(callback_query: types.CallbackQuery):
    global last_conversion_command
    conversion_command = callback_query.data
    if conversion_command in additional_keyboards:
        last_conversion_command = conversion_command
        keyboard = InlineKeyboardMarkup(inline_keyboard=[additional_keyboards[conversion_command]])
        await callback_query.message.answer("Choose an option:", reply_markup=keyboard)
    elif conversion_command in conversion_functions:
        last_conversion_command = conversion_command
        await callback_query.message.answer("Please enter the value to convert for " + conversion_command + ":")
    else:
        await callback_query.message.answer("Invalid conversion option!")


@router.message(
    lambda message: message.text and message.text.strip().replace('.', '', 1).isdigit()
                    and last_conversion_command is not None
)
async def handle_numbers(message: types.Message):
    if last_conversion_command in conversion_functions:
        try:
            number = float(message.text)
            result = conversion_functions[last_conversion_command](number)
            rounded_result = round(result, 1)
            additional_info = {
                "/inches_to_cm": f"Your result is {rounded_result} cm.",
                "/cm_to_inches": f"Your result is {rounded_result} inches.",

                "/miles_to_km": f"Your result is {rounded_result} km.",
                "/km_to_miles": f"Your result is {rounded_result} miles.",

                "/pounds_to_kg": f"Your result is {rounded_result} kg.",
                "/kg_to_pounds": f"Your result is {rounded_result} pounds.",

                "/fahrenheit_to_celsius": f"Your result is {rounded_result} °C.",
                "/celsius_to_fahrenheit": f"Your result is {rounded_result} °F.",

                "/ounces_to_ml": f"Your result is {rounded_result} mL.",
                "/ml_to_ounces": f"Your result is {rounded_result} ounces.",

                "/gallons_to_liters": f"Your result is {rounded_result} liters.",
                "/liters_to_gallons": f"Your result is {rounded_result} gallons.",

                "/feet_to_meters": f"Your result is {rounded_result} meters.",
                "/meters_to_feet": f"Your result is {rounded_result} feet.",

                "/yards_to_meters": f"Your result is {rounded_result} meters.",
                "/meters_to_yards": f"Your result is {rounded_result} yards.",

                "/cups_to_liters": f"Your result is {rounded_result} liters.",
                "/liters_to_cups": f"Your result is {rounded_result} cups.",
            }
            additional_info_text = additional_info.get(last_conversion_command, "")
            await message.reply(additional_info_text)
        except ValueError:
            await message.reply("Invalid input. Please enter a valid number.")
    else:
        await message.reply("Please enter a valid conversion command first.")
