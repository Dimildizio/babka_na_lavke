from datetime import datetime

from bot.constants import SENT_TIME, DELAY_BETWEEN_IMAGES, MAX_IMGS
from database.users_db import can_send_image


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
