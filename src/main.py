from aiogram import Bot, Dispatcher, types, F
import aiohttp
import asyncio
import io
import json
import os
import sys

from datetime import datetime
from PIL import Image, ImageFont, ImageDraw

from constants import TOKEN, GENDER_1, GENDER_2, GENDER_3, MIN_AGE, MIN_FONT, MAX_IMGS, FASTAPI_BASE_URL, IMAGE_DIR, \
                       DELAY_BETWEEN_IMAGES, SENT_TIME
from database.users_db import update_image_count, can_send_image


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def process_and_send_faces(message, file_path, response_data):
    image = Image.open(file_path)
    draw = ImageDraw.Draw(image)

    response_data = json.loads(response_data)
    faces_data = response_data.get("faces", [])

    for face in faces_data:
        age = face["age"]
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

        text_width, text_height = draw.textsize(text, font=font)
        text_position = (bbox[0], bbox[1] - text_height)
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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shut down")
        sys.exit(0)
