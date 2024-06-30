from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from botlogic.settings import secrets


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="start", description="Начало работы"),
        BotCommand(command="get_file", description="Получение файла с материалами"),
        BotCommand(command="weather", description="Получить прогноз погоды"),
        BotCommand(command="help", description="Помощь по доступным командам"),
        BotCommand(command="about", description="Информация о боте"),
    ]

    commands_chat = [
        BotCommand(command="weather", description="Получить прогноз погоды"),
        BotCommand(command="help", description="Помощь по доступным командам"),
        BotCommand(command="about", description="Информация о боте"),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(
        commands=commands_chat, scope=BotCommandScopeChat(chat_id=secrets.group_id)
    )
