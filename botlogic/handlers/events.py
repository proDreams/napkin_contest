import logging
from asyncio import sleep

from aiogram import types
from aiogram.types import ChatMemberUpdated

from botlogic.settings import bot, secrets
from botlogic.utils.check_captcha import send_captcha
from botlogic.utils.commands import set_commands
from botlogic import views

logger = logging.getLogger(__name__)


async def start_bot() -> None:
    await set_commands(bot=bot)
    await bot.send_message(chat_id=secrets.admin_id, text=views.start_bot_msg())


async def stop_bot() -> None:
    await bot.send_message(chat_id=secrets.admin_id, text=views.stop_bot_msg())


async def on_user_join(event: types.ChatMemberUpdated, bot):
    await send_captcha(
        bot, event.chat.id, event.from_user.id, event.from_user.first_name
    )


async def on_user_left(event: ChatMemberUpdated) -> None:
    if event.chat.id == secrets.group_id:
        await sleep(5)
        await event.answer(views.left_message(event.old_chat_member.user.first_name))
