import asyncio
import copy
import random
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram import Router, types, F
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from keyboards.on_start import ButtonText

router = Router(name=__name__)

CHOICES = ["Rock", "Paper", "Scissors"]

WINS_REQUIRED = 3
BLACKJACK_FACES = ["❤️", "♠️", "♦️", "♣️"]
BLACKJACK_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

round_number = 1
health_p1 = 10
health_p2 = 10


def build_rps_keyboard() -> InlineKeyboardMarkup:
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=choice, callback_data=f"rps_{choice.lower()}")
            ] for choice in CHOICES
        ]
    )
    return keyboard_markup


@router.message(F.text == ButtonText.RPS)
async def handle_rps_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to play Rock-Paper-Scissors,\n"
             "click /rps any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("rps", prefix="!/"))
async def start_rps_game(message: types.Message):
    keyboard_markup = build_rps_keyboard()
    await message.answer("Choose your move:", reply_markup=keyboard_markup)


@router.callback_query(lambda callback_query: callback_query.data.startswith("rps_"))
async def process_rps_move(callback_query: types.CallbackQuery):
    user_choice = callback_query.data.split("_")[1].capitalize()
    bot_choice = random.choice(CHOICES)

    winner = determine_winner(user_choice, bot_choice)

    await callback_query.answer(f"Bot chose {bot_choice}. {winner}")


def determine_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "It's a tie!"
    elif (user_choice == "Rock" and bot_choice == "Scissors") or \
            (user_choice == "Paper" and bot_choice == "Rock") or \
            (user_choice == "Scissors" and bot_choice == "Paper"):
        return "You win!"
    else:
        return "Bot wins!"


# DICE EMOJI BOT =======================================================================================================
@router.message(F.text == ButtonText.BOWLING)
async def handle_bowling_message(message: types.Message):
    await message.answer(
        text="Nyan! Click /bowling any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("bowling", prefix="!/"))
async def play_games_bowling(message: Message):
    x = await message.answer_dice(DiceEmoji.BOWLING)
    print(x.dice.value)


@router.message(F.text == ButtonText.DICE)
async def handle_dice_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to throw a dice,\n"
             "Click /dice any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("dice", prefix="!/"))
async def play_games_dice(message: Message):
    x = await message.answer_dice(DiceEmoji.DICE)
    print(x.dice.value)


@router.message(F.text == ButtonText.CASINO)
async def handle_casino_message(message: types.Message):
    await message.answer(
        text="Mreow! Click /casino any time!\n"
             "Good luck >w^",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("casino", prefix="!/"))
async def play_games_casino(message: Message):
    x = await message.answer_dice(DiceEmoji.SLOT_MACHINE)
    print(x.dice.value)


@router.message(F.text == ButtonText.DART)
async def handle_dart_message(message: types.Message):
    await message.answer(
        text="Nya! Click /dart to throw a dart any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("dart", prefix="!/"))
async def play_games_dart(message: Message):
    x = await message.answer_dice(DiceEmoji.DART)
    print(x.dice.value)


@router.message(F.text == ButtonText.BASKETBALL)
async def handle_basketball_message(message: types.Message):
    await message.answer(
        text="Nyan! Click /basketball any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("basketball", prefix="!/"))
async def play_games_basketball(message: Message):
    x = await message.answer_dice(DiceEmoji.BASKETBALL)
    print(x.dice.value)


@router.message(F.text == ButtonText.FOOTBALL)
async def handle_football_message(message: types.Message):
    await message.answer(
        text="Mew! Click /football any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("football", prefix="!/"))
async def play_games_football(message: Message):
    x = await message.answer_dice(DiceEmoji.FOOTBALL)
    print(x.dice.value)


# BLACKJACK ============================================================================================================
class BlackjackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            message: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        result = await handler(message, data)
        return result


def deal_card():
    return random.choice(BLACKJACK_FACES), random.choice(BLACKJACK_VALUES)


player_hand = []
dealer_hand = []


@router.message(F.text == ButtonText.BLACKJACK)
async def handle_21_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to play Blackjack,\n"
             "click /start_blackjack any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("start_blackjack", prefix="!/"))
async def start_blackjack(message: types.Message):
    await message.answer("Hi! Welcome to Blackjack. Send /play21 to start playing.")


@router.message(Command("play21", prefix="!/"))
async def play_blackjack(message: types.Message):
    global player_hand, dealer_hand
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]

    player_score = calculate_hand_score(player_hand)
    dealer_score = calculate_hand_score(dealer_hand)

    player_message = f"Your hand: {player_hand}\nYour score: {player_score}"
    dealer_message = f"Dealer's hand: [{dealer_hand[0]}, ???]\nDealer's score: {dealer_hand[0][1]}"

    await message.answer(player_message)
    await message.answer(dealer_message)
    await message.answer("Type /hit to get a card or /stand to end your turn.")


@router.message(Command("hit", prefix="!/"))
async def hit_blackjack(message: types.Message):
    global player_hand
    card = deal_card()
    player_hand.append(card)

    player_score = calculate_hand_score(player_hand)
    await message.answer(f"You drew: {card}. Your score: {player_score}")

    if player_score > 21:
        await message.answer("You bust! Dealer wins.")
        reset_game()


@router.message(Command("stand", prefix="!/"))
async def stand_blackjack(message: types.Message):
    global dealer_hand
    while calculate_hand_score(dealer_hand) < 17:
        dealer_hand.append(deal_card())

    dealer_score = calculate_hand_score(dealer_hand)
    await message.answer(f"Dealer's hand: {dealer_hand}. Dealer's score: {dealer_score}")

    player_score = calculate_hand_score(player_hand)
    if player_score > 21 or player_score < dealer_score <= 21:
        await message.answer("Dealer wins!")
    elif dealer_score > 21 or player_score > dealer_score:
        await message.answer("You win!")
    elif player_score == dealer_score:
        await message.answer("It's a tie!")

    reset_game()


def calculate_hand_score(hand):
    score = 0
    ace_count = 0
    for card in hand:
        value = card[1]
        if value.isdigit():
            score += int(value)
        elif value in ('J', 'Q', 'K'):
            score += 10
        elif value == 'A':
            ace_count += 1
            score += 11
    while ace_count > 0 and score > 21:
        score -= 10
        ace_count -= 1
    return score


def reset_game():
    global player_hand, dealer_hand
    player_hand = []
    dealer_hand = []


# BLOCK ME =============================================================================================================
@router.message(F.text == ButtonText.BLOCK_ME)
async def handle_blockme_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to block my paws,\n"
             "click /start_block_me any time! >:3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("start_block_me", prefix="!/"))
async def start_blockme_game(message: types.Message):
    global round_number, health_p1, health_p2
    round_number = 1
    health_p1 = 10
    health_p2 = 10

    block_me_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="^", callback_data="hit_head"),
                InlineKeyboardButton(text=">", callback_data="hit_chest"),
                InlineKeyboardButton(text="v", callback_data="hit_legs")
            ]
        ]
    )

    await message.answer("Round 1. Player 2, choose an attack:", reply_markup=block_me_kb)


@router.callback_query(lambda callback_query: callback_query.data.startswith("hit_"))
async def process_blockme_attack(callback_query: types.CallbackQuery):
    global health_p1, health_p2, round_number
    choice_p2 = callback_query.data
    choice_p1 = random.choice(["hit_head", "hit_chest", "hit_legs"])

    if choice_p2 == choice_p1:
        round_result = "Player 1 defended successfully"
    elif (choice_p2 == "hit_head" and choice_p1 == "hit_legs") or \
            (choice_p2 == "hit_chest" and choice_p1 == "hit_legs") or \
            (choice_p2 == "hit_legs" and choice_p1 == "hit_head"):
        round_result = "Player 1 lost 2 health points"
        health_p1 -= 2
    else:
        round_result = "Player 1 lost 1 health point"
        health_p1 -= 1

    await callback_query.answer(f"{round_result}\n"
                                f"Player 1 health: {health_p1}\n"
                                f"Player 2 health: {health_p2}")

    if health_p1 <= 0:
        await callback_query.message.reply("Player 1 is defeated! GAME OVER")
    elif health_p2 <= 0:
        await callback_query.message.reply("Player 2 is defeated! GAME OVER")
    else:
        await asyncio.sleep(5)


# SEA BATTLE ===========================================================================================================
FIELD_SIZE = 8

LEXICON = {
    '/start': 'Вот твое поле. Можешь делать ход',
    '/start_naval': 'Your message for /start_naval command goes here',
    0: ' ',
    1: '🌊',
    2: '💥',
    'miss': 'Мимо!',
    'hit': 'Попал!',
    'used': 'Вы уже стреляли сюда!',
    'next_move': 'Делайте ваш следующий ход'
}

ships: list[list[int]] = [
    [1, 0, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0],
]

users: dict[int, dict[str, list]] = {}


class FieldCallbackFactory(CallbackData, prefix="user_field"):
    x: int
    y: int


def reset_field(user_id: int) -> None:
    users[user_id]['ships'] = copy.deepcopy(ships)
    users[user_id]['field'] = [
        [0 for _ in range(FIELD_SIZE)]
        for _ in range(FIELD_SIZE)
    ]


def get_field_keyboard(user_id: int) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []

    for i in range(FIELD_SIZE):
        array_buttons.append([])
        for j in range(FIELD_SIZE):
            array_buttons[i].append(InlineKeyboardButton(
                text=LEXICON[users[user_id]['field'][i][j]],
                callback_data=FieldCallbackFactory(x=i, y=j).pack()
            ))

    return InlineKeyboardMarkup(inline_keyboard=array_buttons)


@router.message(F.text == ButtonText.BATTLESHIP)
async def handle_battleship_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to play Battleship,\n"
             "click /start_naval any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("start_naval", prefix="!/"))
async def process_start_command(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {}
    reset_field(message.from_user.id)
    await message.answer(
        text=LEXICON['/start_naval'],
        reply_markup=get_field_keyboard(message.from_user.id)
    )


@router.callback_query(FieldCallbackFactory.filter())
async def process_category_press(callback: CallbackQuery,
                                 callback_data: FieldCallbackFactory):
    field = users[callback.from_user.id]['field']
    ships = users[callback.from_user.id]['ships']
    if field[callback_data.x][callback_data.y] == 0 and \
            ships[callback_data.x][callback_data.y] == 0:
        answer = LEXICON['miss']
        field[callback_data.x][callback_data.y] = 1
    elif field[callback_data.x][callback_data.y] == 0 and \
            ships[callback_data.x][callback_data.y] == 1:
        answer = LEXICON['hit']
        field[callback_data.x][callback_data.y] = 2
    else:
        answer = LEXICON['used']

    try:
        await callback.message.edit_text(
            text=LEXICON['next_move'],
            reply_markup=get_field_keyboard(callback.from_user.id)
        )
    except TelegramBadRequest:
        pass

    await callback.answer(answer)


# Five cats memory game ================================================================================================
cat_data = [
    {"name": "Рыжик", "sticker_id": "CAACAgIAAxkBAU4nKGYa5ZK0jTMFY5e2XYYrkGZDqCS1AAJVPQACxW34SnUXpLRodIq0NAQ"},
    {"name": "Сиамочка", "sticker_id": "CAACAgIAAxkBAU4nRmYa5lH4SBbRLWwBjKwR_84afmr-AAIsNgACNZvxSvKNYjzvkYigNAQ"},
    {"name": "Снежок", "sticker_id": "CAACAgIAAxkBAU4nQ2Ya5kI8KwXCzSAce4WvCnhOzi_8AAJUPAACRboJS3juH0a3Q8ocNAQ"},
    {"name": "Тортик", "sticker_id": "CAACAgIAAxkBAU4nPmYa5ey_nB6hS9dX71eZL7WmJ63iAAKXPQACuSLwSqDsP1hlPM6sNAQ"},
    {"name": "Фиалка", "sticker_id": "CAACAgIAAxkBAU4nSmYa5mRSn-CFZFkO_hyI_gdKqiN-AALjOAACwVwIS78AAfOpYkBUmjQE"}
]

bot_sequence = []

correct_sequence = [cat["name"] for cat in cat_data]

user_choices = {}


@router.message(F.text == ButtonText.FIVE_CATS)
async def handle_5_cats_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to play memory game,\n"
             "click /start_five_cats to meet my friends! ^w^",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("start_five_cats", prefix="!/"))
async def start_five_cats(message: types.Message):
    await message.answer("Hi! Welcome to Five Cats. Send /play_five_cats to start playing :3")


async def show_random_cats(chat_id, bot):
    global bot_sequence

    random.shuffle(cat_data)

    for cat in cat_data:
        await asyncio.sleep(2)
        await bot.send_sticker(chat_id, cat["sticker_id"])
        await bot.send_message(chat_id, cat["name"])

        bot_sequence.append(cat["name"])


@router.message(Command("play_five_cats", prefix="!/"))
async def play_five_cats(message: types.Message):
    global bot_sequence
    bot_sequence = []

    await message.answer("Get ready! The cats will appear shortly...")
    await asyncio.sleep(2)

    await show_random_cats(message.chat.id, message.bot)

    user_id = message.from_user.id
    user_choices[user_id] = []

    five_cats_buttons = [
        [InlineKeyboardButton(text='Рыжик', callback_data='1')],
        [InlineKeyboardButton(text='Сиамочка', callback_data='2')],
        [InlineKeyboardButton(text='Снежок', callback_data='3')],
        [InlineKeyboardButton(text='Тортик', callback_data='4')],
        [InlineKeyboardButton(text='Фиалка', callback_data='5')],
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=five_cats_buttons)

    await message.answer("Now choose the correct order!", reply_markup=inline_kb)


async def compare_choices(callback_query: types.CallbackQuery):
    global bot_sequence

    user_id = callback_query.from_user.id
    user_choices_list = user_choices[user_id]

    if user_choices_list == bot_sequence:
        await callback_query.message.answer("Good job, your memory is fine :3 Play again? /play_five_cats")
    else:
        await callback_query.message.answer(f"You have mistakes! The correct sequence is: {', '.join(bot_sequence)}")


@router.callback_query(lambda c: c.data.isdigit() and int(c.data) in range(1, 6))
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    choice_number = int(callback_query.data)
    user_choices[user_id].append(correct_sequence[choice_number - 1])

    current_cat_index = len(user_choices[user_id])

    if correct_sequence[choice_number - 1] == bot_sequence[current_cat_index - 1]:
        await callback_query.message.answer("Excellent choice! Meow :3")
    else:
        await callback_query.message.answer("Wrong choice! Try again.")

    if current_cat_index == 5:
        await compare_choices(callback_query)
    else:

        await callback_query.message.answer(f"Now choose Cat {current_cat_index + 1}")
