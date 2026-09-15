from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from keyboards.on_start import ButtonText, get_on_help_kb

router = Router(name=__name__)


# CALCULATOR ===========================================================================================================
class CalcStates(StatesGroup):
    waiting_numbers = State()


OP_SYMBOLS = {
    "add": "+",
    "subtract": "-",
    "multiply": "*",
    "divide": "/",
}


def make_row_calculator_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(
        keyboard=[row, [KeyboardButton(text=ButtonText.BACK)]],
        resize_keyboard=True,
    )


@router.message(F.text == ButtonText.CALCULATOR)
@router.message(Command("calculator", prefix="/!%"))
async def send_welcome(message: types.Message, state: FSMContext):
    await state.clear()
    calculator_operations = ["Add", "Subtract", "Multiply", "Divide"]
    keyboard = make_row_calculator_keyboard(calculator_operations)
    await message.reply(
        "Calculator\n"
        "Tap an operation, then send two numbers like: `5 3`\n"
        "Or type: /add 5 3",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.message(F.text.in_({"Add", "Subtract", "Multiply", "Divide"}))
async def pick_calc_op(message: types.Message, state: FSMContext):
    op = message.text.lower()
    await state.set_state(CalcStates.waiting_numbers)
    await state.update_data(op=op)
    await message.answer(f"Send two numbers for {message.text}, e.g. `12 4`", parse_mode="Markdown")


@router.message(CalcStates.waiting_numbers, F.text == ButtonText.BACK)
async def calc_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(CalcStates.waiting_numbers)
async def calc_numbers(message: types.Message, state: FSMContext):
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.reply("Please send exactly two numbers, e.g. 12 4")
        return
    try:
        num1 = float(parts[0])
        num2 = float(parts[1])
    except ValueError:
        await message.reply("Invalid numbers. Try again, e.g. 12 4")
        return

    data = await state.get_data()
    op = data.get("op", "add")
    symbol = OP_SYMBOLS.get(op, "+")
    await state.clear()
    await _compute_and_reply(message, symbol, num1, num2)


@router.message(Command("add", prefix="/!%"))
async def add(message: types.Message, state: FSMContext):
    await process_operation(message, "+", state)


@router.message(Command("subtract", prefix="/!%"))
async def subtract(message: types.Message, state: FSMContext):
    await process_operation(message, "-", state)


@router.message(Command("multiply", prefix="/!%"))
async def multiply(message: types.Message, state: FSMContext):
    await process_operation(message, "*", state)


@router.message(Command("divide", prefix="/!%"))
async def divide(message: types.Message, state: FSMContext):
    await process_operation(message, "/", state)


async def process_operation(message: types.Message, operator: str, state: Optional[FSMContext] = None):
    parts = (message.text or "").split()
    if len(parts) < 3:
        op_name = { "+": "add", "-": "subtract", "*": "multiply", "/": "divide" }[operator]
        if state is not None:
            await state.set_state(CalcStates.waiting_numbers)
            await state.update_data(op=op_name)
        await message.reply(f"Send two numbers for {operator}, e.g. 5 3")
        return
    try:
        num1 = float(parts[1])
        num2 = float(parts[2])
    except ValueError:
        await message.reply("Invalid input. Please provide two numbers UwU")
        return
    if state is not None:
        await state.clear()
    await _compute_and_reply(message, operator, num1, num2)


async def _compute_and_reply(message: types.Message, operator: str, num1: float, num2: float):
    if operator == "+":
        result = round(num1 + num2)
    elif operator == "-":
        result = round(num1 - num2)
    elif operator == "*":
        result = round(num1 * num2)
    elif operator == "/":
        if num2 == 0:
            await message.reply("Division by zero is not allowed.")
            return
        result = num1 / num2
    else:
        await message.reply("Unknown operation")
        return
    await message.reply(f"Result: {result}", reply_markup=get_on_help_kb())


@router.message(F.text == ButtonText.BACK)
async def mathix_back_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Back to help menu :3", reply_markup=get_on_help_kb())


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
@router.message(Command("converter", prefix="/!%"))
async def converter_menu(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = create_keyboard(list(additional_keyboards.keys()))
    await message.reply("Choose a conversion:", reply_markup=keyboard)


class UnitConvertStates(StatesGroup):
    waiting_value = State()


ADDITIONAL_INFO = {
    "/inches_to_cm": "cm",
    "/cm_to_inches": "inches",
    "/miles_to_km": "km",
    "/km_to_miles": "miles",
    "/pounds_to_kg": "kg",
    "/kg_to_pounds": "pounds",
    "/fahrenheit_to_celsius": "°C",
    "/celsius_to_fahrenheit": "°F",
    "/ounces_to_ml": "mL",
    "/ml_to_ounces": "ounces",
    "/gallons_to_liters": "liters",
    "/liters_to_gallons": "gallons",
    "/feet_to_meters": "meters",
    "/meters_to_feet": "feet",
    "/yards_to_meters": "meters",
    "/meters_to_yards": "yards",
    "/cups_to_liters": "liters",
    "/liters_to_cups": "cups",
}


@router.callback_query(lambda c: c.data in additional_keyboards or c.data in conversion_functions)
async def handle_conversion_query(callback_query: types.CallbackQuery, state: FSMContext):
    conversion_command = callback_query.data
    await callback_query.answer()
    if conversion_command in additional_keyboards:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[additional_keyboards[conversion_command]]
        )
        await callback_query.message.answer("Choose an option:", reply_markup=keyboard)
    elif conversion_command in conversion_functions:
        await state.set_state(UnitConvertStates.waiting_value)
        await state.update_data(conversion_command=conversion_command)
        await callback_query.message.answer(
            f"Enter the value to convert for {conversion_command}:"
        )
    else:
        await callback_query.message.answer("Invalid conversion option!")


@router.message(StateFilter(UnitConvertStates.waiting_value), F.text == ButtonText.BACK)
async def unit_convert_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Back to menu :3", reply_markup=get_on_help_kb())


@router.message(StateFilter(UnitConvertStates.waiting_value))
async def handle_conversion_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conversion_command = data.get("conversion_command")
    if conversion_command not in conversion_functions:
        await state.clear()
        await message.reply("Please choose a conversion from the menu first.")
        return
    try:
        number = float((message.text or "").strip())
    except ValueError:
        await message.reply("Invalid input. Please enter a valid number.")
        return

    result = conversion_functions[conversion_command](number)
    rounded_result = round(result, 1)
    unit = ADDITIONAL_INFO.get(conversion_command, "")
    await state.clear()
    await message.reply(
        f"Your result is {rounded_result} {unit}.",
        reply_markup=get_on_help_kb(),
    )
