# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums.chat_type import ChatType

from app.config import GROUP_ID


# Инициализация роутера.
router = Router()


# Обработчик команды /start.
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Отправка приветственного сообщения/ссылки на группу и канал."""

    if ChatType.SUPERGROUP == message.chat.type and message.chat.id == GROUP_ID:
        await message.answer(
            text=f' Привет, {message.from_user.full_name} 👋🏻\n\n'
                 'Я бот для администрирования группы канал "Кот на салфетке", '
                 f'выполняю функцию "капчи" и защищаю группу от спамеров',
        )

    else:
        await message.answer(
            text=f' Привет, {message.from_user.full_name} 👋🏻\n\n'
                 f'Я бот для администрирования группы канал "Кот на салфетке", '
                 f'выполняю функцию "капчи" и защищаю группу от спамеров. \n\n'
                 f'Переходи поскорее в наш телеграмм-канал!',
        )
