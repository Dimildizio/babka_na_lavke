import aiocron
import asyncio
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command

from bot import constants, face_processing
from bot.constants import TXT
from database.users_db import reset_image_counts, count_unique_users, create_user, update_lang_db, get_lang
from utils import get_user_info

bot = Bot(token=constants.TOKEN)
dp = Dispatcher()


@dp.message(Command("utils"))
async def handle_utils(message: types.Message):
    reset_image_counts(message.from_user.id)
    await message.answer(f'num: {count_unique_users()}')


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    create_user(message)
    lang = get_lang(message)
    await message.answer(TXT[lang]['welcome'])
    await message.answer(TXT[lang]['help'])


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    lang = get_lang(message)
    await message.answer(TXT[lang]['help'])


@dp.message(Command("lang"))
async def handle_lang(message: types.Message):
    lang = 'en' if get_lang(message) == 'ru' else 'ru'
    update_lang_db(message.from_user.id, lang)
    await message.answer(TXT[lang]['lang'])


@dp.message(Command("contacts"))
async def handle_help(message: types.Message):
    info = await get_user_info(message)
    lang = get_lang(message)
    print(f"{info} requested contacts")
    text = TXT[lang]['contact_me'].format(tg=constants.TG, public=constants.TGPUBLIC,
                                          adjuface=constants.ADJUFACE, github=constants.GITHUB)
    await message.answer(text)


@dp.message(F.text)
async def handle_text(message: types.Message):
    info = await get_user_info(message)
    lang = get_lang(message)
    print(f"{info}: {message.text}")
    if 'лапушка' in message.text.lower():
        return await message.answer("Лапушка - значит у бабули есть любимчики. Я тебя запомнила")
    await message.answer(TXT[lang]['please_no_text'])


@dp.message(F.document)
async def handle_doc(message: types.Message):

    lang = get_lang(message)
    for ext in [".png", ".jpg", ".jpeg"]:
        if ext in message.document.file_name:
            await face_processing.process_image(message, photo=False, lang=lang)
            return
    await message.answer(TXT[lang]['wrong_doc'])


@dp.message(F.content_type == "photo")
async def handle_image(message: types.Message):
    lang = get_lang(message)
    await face_processing.process_image(message, lang=lang)


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
