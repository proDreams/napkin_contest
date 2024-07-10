# -*- coding: utf-8 -*-


# Импорт необходимых модулей.

from aiogram.types import ChatMemberUpdated

from botlogic.data_base.requests import MyRequests


# Обработчик события "покинул(а) чат".
async def on_user_left(event: ChatMemberUpdated) -> None:
    """Прощальное сообщение предателю!!"""

    await event.answer(
        text=f"С прискорбием сообщаю, что {event.old_chat_member.user.full_name} покинул(а) наш чатик.\n\n"
        f"(предатель(ница))",
    )

    await MyRequests.clear_table()
