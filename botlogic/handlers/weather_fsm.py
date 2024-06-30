from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from botlogic import views
from botlogic.settings import bot
from botlogic.utils.get_weather import request_weather
from botlogic.utils.statesform import GetWeatherSteps


async def get_weather_command(message: Message, state: FSMContext) -> None:
    await message.answer(text=views.enter_city())
    await state.set_state(state=GetWeatherSteps.BY_CITY)


async def get_by_city(message: Message, state: FSMContext) -> None:
    if message.text.lower() == "отмена":
        await message.answer(text=views.abort_weather())
        await state.clear()
    else:
        result = request_weather(city=message.text)
        if result:
            await message.reply(text=result)
            await message.answer(text=views.weather_request_done())
            await state.clear()
        else:
            await bot.send_message(
                chat_id=message.chat.id, text=views.weather_wrong_city()
            )
            await state.set_state(state=GetWeatherSteps.BY_CITY)
