from aiogram.types import Message

from botlogic import views
from botlogic.settings import secrets
from botlogic.utils.api_actions import register_user


async def start_command(message: Message) -> None:
    if message.chat.id != secrets.group_id:
        register_user(
            chat_id=message.chat.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
        await message.answer(text=views.start_message())


async def about_command(message: Message) -> None:
    await message.answer(text=views.about_message())


async def help_command(message: Message) -> None:
    if message.chat.id != secrets.group_id:
        await message.answer(text=views.help_message())
    else:
        await message.answer(text=views.help_chat_message())
