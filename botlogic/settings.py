import logging

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BAN_WORDS = set(line.strip() for line in open("res/ban_words.txt"))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs.txt")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


class Secrets(BaseSettings):
    token: SecretStr
    admin_id: int
    group_id: int 
    weather_key:SecretStr
    audio_key_id: str
    audio_key_secret:SecretStr
    api_url: str = "http://127.0.0.1:8000/bot"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf8", extra="ignore"
    )


secrets = Secrets()

bot = Bot(
    token=secrets.token.get_secret_value(),
    default=DefaultBotProperties(parse_mode="HTML"),
)
