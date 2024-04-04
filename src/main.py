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

    image = Image.open(file_path)
    draw = ImageDraw.Draw(image)


    for face in faces_data:
        age = int(face["age"])
        gender = face["gender"]
        bbox = face["bbox"]

        draw.rectangle(bbox, outline="green", width=3)

        cls = GENDER_1 if gender else GENDER_2
        text = f"{age}-летн{'ий' if gender else 'яя'} {cls if age < MIN_AGE else GENDER_3}"
        font_size = max((bbox[2] - bbox[0])//10, MIN_FONT)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        x1, y1, x2, y2 = font.getbbox(text)
        text_width, text_height = (x2-x1, y2-y1)
        text_position = (bbox[0]-text_width//4, bbox[1] - 2*text_height)
        draw.text(text_position, text, fill="red", font=font)

    image.save(file_path, format='PNG')
    result = types.FSInputFile(file_path)
    if faces_data:
        await message.answer_photo(photo=result)


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



@dp.message((F.text))
async def handle_text(message: types.Message):
    await message.answer("Ась? Глухая я стала. Не слышу ничаво. Покажи свое лицо")


@dp.message(F.content_type == "photo")
async def handle_image(message: types.Message):
    if not (await block_message(message)):
        return

    file_id = message.photo[-1].file_id
    file_info = await message.bot.get_file(file_id)

    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    input_path = os.path.join(IMAGE_DIR, f"{file_info.file_unique_id}.png")
    update_image_count(message, input_path)

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                content = await response.read()
                orig = Image.open(io.BytesIO(content))
                orig.save(input_path, format='PNG')
            else:
                print('Failed', response.status)
    response = await send_image_path_to_analyze_faces(input_path)

    if response:
        await process_and_send_faces(message, input_path, response)
    else:
        await message.answer("Failed to analyze the image.")


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
