from aiogram.types import ChatMemberUpdated

from botlogic.settings import bot, secrets
from botlogic.utils.commands import set_commands
from botlogic.handlers import captcha_handler
from botlogic import views


async def start_bot() -> None:
    await set_commands(bot=bot)
    await bot.send_message(chat_id=secrets.admin_id, text=views.start_bot_msg())


async def stop_bot() -> None:
    await bot.send_message(chat_id=secrets.admin_id, text=views.stop_bot_msg())


async def on_user_left(event: ChatMemberUpdated) -> None:
    await event.answer(text=views.left_message(first_name=event.from_user.first_name))
