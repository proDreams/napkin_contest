import asyncio

from aiogram import Dispatcher, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram import types

from botlogic.handlers import send_file, simple, weather_fsm, payment
from botlogic.handlers.events import start_bot, stop_bot, on_user_left
from botlogic.handlers.filter_words import check_message
from botlogic.handlers import captcha_handler
from botlogic.settings import bot
from botlogic.utils.statesform import SendFileSteps, GetWeatherSteps, CaptchaState


async def start():
    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.pre_checkout_query.register(payment.pre_checkout_handler)

    dp.message.register(simple.start_command, Command(commands="start"))
    dp.message.register(simple.about_command, Command(commands="about"))
    dp.message.register(simple.help_command, Command(commands="help"))
    dp.message.register(send_file.send_file_start, Command(commands="get_file"))
    dp.message.register(send_file.send_file_get_data, SendFileSteps.get_code_from_user)

    dp.message.register(payment.pay_support_handler, Command(commands="paysupport"))
    dp.message.register(payment.send_invoice_handler, Command(commands="donate"))
    dp.message.register(payment.success_payment_handler, F.successful_payment)

    dp.message.register(weather_fsm.get_weather_command, Command(commands="weather"))
    dp.message.register(weather_fsm.get_by_city, GetWeatherSteps.BY_CITY)

    dp.chat_member.register(
        on_user_left, ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER)
    )
    dp.message_reaction.register(check_message)

    dp.chat_member.register(
        captcha_handler.on_user_joined,ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
    )
    dp.message.register(captcha_handler.on_captcha_response)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
