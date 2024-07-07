# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
import asyncio

from datetime import datetime

import random

from aiogram import Router, F
from aiogram.types import ChatMemberUpdated, BufferedInputFile, Message
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

from app.data_base.requests import MyRequests
from app.utils.create_picture import generate_image
from app.utils.check_timeout import check_captcha_timeout
from .loader import bot
from app.config import user_timers


# Инициализация роутера.
router = Router(name=__name__)


# Код обработчика события "присоединился к чату".
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated) -> None:
    """Приветствие нового участника и отправка фото-капчи,
    занос пользователя в базу данных и включение таймера для пользователя на 3 минуты."""

    num_0 = random.randint(0, 9)
    num_1 = random.randint(0, 9)
    result = num_1 + num_0
    path = generate_image(num_0, num_1)

    await event.answer_photo(
        photo=BufferedInputFile(open(path, "rb").read(), 'picture_of_capcha'),
        caption=f'Здравствуй, '
                f'<a href="tg://user?id={event.new_chat_member.user.id}"><i>{event.new_chat_member.user.full_name}</i></a> 👋🏻\n\n'
                'Для подтверждения, что ты не спамер, '
                'отправь сообщение с ответом на задачу в течении <b>3-х</b> минут:\n'
                '<i>Какой результат выражения на изображении?</i>',
    )

    await MyRequests.add_new_user(
        user_id=event.new_chat_member.user.id,
        check_captcha=f'❌',
        time=f'{datetime.now()}',
        result=result
    )

    user_timers[event.new_chat_member.user.id] = asyncio.create_task(
        check_captcha_timeout(event.new_chat_member.user.id, bot, event)

    )


# Обработчик текстовых сообщений.
@router.message(F.text)
async def send_answer(message: Message) -> None:
    """Взятие id нового пользователя из базы данных и сравнение его с id отправителя сообщения,
    Проверка ответа нового пользователя, удаление таймера, удаление пользователя из базы данных.
    """

    user_id = message.from_user.id
    info_about_new_user = await MyRequests.get_user()

    if user_id == info_about_new_user.user_id:
        if message.text == str(info_about_new_user.result):
            await message.answer(
                text=f'Добро пожаловать в нашу группу, <i>{message.from_user.full_name}</i>!\n\n'
                     f'Давай знакомиться: расскажи немного о себе, своих увлечениях и о своём пути в программировании.'
            )
            await MyRequests.clear_table()

            user_timers[user_id].cancel()
            del user_timers[user_id]

        else:
            if info_about_new_user.count_attempts >= 1:
                count_attempts = info_about_new_user.count_attempts - 1

                await message.answer(
                    text=f'<i>Неправильно 😢\n</i>'
                         f'Попробуй еще раз, у тебя еще {count_attempts} попытки!\n'
                )

                await MyRequests.set_item('count_attempts', count_attempts)

            else:
                await bot.ban_chat_member(
                    chat_id=message.chat.id,
                    user_id=user_id
                )

                await MyRequests.clear_table()

                user_timers[user_id].cancel()
                del user_timers[user_id]
