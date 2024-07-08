import asyncio

from aiogram import Dispatcher, F
from aiogram.filters import Command, ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

from botlogic.handlers import send_file, simple, weather_fsm, payment
from botlogic.handlers.events import start_bot, stop_bot, on_user_join, on_user_left
from botlogic.handlers.filter_words import check_message
from botlogic.settings import bot
from botlogic.utils.statesform import SendFileSteps, GetWeatherSteps
from botlogic.utils.check_captcha import (
    check_user_captcha,
    delete_admin_warning_callback,
    check_captcha_timeouts,
    handle_message,
    test_captcha,
)


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
    dp.message.register(test_captcha, Command(commands=["test_captcha"]))
    dp.message.register(handle_message)
    dp.message.register(check_user_captcha)
    dp.message.register(check_captcha_timeouts)
    dp.chat_member.register(
        on_user_join, ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
    )
    dp.callback_query.register(delete_admin_warning_callback, F.data == "admin_warning")
    dp.message.register(check_message)
    dp.chat_member.register(
        on_user_left, ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER)
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
