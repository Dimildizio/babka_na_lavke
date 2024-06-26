import aiogram.exceptions
import aiohttp
import json
import random

from aiogram import types
from PIL import Image, ImageFont, ImageDraw

from bot import img_downloader, checks
from bot.constants import MIN_AGE, MAX_AGE, MIN_FONT, FASTAPI_BASE_URL, TXT
from utils import savefile


async def get_faces(message, response_data, lang):
    response_data = json.loads(response_data)
    if response_data.get("message", None):
        await message.answer(TXT[lang]['no_face'])
        return
    return response_data.get("faces", [])


async def send_image(message, file_path, lang):
    try:
        result = types.FSInputFile(file_path)
        await message.answer_photo(photo=result)
    except aiogram.exceptions.TelegramBadRequest:
        await message.answer(TXT[lang]["try_again"])


async def draw_image(faces_data, file_path, lang):
    image = Image.open(file_path)
    draw = ImageDraw.Draw(image)
    await process_faces(faces_data, draw, image.size, lang)
    return await savefile(image, file_path)


async def process_faces(faces_data, draw, image_size, lang):
    for face in faces_data:
        age = int(face["age"])
        gender = face["gender"]
        bbox = face["bbox"]

        cls = await misgender(gender, age, lang)
        text = f"{age}-{TXT[lang]['text_year']}{TXT[lang]['text_g1'] if gender else TXT[lang]['text_g2']} {cls}"

        await draw_text(draw, bbox, text, image_size)


async def misgender(gender, age, lang):
    if random.randint(0, 100) < 5:
        return TXT[lang]['gender_5']
    elif age < MIN_AGE:
        return TXT[lang]['gender_4']
    elif age > MAX_AGE:
        return TXT[lang]['gender_3']
    elif not gender:
        return TXT[lang]['gender_2']
    else:
        return TXT[lang]['gender_1']


async def draw_text(draw, bbox, text, image_size):
    font = await get_font(bbox, text, image_size)
    draw.rectangle(bbox, outline="green", width=5)
    text_position = await get_text_position(font, bbox, text, image_size)
    draw.text(text_position, text, fill="red", font=font)


async def get_text_position(font, bbox, text, image_size):
    text_width, text_height = await gettext_size(font, text)

    bbox_center_x = bbox[0] + (bbox[2] - bbox[0]) / 2
    text_position_x = min(max(0, bbox_center_x - text_width / 2), image_size[0] - text_width)
    text_position_y = max(text_height, bbox[1] - text_height - 10)

    return text_position_x, text_position_y


async def gettext_size(font, text):
    x1, y1, x2, y2 = font.getbbox(text)
    text_width, text_height = (x2 - x1, y2 - y1)
    return text_width, text_height


async def get_font(bbox, text, image_size):
    font_size = max((bbox[2] - bbox[0]) // 10, MIN_FONT)
    fontname = "arial.ttf"
    font = ImageFont.truetype(fontname, font_size)
    text_width, text_height = await gettext_size(font, text)

    while text_width > image_size[0] and font_size > 1:
        font_size -= 3
        font = ImageFont.truetype(fontname, font_size)
        text_width, text_height = await gettext_size(font, text)
    return font


async def process_and_send_faces(message, file_path, response_data, lang):
    faces_data = await(get_faces(message, response_data, lang))
    if not faces_data:
        return
    new_filename = await draw_image(faces_data, file_path, lang)
    if new_filename:
        await send_image(message, new_filename, lang)
    else:
        await message.answer(TXT[lang]['try_again'])


async def send_image_path_to_analyze_faces(file_path):
    async with aiohttp.ClientSession() as session:
        data = {"file_path": file_path}
        try:
            async with session.post(f"{FASTAPI_BASE_URL}/analyze_faces", data=data) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    return None
        except Exception as e:
            print(f"Failed to send image path to FastAPI: {e}")
            return None


async def process_image(message: types.Message, photo: bool = True, lang: str = 'ru'):
    if not (await checks.block_message(message)):
        return
    input_path = await img_downloader.handle_download(message, photo)
    if input_path:
        response = await send_image_path_to_analyze_faces(input_path)
        if response:
            await process_and_send_faces(message, input_path, response, lang)
        else:
            await message.answer(TXT[lang]['bad_response'])
