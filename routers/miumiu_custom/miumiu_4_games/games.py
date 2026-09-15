import asyncio
import copy
import random
from typing import Dict, List, Tuple

from aiogram import F, Router, types
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from keyboards.on_start import ButtonText, get_games_kb

router = Router(name=__name__)

CHOICES = ["Rock", "Paper", "Scissors"]
BLACKJACK_FACES = ["❤️", "♠️", "♦️", "♣️"]
BLACKJACK_VALUES = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
ZONES = ("hit_head", "hit_chest", "hit_legs")
ZONE_LABEL = {
    "hit_head": "head ^",
    "hit_chest": "chest >",
    "hit_legs": "legs v",
}

# Per-user game state (avoids multi-user races on globals)
blockme_games: Dict[int, Dict[str, int]] = {}
blackjack_games: Dict[int, Dict[str, List[Tuple[str, str]]]] = {}
five_cats_games: Dict[int, Dict[str, List[str]]] = {}
users: Dict[int, Dict[str, list]] = {}


def build_rps_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=choice, callback_data=f"rps_{choice.lower()}")]
            for choice in CHOICES
        ]
    )


def build_play_again_kb(callback: str, label: str = "Play again") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=callback)]]
    )


@router.message(F.text == ButtonText.RPS)
@router.message(Command("rps", prefix="!/"))
async def start_rps_game(message: types.Message):
    await message.answer("Choose your move:", reply_markup=build_rps_keyboard())


@router.callback_query(F.data == "rps_again")
async def rps_again(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Choose your move:", reply_markup=build_rps_keyboard())


@router.callback_query(F.data.startswith("rps_"))
async def process_rps_move(callback_query: types.CallbackQuery):
    user_choice = callback_query.data.split("_", 1)[1].capitalize()
    if user_choice not in CHOICES:
        await callback_query.answer("Invalid move")
        return

    bot_choice = random.choice(CHOICES)
    winner = determine_winner(user_choice, bot_choice)
    text = f"You: {user_choice}\nBot: {bot_choice}\n\n{winner}"

    await callback_query.answer(winner)
    await callback_query.message.answer(
        text,
        reply_markup=build_play_again_kb("rps_again"),
    )


def determine_winner(user_choice: str, bot_choice: str) -> str:
    if user_choice == bot_choice:
        return "It's a tie!"
    wins = {
        ("Rock", "Scissors"),
        ("Paper", "Rock"),
        ("Scissors", "Paper"),
    }
    if (user_choice, bot_choice) in wins:
        return "You win!"
    return "Bot wins!"


# DICE EMOJI ===========================================================================================================
async def _play_dice(message: Message, emoji: str, title: str) -> None:
    dice_msg = await message.answer_dice(emoji)
    await asyncio.sleep(3)
    value = dice_msg.dice.value if dice_msg.dice else "?"
    await message.answer(f"{title}: {value}")


@router.message(F.text == ButtonText.BOWLING)
@router.message(Command("bowling", prefix="!/"))
async def play_games_bowling(message: Message):
    await _play_dice(message, DiceEmoji.BOWLING, "Bowling score")


@router.message(F.text == ButtonText.DICE)
@router.message(Command("dice", prefix="!/"))
async def play_games_dice(message: Message):
    await _play_dice(message, DiceEmoji.DICE, "Dice roll")


@router.message(F.text == ButtonText.CASINO)
@router.message(Command("casino", prefix="!/"))
async def play_games_casino(message: Message):
    await _play_dice(message, DiceEmoji.SLOT_MACHINE, "Slot result")


@router.message(F.text == ButtonText.DART)
@router.message(Command("dart", prefix="!/"))
async def play_games_dart(message: Message):
    await _play_dice(message, DiceEmoji.DART, "Dart score")


@router.message(F.text == ButtonText.BASKETBALL)
@router.message(Command("basketball", prefix="!/"))
async def play_games_basketball(message: Message):
    await _play_dice(message, DiceEmoji.BASKETBALL, "Basketball score")


@router.message(F.text == ButtonText.FOOTBALL)
@router.message(Command("football", prefix="!/"))
async def play_games_football(message: Message):
    await _play_dice(message, DiceEmoji.FOOTBALL, "Football score")


# BLACKJACK ============================================================================================================
def deal_card() -> Tuple[str, str]:
    return random.choice(BLACKJACK_FACES), random.choice(BLACKJACK_VALUES)


def format_hand(hand: List[Tuple[str, str]]) -> str:
    return " ".join(f"{face}{value}" for face, value in hand)


def calculate_hand_score(hand: List[Tuple[str, str]]) -> int:
    score = 0
    ace_count = 0
    for _face, value in hand:
        if value.isdigit():
            score += int(value)
        elif value in ("J", "Q", "K"):
            score += 10
        elif value == "A":
            ace_count += 1
            score += 11
    while ace_count > 0 and score > 21:
        score -= 10
        ace_count -= 1
    return score


def blackjack_actions_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Hit", callback_data="bj_hit"),
                InlineKeyboardButton(text="Stand", callback_data="bj_stand"),
            ]
        ]
    )


async def _start_blackjack_round(target: types.Message, user_id: int) -> None:
    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
    blackjack_games[user_id] = {"player": player_hand, "dealer": dealer_hand}

    player_score = calculate_hand_score(player_hand)
    await target.answer(
        f"Your hand: {format_hand(player_hand)} (score {player_score})\n"
        f"Dealer shows: {format_hand([dealer_hand[0]])} ???\n\n"
        "Hit or Stand?",
        reply_markup=blackjack_actions_kb(),
    )


@router.message(F.text == ButtonText.BLACKJACK)
@router.message(Command("start_blackjack", prefix="!/"))
@router.message(Command("play21", prefix="!/"))
async def start_blackjack(message: types.Message):
    await message.answer("Blackjack — get as close to 21 as you can without going over.")
    await _start_blackjack_round(message, message.from_user.id)


@router.callback_query(F.data == "bj_again")
async def bj_again(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await _start_blackjack_round(callback_query.message, callback_query.from_user.id)


@router.callback_query(F.data == "bj_hit")
async def hit_blackjack(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    game = blackjack_games.get(user_id)
    if not game or not game.get("player"):
        await callback_query.answer("Start a new game first", show_alert=True)
        return

    card = deal_card()
    game["player"].append(card)
    player_score = calculate_hand_score(game["player"])
    await callback_query.answer(f"Drew {card[0]}{card[1]}")
    await callback_query.message.answer(
        f"You drew: {card[0]}{card[1]}\n"
        f"Hand: {format_hand(game['player'])} (score {player_score})"
    )

    if player_score > 21:
        await callback_query.message.answer(
            "You bust! Dealer wins.",
            reply_markup=build_play_again_kb("bj_again"),
        )
        blackjack_games.pop(user_id, None)
    else:
        await callback_query.message.answer("Hit or Stand?", reply_markup=blackjack_actions_kb())


@router.callback_query(F.data == "bj_stand")
async def stand_blackjack(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    game = blackjack_games.get(user_id)
    if not game or not game.get("player"):
        await callback_query.answer("Start a new game first", show_alert=True)
        return

    await callback_query.answer()
    dealer_hand = game["dealer"]
    while calculate_hand_score(dealer_hand) < 17:
        dealer_hand.append(deal_card())

    dealer_score = calculate_hand_score(dealer_hand)
    player_score = calculate_hand_score(game["player"])
    await callback_query.message.answer(
        f"Dealer: {format_hand(dealer_hand)} (score {dealer_score})"
    )

    if player_score > 21 or (player_score < dealer_score <= 21):
        result = "Dealer wins!"
    elif dealer_score > 21 or player_score > dealer_score:
        result = "You win!"
    else:
        result = "It's a tie!"

    await callback_query.message.answer(
        result,
        reply_markup=build_play_again_kb("bj_again"),
    )
    blackjack_games.pop(user_id, None)


@router.message(Command("hit", prefix="!/"))
async def hit_blackjack_cmd(message: types.Message):
    user_id = message.from_user.id
    game = blackjack_games.get(user_id)
    if not game or not game.get("player"):
        await message.answer("Start Blackjack from Games first.")
        return
    card = deal_card()
    game["player"].append(card)
    player_score = calculate_hand_score(game["player"])
    await message.answer(
        f"You drew: {card[0]}{card[1]}\n"
        f"Hand: {format_hand(game['player'])} (score {player_score})"
    )
    if player_score > 21:
        await message.answer(
            "You bust! Dealer wins.",
            reply_markup=build_play_again_kb("bj_again"),
        )
        blackjack_games.pop(user_id, None)
    else:
        await message.answer("Hit or Stand?", reply_markup=blackjack_actions_kb())


@router.message(Command("stand", prefix="!/"))
async def stand_blackjack_cmd(message: types.Message):
    user_id = message.from_user.id
    game = blackjack_games.get(user_id)
    if not game or not game.get("player"):
        await message.answer("Start Blackjack from Games first.")
        return
    dealer_hand = game["dealer"]
    while calculate_hand_score(dealer_hand) < 17:
        dealer_hand.append(deal_card())
    dealer_score = calculate_hand_score(dealer_hand)
    player_score = calculate_hand_score(game["player"])
    await message.answer(f"Dealer: {format_hand(dealer_hand)} (score {dealer_score})")
    if player_score > 21 or (player_score < dealer_score <= 21):
        result = "Dealer wins!"
    elif dealer_score > 21 or player_score > dealer_score:
        result = "You win!"
    else:
        result = "It's a tie!"
    await message.answer(result, reply_markup=build_play_again_kb("bj_again"))
    blackjack_games.pop(user_id, None)


# BLOCK ME =============================================================================================================
def blockme_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="^ head", callback_data="hit_head"),
                InlineKeyboardButton(text="> chest", callback_data="hit_chest"),
                InlineKeyboardButton(text="v legs", callback_data="hit_legs"),
            ]
        ]
    )


def _reset_blockme(user_id: int) -> None:
    blockme_games[user_id] = {"round": 1, "player_hp": 10, "bot_hp": 10}


@router.message(F.text == ButtonText.BLOCK_ME)
@router.message(Command("start_block_me", prefix="!/"))
async def start_blockme_game(message: types.Message):
    _reset_blockme(message.from_user.id)
    await message.answer(
        "Block Me — pick where you attack.\n"
        "Bot randomly blocks a zone. Hit = −2 HP to bot, blocked = bot counter (−1 to you).\n"
        "First to 0 HP loses.\n\n"
        "Round 1 — choose your attack:",
        reply_markup=blockme_kb(),
    )


@router.callback_query(F.data.in_(set(ZONES)))
async def process_blockme_attack(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    game = blockme_games.get(user_id)
    if not game:
        _reset_blockme(user_id)
        game = blockme_games[user_id]

    attack = callback_query.data
    block = random.choice(ZONES)

    if attack == block:
        game["player_hp"] -= 1
        round_result = (
            f"Blocked! Bot guarded {ZONE_LABEL[block]}.\n"
            f"Bot counters — you lose 1 HP."
        )
    else:
        game["bot_hp"] -= 2
        round_result = (
            f"Hit! You struck {ZONE_LABEL[attack]}, "
            f"bot blocked {ZONE_LABEL[block]}.\n"
            f"Bot loses 2 HP."
        )

    status = (
        f"{round_result}\n\n"
        f"Round {game['round']}\n"
        f"You: {game['player_hp']} HP | Bot: {game['bot_hp']} HP"
    )
    await callback_query.answer("Resolved")
    game["round"] += 1

    if game["player_hp"] <= 0:
        await callback_query.message.answer(
            status + "\n\nYou are defeated! GAME OVER",
            reply_markup=build_play_again_kb("blockme_again", "Fight again"),
        )
        blockme_games.pop(user_id, None)
    elif game["bot_hp"] <= 0:
        await callback_query.message.answer(
            status + "\n\nBot defeated! YOU WIN",
            reply_markup=build_play_again_kb("blockme_again", "Fight again"),
        )
        blockme_games.pop(user_id, None)
    else:
        await callback_query.message.answer(
            status + f"\n\nRound {game['round']} — choose your attack:",
            reply_markup=blockme_kb(),
        )


@router.callback_query(F.data == "blockme_again")
async def blockme_again(callback_query: types.CallbackQuery):
    await callback_query.answer()
    _reset_blockme(callback_query.from_user.id)
    await callback_query.message.answer(
        "Round 1 — choose your attack:",
        reply_markup=blockme_kb(),
    )


# SEA BATTLE ===========================================================================================================
FIELD_SIZE = 8

LEXICON = {
    "/start": "Вот твое поле. Можешь делать ход",
    0: "·",
    1: "🌊",
    2: "💥",
    "miss": "Мимо!",
    "hit": "Попал!",
    "used": "Вы уже стреляли сюда!",
    "next_move": "Делайте ваш следующий ход",
    "win": "Все корабли потоплены! Победа 🎉",
}

ships_template: list[list[int]] = [
    [1, 0, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0],
]


class FieldCallbackFactory(CallbackData, prefix="user_field"):
    x: int
    y: int


def reset_field(user_id: int) -> None:
    users[user_id]["ships"] = copy.deepcopy(ships_template)
    users[user_id]["field"] = [
        [0 for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)
    ]


def ships_remaining(user_id: int) -> int:
    ships = users[user_id]["ships"]
    field = users[user_id]["field"]
    left = 0
    for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
            if ships[i][j] == 1 and field[i][j] != 2:
                left += 1
    return left


def get_field_keyboard(user_id: int) -> InlineKeyboardMarkup:
    array_buttons: list[list[InlineKeyboardButton]] = []
    for i in range(FIELD_SIZE):
        array_buttons.append([])
        for j in range(FIELD_SIZE):
            array_buttons[i].append(
                InlineKeyboardButton(
                    text=LEXICON[users[user_id]["field"][i][j]],
                    callback_data=FieldCallbackFactory(x=i, y=j).pack(),
                )
            )
    return InlineKeyboardMarkup(inline_keyboard=array_buttons)


@router.message(F.text == ButtonText.BATTLESHIP)
@router.message(Command("start_naval", prefix="!/"))
async def process_start_command(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {}
    reset_field(message.from_user.id)
    await message.answer(
        text="Sea Battle — tap cells to shoot. · empty, 🌊 miss, 💥 hit.\n"
             "Sink every ship to win!",
        reply_markup=get_field_keyboard(message.from_user.id),
    )


@router.callback_query(FieldCallbackFactory.filter())
async def process_category_press(
    callback: CallbackQuery,
    callback_data: FieldCallbackFactory,
):
    if callback.from_user.id not in users:
        users[callback.from_user.id] = {}
        reset_field(callback.from_user.id)

    field = users[callback.from_user.id]["field"]
    ships = users[callback.from_user.id]["ships"]

    if field[callback_data.x][callback_data.y] == 0 and ships[callback_data.x][callback_data.y] == 0:
        answer = LEXICON["miss"]
        field[callback_data.x][callback_data.y] = 1
    elif field[callback_data.x][callback_data.y] == 0 and ships[callback_data.x][callback_data.y] == 1:
        answer = LEXICON["hit"]
        field[callback_data.x][callback_data.y] = 2
    else:
        answer = LEXICON["used"]

    remaining = ships_remaining(callback.from_user.id)
    if remaining == 0:
        text = LEXICON["win"]
        markup = build_play_again_kb("naval_again", "New battle")
    else:
        text = f"{LEXICON['next_move']} (ships left: {remaining})"
        markup = get_field_keyboard(callback.from_user.id)

    try:
        await callback.message.edit_text(text=text, reply_markup=markup)
    except TelegramBadRequest:
        pass

    await callback.answer(answer)


@router.callback_query(F.data == "naval_again")
async def naval_again(callback: CallbackQuery):
    await callback.answer()
    if callback.from_user.id not in users:
        users[callback.from_user.id] = {}
    reset_field(callback.from_user.id)
    await callback.message.answer(
        "New battle — tap cells to shoot!",
        reply_markup=get_field_keyboard(callback.from_user.id),
    )


# Five cats memory game ================================================================================================
cat_data = [
    {
        "name": "Рыжик",
        "sticker_id": "CAACAgIAAxkBAU4nKGYa5ZK0jTMFY5e2XYYrkGZDqCS1AAJVPQACxW34SnUXpLRodIq0NAQ",
    },
    {
        "name": "Сиамочка",
        "sticker_id": "CAACAgIAAxkBAU4nRmYa5lH4SBbRLWwBjKwR_84afmr-AAIsNgACNZvxSvKNYjzvkYigNAQ",
    },
    {
        "name": "Снежок",
        "sticker_id": "CAACAgIAAxkBAU4nQ2Ya5kI8KwXCzSAce4WvCnhOzi_8AAJUPAACRboJS3juH0a3Q8ocNAQ",
    },
    {
        "name": "Тортик",
        "sticker_id": "CAACAgIAAxkBAU4nPmYa5ey_nB6hS9dX71eZL7WmJ63iAAKXPQACuSLwSqDsP1hlPM6sNAQ",
    },
    {
        "name": "Фиалка",
        "sticker_id": "CAACAgIAAxkBAU4nSmYa5mRSn-CFZFkO_hyI_gdKqiN-AALjOAACwVwIS78AAfOpYkBUmjQE",
    },
]

CAT_BY_NAME = {cat["name"]: cat for cat in cat_data}


def five_cats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat["name"], callback_data=f"fc_{cat['name']}")]
            for cat in cat_data
        ]
    )


async def show_random_cats(message: types.Message, sequence: List[str]) -> None:
    order = list(cat_data)
    random.shuffle(order)
    for cat in order:
        await asyncio.sleep(1.5)
        await message.answer_sticker(cat["sticker_id"])
        await message.answer(cat["name"])
        sequence.append(cat["name"])


async def _run_five_cats(target: types.Message, user_id: int) -> None:
    five_cats_games[user_id] = {"sequence": [], "picks": [], "active": True}

    await target.answer("Five Cats — memorize the order of the cats!")
    await asyncio.sleep(1)
    await show_random_cats(target, five_cats_games[user_id]["sequence"])
    await target.answer(
        "Now tap the cats in the same order (1 of 5):",
        reply_markup=five_cats_kb(),
    )


@router.message(F.text == ButtonText.FIVE_CATS)
@router.message(Command("start_five_cats", prefix="!/"))
@router.message(Command("play_five_cats", prefix="!/"))
async def play_five_cats(message: types.Message):
    await _run_five_cats(message, message.from_user.id)


@router.callback_query(F.data == "fc_again")
async def five_cats_again(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await _run_five_cats(callback_query.message, callback_query.from_user.id)


@router.callback_query(F.data.startswith("fc_"))
async def process_five_cats_pick(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    game = five_cats_games.get(user_id)
    if not game or not game.get("active"):
        await callback_query.answer("Start Five Cats from the Games menu", show_alert=True)
        return

    name = callback_query.data[3:]
    if name not in CAT_BY_NAME:
        await callback_query.answer("Unknown cat")
        return

    expected = game["sequence"][len(game["picks"])]
    game["picks"].append(name)
    step = len(game["picks"])

    if name != expected:
        game["active"] = False
        await callback_query.answer("Wrong!")
        await callback_query.message.answer(
            f"Wrong! Expected {expected}.\n"
            f"Correct order: {', '.join(game['sequence'])}",
            reply_markup=build_play_again_kb("fc_again", "Try again"),
        )
        return

    await callback_query.answer("Correct!")
    if step == len(game["sequence"]):
        game["active"] = False
        await callback_query.message.answer(
            "Perfect memory! All five cats in order :3",
            reply_markup=build_play_again_kb("fc_again", "Play again"),
        )
    else:
        await callback_query.message.answer(
            f"Good! Now pick cat {step + 1} of {len(game['sequence'])}:",
            reply_markup=five_cats_kb(),
        )


@router.message(F.text == ButtonText.BACK_TO_GAMES)
async def back_to_games(message: types.Message):
    await message.answer("Games menu:", reply_markup=get_games_kb())
