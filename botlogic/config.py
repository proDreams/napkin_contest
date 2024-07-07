# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
import os

from dotenv import load_dotenv


# Класс конфигурации.
class Config:
    """Класс конфигурации.
    Хранит токен бота, ID группы, ID админа, адрес базы данных,
    ключ для работы с погодой, ключи для работы с аудиофайлами.

    """

    def __init__(
        self,
        token: str,
        group_id: int,
        audio_secret_key: str,
        audio_key_id: int,
        weather_key: str,
        admin_id: int,
        data_base_url: str,
    ) -> None:
        self.__token = token
        self.__group_id = group_id
        self.__admin_id = admin_id
        self.__weather_key = weather_key
        self.__audio_key_id = audio_key_id
        self.__audio_secret_key = audio_secret_key
        self.__data_base_url = data_base_url

    def get_base_configuration(self) -> tuple[str, int, int]:
        return self.__token, self.__group_id, self.__admin_id

    def get_data_base_url(self) -> str:
        return self.__data_base_url

    def get_app_configuration(self):
        return self.__audio_secret_key, self.__weather_key, self.__audio_key_id


load_dotenv()
# Инициализация объекта класса Config.
MyConfig = Config(
    token=os.getenv("TOKEN"),
    group_id=int(os.getenv("GROUP_ID")),
    audio_secret_key=os.getenv("AUDIO_SECRET_KEY"),
    audio_key_id=int(os.getenv("AUDIO_KEY_ID")),
    weather_key=os.getenv("WEATHER_KEY"),
    admin_id=int(os.getenv("ADMIN_ID")),
    data_base_url=os.getenv("DATA_BASE_URL"),
)


# Инициализация переменных.
TOKEN, GROUP_ID, ADMIN_ID = MyConfig.get_base_configuration()
DATA_BASE_URL = MyConfig.get_data_base_url()
AUDIO_KEY_ID, AUDIO_SECRET_KEY, WEATHER_KEY = MyConfig.get_app_configuration()

# Инициализация словаря для хранения таймеров.
user_timers: dict = {}
