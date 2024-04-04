import aiocron
import asyncio
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command

from bot import constants, face_processing
from database.users_db import reset_image_counts


bot = Bot(token=constants.TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer("Хто тут ходить?! Покажи свое лицо!")


@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.answer("Ась? Глухая я стала. Не слышу ничаво. Покажи свое лицо")


@dp.message(F.document)
async def handle_doc(message: types.Message):
    for ext in [".png", ".jpg", ".jpeg"]:
        if ext in message.document.file_name:
            await face_processing.process_image(message, photo=False)
            return
    await message.answer("Шото ты не то шлешь такое! Не тыкай мне тут!")


@dp.message(F.content_type == "photo")
async def handle_image(message: types.Message):
    await face_processing.process_image(message)


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
