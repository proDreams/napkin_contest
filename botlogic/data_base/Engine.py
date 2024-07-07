# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from .models import engine, Base


# Функция подключения к базе данных.
async def async_main():
    """Подключает бота к базе данных."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
