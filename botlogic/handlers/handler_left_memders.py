# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from aiogram import Router

from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER


# Инициализация роутера.
router = Router(name=__name__)


# Обработчик события "покинул(а) чат".
@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER << IS_MEMBER))
async def on_user_left(event: ChatMemberUpdated) -> None:
    """Прощальное сообщение предателю!!"""

    await event.answer(
        text=f"С прискорбием сообщаю, что {event.old_chat_member.user.full_name} покинул(а) наш чатик.\n\n"
        f"(предатель(ница))",
    )
