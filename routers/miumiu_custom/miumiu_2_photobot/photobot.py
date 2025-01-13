import base64
import json
import os
import random
import tempfile
import time
from io import BytesIO

import aiohttp
import requests
from aiogram import (
    Bot,
    types,
    Dispatcher,
    F,
)
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    FSInputFile,
    BufferedInputFile,
    ReplyKeyboardRemove,
)
from aiogram.types import InputFile
from aiogram.types import Message
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from dotenv import load_dotenv
from moviepy.video.io.VideoFileClip import VideoFileClip

from keyboards.inline_keyboards.actions_kb import build_actions_kb
from keyboards.on_start import ButtonText

bot_token = os.getenv('BOT_TOKEN')
fusion_brain_token = os.getenv('FUSION_BRAIN_TOKEN')
fusion_brain_key = os.getenv('FB_KEY')

load_dotenv()

bot = Bot(token=bot_token)
dp = Dispatcher()

router = Router(name=__name__)


class InputFileBytes(InputFile):
    def __init__(self, file_data: bytes, filename: str):
        """
        Represents the contents of a file to be uploaded from bytes data.

        :param file_data: Bytes data of the file
        :param filename: Name of the file
        """
        super().__init__(filename=filename)
        self.file_data = file_data

    async def read(self, bot):
        """
        Implementation of the read method to yield bytes data of the file.
        """
        yield self.file_data


class AIfilters(StatesGroup):
    Maskings = State()
    Filterings = State()
    Framings = State()
    Rembg = State()


# MEME BOX =============================================================================================================

MEME_COUNT = 37


@router.message(F.text == ButtonText.MEMES)
async def handle_memes_message(message: types.Message):
    await message.answer(
        text="Meow! If you want get some memes,\n"
             "click /memes any time! I have 37 of them! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("memes", prefix="!/"))
async def give_random_meme(message: types.Message):
    folder_path = os.path.join(os.getcwd(), "routers", "miumiu_custom", "miumiu_2_photobot", "meme_box")
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    if not files:
        await message.reply("No memes found :(")
        return

    random_meme = random.choice(files)
    file_path = os.path.join(folder_path, random_meme)

    photo = FSInputFile(file_path)
    await message.reply_photo(photo, caption="Here you are ^w^")


@router.message(Command("actions", prefix="!/"))
async def send_actions_message_w_kb(message: types.Message):
    await message.answer(
        text="Your actions:",
        reply_markup=build_actions_kb(),
    )


# STICKER BOT ==========================================================================================================
class StickerButtonText:
    COOL_SERVAL = "Cool serval"
    NIKA = "Eustoma"
    ROCKET_KITTY = "Rocket-cat"
    RED_FOXIE = "Red fox"
    KITTY = "Cutie kitten"
    FOX = "Chonky Fox"
    GENSHIN = "Genshin Impact"
    TIK_TOK = "Tiktok animals"
    HSR = "HSR"
    MANGA = "Manga"


async def send_sticker(chat_id, sticker_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendSticker'
    params = {'chat_id': chat_id, 'sticker': sticker_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            return await response.json()


@router.message(F.text == ButtonText.STICKERS)
async def handle_stickers_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to get some cool stickers,\n"
             "click /sticker_kb any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("sticker_kb", prefix="!/"))
async def send_keyboard_command(message: types.Message):
    markup = get_sticker_kb()
    await message.answer("Choose a sticker:", reply_markup=markup)


def get_sticker_kb() -> ReplyKeyboardMarkup:
    buttons_row_1 = [
        KeyboardButton(
            text=StickerButtonText.COOL_SERVAL
        ),
        KeyboardButton(
            text=StickerButtonText.NIKA
        ),
        KeyboardButton(
            text=StickerButtonText.ROCKET_KITTY
        ),
    ]
    buttons_row_2 = [
        KeyboardButton(
            text=StickerButtonText.RED_FOXIE
        ),
        KeyboardButton(
            text=StickerButtonText.KITTY
        ),
        KeyboardButton(
            text=StickerButtonText.FOX
        ),
    ]
    buttons_row_3 = [
        KeyboardButton(
            text=StickerButtonText.GENSHIN
        ),
        KeyboardButton(
            text=StickerButtonText.TIK_TOK
        ),
        KeyboardButton(
            text=StickerButtonText.HSR
        ),
    ]
    buttons_row_4 = [
        KeyboardButton(
            text=StickerButtonText.MANGA
        ),
    ]

    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            buttons_row_1,
            buttons_row_2,
            buttons_row_3,
            buttons_row_4
        ],
        resize_keyboard=True,
    )
    return markup_keyboard


async def process_button(callback_query: types.CallbackQuery, sticker_id: str):
    await callback_query.answer()
    await bot.send_sticker(callback_query.message.chat.id, sticker_id)


# 1
@router.callback_query(lambda query: query.data == 'cool_serval')
async def process_cool_serv(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSIGY063zYcJsNIAwHRE9NnjiLjzWmAAJKSQAC4AfxSkws0ZUa6nFtNAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.COOL_SERVAL)
async def cool_serv_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSIGY063zYcJsNIAwHRE9NnjiLjzWmAAJKSQAC4AfxSkws0ZUa6nFtNAQ'
    await send_sticker(message.chat.id, sticker_id)


# 2
@router.callback_query(lambda query: query.data == 'eustoma')
async def process_eustoma(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSAmY06vl7dAsZCAKHmSqN5FH9d5PYAAISUAAClT8RSGf6RXnVmT2nNAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.NIKA)
async def eustoma_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSAmY06vl7dAsZCAKHmSqN5FH9d5PYAAISUAAClT8RSGf6RXnVmT2nNAQ'
    await send_sticker(message.chat.id, sticker_id)


# 3
@router.callback_query(lambda query: query.data == 'rocket_kitty')
async def process_rocket_kitty(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSDmY06yAl2_skuYkJi9Vz8fRrlLb6AAKoSAACWHM5SUoG_rkCAUQAATQE'
    )


@router.message(lambda message: message.text == StickerButtonText.ROCKET_KITTY)
async def rocket_kitty_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSDmY06yAl2_skuYkJi9Vz8fRrlLb6AAKoSAACWHM5SUoG_rkCAUQAATQE'
    await send_sticker(message.chat.id, sticker_id)


# 4
@router.callback_query(lambda query: query.data == 'red_foxie')
async def process_red_fox(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSC2Y06xS5BOYGOg3FdBu39cHMjjatAAL_GwAC11hpSDnOE4z7Np33NAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.RED_FOXIE)
async def red_fox_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSC2Y06xS5BOYGOg3FdBu39cHMjjatAAL_GwAC11hpSDnOE4z7Np33NAQ'
    await send_sticker(message.chat.id, sticker_id)


# 5
@router.callback_query(lambda query: query.data == 'kitty')
async def process_cutie_kitty(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSBWY06wdjNO71aHgvFkTUgaAzgw7_AAJjKQACkpAZS_BALMjD9j1gNAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.KITTY)
async def cutie_kitty_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSBWY06wdjNO71aHgvFkTUgaAzgw7_AAJjKQACkpAZS_BALMjD9j1gNAQ'
    await send_sticker(message.chat.id, sticker_id)


# 6
@router.callback_query(lambda query: query.data == 'chonky_fox')
async def process_chonky_fox(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSE2Y06z9rV1zG9p8NU3cwXVKJvM6qAAIHAwACz7vUDpXjgMoqn_mKNAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.FOX)
async def chonky_fox_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSE2Y06z9rV1zG9p8NU3cwXVKJvM6qAAIHAwACz7vUDpXjgMoqn_mKNAQ'
    await send_sticker(message.chat.id, sticker_id)


# 7
@router.callback_query(lambda query: query.data == 'genshin')
async def process_genshin(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgUAAxkBAVPSHmY0620IpHcCQrD8ZkLl6Q0mKD5UAALxDAACjIaBVVP5YlW7vh92NAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.GENSHIN)
async def genshin_handler(message: types.Message):
    sticker_id = 'CAACAgUAAxkBAVPSHmY0620IpHcCQrD8ZkLl6Q0mKD5UAALxDAACjIaBVVP5YlW7vh92NAQ'
    await send_sticker(message.chat.id, sticker_id)


# 8
@router.callback_query(lambda query: query.data == 'tik_tok')
async def process_tik_tok_animals(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSGmY061-ICZ4RrxvlgLeHi6KkUWd5AAIqRwACYdpoSKsAAQ2QWBSuaDQE'
    )


@router.message(lambda message: message.text == StickerButtonText.TIK_TOK)
async def tik_tok_animals_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSGmY061-ICZ4RrxvlgLeHi6KkUWd5AAIqRwACYdpoSKsAAQ2QWBSuaDQE'
    await send_sticker(message.chat.id, sticker_id)


# 9
@router.callback_query(lambda query: query.data == 'hsr')
async def process_hsr(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgIAAxkBAVPSFmY061WAA6rHHWhdvUxCv7u7ig9PAAK_MAAC6dvJSH8MV1OceRHLNAQ'
    )


@router.message(lambda message: message.text == StickerButtonText.HSR)
async def hsr_handler(message: types.Message):
    sticker_id = 'CAACAgIAAxkBAVPSFmY061WAA6rHHWhdvUxCv7u7ig9PAAK_MAAC6dvJSH8MV1OceRHLNAQ'
    await send_sticker(message.chat.id, sticker_id)


# 10
@router.callback_query(lambda query: query.data == 'manga')
async def process_manga(callback_query: types.CallbackQuery):
    await process_button(
        callback_query, 'CAACAgEAAxkBAVPR_mY06uLrPTII3Y8iZyRbGU7VAAH9WAACqwoAApl_iAIiidAVEPqjMTQE'
    )


@router.message(lambda message: message.text == StickerButtonText.MANGA)
async def manga_handler(message: types.Message):
    sticker_id = 'CAACAgEAAxkBAVPR_mY06uLrPTII3Y8iZyRbGU7VAAH9WAACqwoAApl_iAIiidAVEPqjMTQE'
    await send_sticker(message.chat.id, sticker_id)


# PowerPoint Presentation ==============================================================================================
@router.message(F.text == ButtonText.PYTHON_PRESENTATION)
async def handle_python_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to study Python 3,\n"
             "click /presentation to get your presentation .pptx! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("presentation", prefix="!/"))
async def send_presentation(message: types.Message):
    presentations_dir = os.path.join(os.path.dirname(__file__), "presentations")

    if not os.path.exists(presentations_dir):
        await message.answer("Sorry, the presentations are not available at the moment.")
        return

    presentations = [f for f in os.listdir(presentations_dir) if f.endswith('.pptx')]

    if not presentations:
        await message.answer("Sorry, there are no presentations available at the moment.")
        return

    presentation_path = os.path.join(presentations_dir, presentations[0])

    await message.answer_document(types.FSInputFile(presentation_path, presentations[0]))


# VIDEO TO MP3 CONVERTER ===============================================================================================
class VideoMaster(StatesGroup):
    WaitingForVideo = State()


@router.message(F.video)
async def handle_video(message: Message, state: FSMContext):
    await state.set_state(VideoMaster.WaitingForVideo)
    if message.video.duration <= 30:
        video_file = await message.bot.get_file(message.video.file_id)

        input_video_stream = BytesIO()
        await message.bot.download_file(video_file.file_path, destination=input_video_stream)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
            temp_video_file.write(input_video_stream.getvalue())
            temp_video_file_path = temp_video_file.name

        video = VideoFileClip(temp_video_file_path)
        temp_audio_file_path = temp_video_file_path.replace(".mp4", ".mp3")
        video.audio.write_audiofile(temp_audio_file_path)
        video.close()

        with open(temp_audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio = BufferedInputFile(audio_bytes, filename="audio.mp3")
            await message.reply_document(audio)
            # await message.reply_voice(audio)  # for voice messages

        os.unlink(temp_video_file_path)
        os.unlink(temp_audio_file_path)

        await state.clear()
    else:
        await message.answer("Sorry, the video duration exceeds the limit of 30 seconds.")


@router.message(F.text == ButtonText.VIDEO_TO_MP3)
async def handle_vid_to_mp3_message(message: types.Message):
    await message.answer(
        text="Meow! If you want to get the mp3 file from your video,\n"
             "click /video_to_mp3 any time! 30 seconds max! ;3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("video_to_mp3", prefix="!/"))
async def start_video(message: Message, state: FSMContext):
    await state.set_state(VideoMaster.WaitingForVideo)
    await message.answer("Send me a video (30 seconds max).")


# KANDINSKIY ===========================================================================================================
class KandinskyStates(StatesGroup):
    Intro = State()
    TextToImage = State()


class ButtonTextKandinsky:
    TEXT_TO_IMAGE = "Text to image"


API_URL = "https://api-key.fusionbrain.ai/"

MODELS_ENDPOINT = API_URL + "key/api/v1/models"
GENERATE_ENDPOINT = API_URL + "key/api/v1/text2image/run"
STATUS_ENDPOINT = API_URL + "key/api/v1/text2image/status/"

headers = {
    'X-Key': f'Key {fusion_brain_token}',
    'X-Secret': f'Secret {fusion_brain_key}',
}


def get_text_to_image_kb() -> ReplyKeyboardMarkup:
    text_to_image_button = KeyboardButton(text="Text to image")
    buttons_row_1 = [text_to_image_button]
    markup_keyboard = ReplyKeyboardMarkup(
        keyboard=[buttons_row_1],
        resize_keyboard=True
    )
    return markup_keyboard


class Text2ImageAPI:
    def __init__(self, url, fusion_brain_token, fusion_brain_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {fusion_brain_token}',
            'X-Secret': f'Secret {fusion_brain_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)


@router.message(F.text == ButtonText.KANDINSKY)
async def handle_kandinskiy_message(message: types.Message):
    await message.answer(
        text="Meow! If you want draw with me,\n"
             "click /start_kandinsky any time! :3",
        reply_markup=ReplyKeyboardRemove(),
        one_time_keyboard=True
    )


@router.message(Command("start_kandinsky", prefix="!/"))
async def start(message: types.Message):
    await message.answer(
        "Welcome to the Kandinsky bot! Please, press on the button 'Text to Image' ^w^\n"
        "And please, don't ask me to draw violent or forbidden things!\n"
        "I have paws 😿",
        reply_markup=get_text_to_image_kb()
    )


@router.message(F.text == ButtonTextKandinsky.TEXT_TO_IMAGE)
async def handle_text_to_image(message: Message, state: FSMContext):
    await state.set_state(KandinskyStates.Intro)
    await message.answer("Please enter the text you want to generate an image for.\n"
                         "It may take some time, almost 30 seconds, so be patient UwU")
    await state.set_state(KandinskyStates.TextToImage)


@router.message(KandinskyStates.TextToImage)
async def process_text_for_image(message: types.Message, state: FSMContext):
    await state.set_state(KandinskyStates.TextToImage)
    text = message.text
    api = Text2ImageAPI(
        "https://api-key.fusionbrain.ai/",
        f"{fusion_brain_token}",
        f"{fusion_brain_key}"
    )
    model_id = api.get_model()
    if model_id:
        print(f"Model ID: {model_id}")
        uuid = api.generate(text, model_id)
        print(f"Image UUID: {uuid}")
        images = api.check_generation(uuid)

        if images:
            print(f"Images: {images}")

            image_base64 = images[0]
            image_data = base64.b64decode(image_base64)

            buffered_input_file = types.input_file.BufferedInputFile(file=image_data, filename="image.jpg")

            await message.answer_photo(buffered_input_file)

        else:
            await message.answer("Error generating image. Please try again later.")
    else:
        await message.answer("Error fetching model ID. Please try again later.")

    await state.clear()
