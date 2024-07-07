# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from app.config import DATA_BASE_URL


# Инициализация базы данных.
engine = create_async_engine(DATA_BASE_URL)


# Инициализация асинхронной сессии.
async_session = async_sessionmaker(engine)


# Класс базы данных.
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Класс модели таблицы NewUser.
class NewUser(Base):
    """Модель таблице NewUser."""

    __tablename__ = "NewUser"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    check_captcha: Mapped[str] = mapped_column(String(2), nullable=False)
    time: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[int] = mapped_column(Integer, nullable=False)
    count_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
