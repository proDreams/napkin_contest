# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from .models import async_session, NewUser
from sqlalchemy import select, update, delete


# Класс запросов к базе данных.
class Requests:
    """Класс для запросов к базе данных."""

    def __init__(self, session) -> None:
        self.session = session

    async def add_new_user(self, user_id: int, check_captcha: str, time: str, result: int) -> None:
        async with self.session:
            new_user = NewUser(
                user_id=user_id,
                check_captcha=check_captcha,
                time=time,
                result=result,
            )
            self.session.add(new_user)
            await self.session.commit()

    async def get_user(self) -> NewUser | None:
        async with self.session:
            user = await self.session.execute(select(NewUser))
            return user.scalars().first()

    async def set_item(self, item: str, mean: str | int) -> None:
        async with self.session:
            stmt = update(NewUser).where(NewUser.id == 1).values({item: mean})
            await self.session.execute(stmt)
            await self.session.commit()

    async def clear_table(self):
        async with self.session:
            await self.session.execute(delete(NewUser))
            await self.session.commit()


# Инициализация объекта класса Requests.
MyRequests = Requests(async_session())
