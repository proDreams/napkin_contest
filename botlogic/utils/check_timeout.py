# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
import asyncio

from aiogram import Bot
from aiogram.types import ChatMemberUpdated

from botlogic.data_base.requests import MyRequests


# Функция запуска таймера.
async def check_captcha_timeout(user_id: int, bot: Bot, event: ChatMemberUpdated):
    """Запускает таймер на 3 минуты и удаляет пользователя, если он не проходит капчу.
    Очищает таблицу."""

    await asyncio.sleep(180)
    info_about_new_user = await MyRequests.get_user()

    if info_about_new_user is not None and info_about_new_user.check_captcha == "❌":
        await bot.ban_chat_member(chat_id=event.chat.id, user_id=user_id)

        await MyRequests.clear_table()
