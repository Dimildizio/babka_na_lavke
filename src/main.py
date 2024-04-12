import aiocron
import asyncio
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command

from bot import constants, face_processing
from bot.constants import TXT
from database.users_db import reset_image_counts, count_unique_users


bot = Bot(token=constants.TOKEN)
dp = Dispatcher()


@dp.message(Command("utils"))
async def handle_utils(message: types.Message):
    reset_image_counts(message.from_user.id)
    await message.answer(f'num: {count_unique_users()}')



@dp.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer(TXT['welcome'])


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    await message.answer(TXT['help'])


@dp.message(Command("contacts"))
async def handle_help(message: types.Message):
    user = message.from_user
    print(f"{user.id}{user.username} {user.first_name} {user.last_name} requested contacts")
    text = TXT['contact_me'].format(tg=constants.TG, public=constants.TGPUBLIC,
                                   adjuface=constants.ADJUFACE, github=constants.GITHUB)
    await message.answer(text)


@dp.message(F.text)
async def handle_text(message: types.Message):
    await message.answer(TXT['please_no_text'])


@dp.message(F.document)
async def handle_doc(message: types.Message):
    for ext in [".png", ".jpg", ".jpeg"]:
        if ext in message.document.file_name:
            await face_processing.process_image(message, photo=False)
            return
    await message.answer(TXT['wrong_doc'])


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
