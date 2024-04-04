import aiocron
import aiohttp
import asyncio
import io
import json
import os
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw

from constants import TOKEN, GENDER_1, GENDER_2, GENDER_3, MIN_AGE, MIN_FONT, MAX_IMGS, FASTAPI_BASE_URL, IMAGE_DIR, \
                       DELAY_BETWEEN_IMAGES, SENT_TIME
from database.users_db import update_image_count, can_send_image, reset_image_counts


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def get_faces(message, response_data):
    response_data = json.loads(response_data)
    if response_data.get("message", None):
        await message.answer("Это хто тут такой ходить?! Не признать!!")
        return
    return response_data.get("faces", [])


async def process_and_send_faces(message, file_path, response_data):
    faces_data = await(get_faces(message, response_data))
    if not faces_data:
        return

    await draw_image(faces_data, file_path)
    await send_image(message, file_path)


async def send_image(message, file_path):
    result = types.FSInputFile(file_path)
    await message.answer_photo(photo=result)


async def draw_image(faces_data, file_path):
    image = Image.open(file_path)
    draw = ImageDraw.Draw(image)
    await process_faces(faces_data, draw)
    image.save(file_path, format='PNG')


async def process_faces(faces_data, draw):
    for face in faces_data:
        age = int(face["age"])
        gender = face["gender"]
        bbox = face["bbox"]

        cls = GENDER_1 if gender else GENDER_2
        text = f"{age}-летн{'ий' if gender else 'яя'} {cls if age < MIN_AGE else GENDER_3}"

        await draw_text(draw, bbox, text)


async def draw_text(draw, bbox, text):
    font = await get_font(bbox)
    draw.rectangle(bbox, outline="green", width=3)
    text_position = await get_text_position(font, bbox, text)
    draw.text(text_position, text, fill="red", font=font)


async def get_text_position(font, bbox, text):
    x1, y1, x2, y2 = font.getbbox(text)
    text_width, text_height = (x2 - x1, y2 - y1)
    text_position = (bbox[0] - text_width // 4, bbox[1] - 2 * text_height)
    return text_position


async def get_font(bbox):
    font_size = max((bbox[2] - bbox[0]) // 10, MIN_FONT)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    return font


async def prevent_multi_sending(message):
    last_sent = SENT_TIME.get(message.from_user.id, None)
    dt = datetime.now()
    if message.media_group_id is None and (last_sent is None or (
            dt - last_sent).total_seconds() >= DELAY_BETWEEN_IMAGES):
        SENT_TIME[message.from_user.id] = dt
        return True
    return False


async def block_message(message):
    if not await prevent_multi_sending(message):
        await message.answer("Ишь какой шустрый! Обожди немного!")
        return
    if not can_send_image(message.from_user.id, MAX_IMGS):
        await message.answer("Ходють тут ходють! Устала я, приходь завтра!")
        return
    return True


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Хто тут ходить?! Покажи свое лицо!")


@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.answer("Ась? Глухая я стала. Не слышу ничаво. Покажи свое лицо")


async def get_file_data(message, photo=True):
    file_id = message.photo[-1].file_id if photo else message.document.file_id
    file_info = await message.bot.get_file(file_id)

    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    input_path = os.path.join(IMAGE_DIR, f"{file_info.file_unique_id}.png")
    update_image_count(message, input_path)
    return file_url, input_path


async def download_image(message, response, input_path):
    if response.status == 200:
        content = await response.read()
        orig = Image.open(io.BytesIO(content))
        orig.save(input_path, format='PNG')
        return input_path
    else:
        await message.answer("Шото ты не то шлешь такое! Не тыкай мне тут!")
        print('Failed', response.status)


async def handle_download(message, photo=True):
    file_url, input_path = await get_file_data(message, photo)
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            downloaded = await download_image(message, response, input_path)
    return downloaded


@dp.message(F.document)
async def handle_doc(message: types.Message):
    for ext in [".png", ".jpg", ".jpeg"]:
        if ext in message.document.file_name:
            await process_image(message, photo=False)
            return


@dp.message(F.content_type == "photo")
async def handle_image(message: types.Message):
    await process_image(message)


async def process_image(message: types.Message, photo: bool = True):
    if not (await block_message(message)):
        return
    input_path = await handle_download(message, photo)
    if input_path:
        response = await send_image_path_to_analyze_faces(input_path)
        if response:
            await process_and_send_faces(message, input_path, response)
        else:
            await message.answer("Шота рожей ты не вышел! Кыш отседова!")


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


@aiocron.crontab('0 0 * * *')
async def scheduled_reset():
    reset_image_counts()
    print("Image counts have been reset.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shut down")
        sys.exit(0)
