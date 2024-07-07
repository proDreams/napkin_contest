import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext

from botlogic import views
from botlogic.settings import bot
from botlogic.utils.event_captcha import create_captcha
from botlogic.utils.statesform import CaptchaState


async def on_user_joined(event: types.ChatMemberUpdated, state: FSMContext) -> None:
    captcha_path, correct_captcha = await create_captcha()
    user_id = event.from_user.id
    with open(captcha_path, "rb") as photo:
        await event.answer_photo(
            types.BufferedInputFile(photo.read(), filename="captcha.png"),
            caption="Подтвердите, что вы не робот, введя текст с изображения",
        )
    await state.set_state(state=CaptchaState.waiting_for_captcha)
    await state.update_data(
        user_id=event.from_user.id,
        correct_captcha=correct_captcha,
        counter=3,
        chat_id=event.chat.id,
        user_first_name=event.from_user.first_name,
    )
    await asyncio.sleep(60)
    if (await state.get_state()) == CaptchaState.waiting_for_captcha:
        await event.answer(
            f"Чего молчим? {event.from_user.first_name} Пошел(ла) ка ты отсюда увОжаемый"
        )
        chat_id = event.chat.id
        user_id = event.from_user.id
        await bot.ban_chat_member(chat_id, user_id)
        await state.clear()


async def on_captcha_response(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    correct_captcha = data.get("correct_captcha")
    counter = data.get("counter")
    user_id = data.get("user_id")
    chat_id = data.get("chat_id")
    user_first_name = data.get("user_first_name")
    try:
        if message.text.upper() == correct_captcha:
            await message.answer(text=f"Молодец! Проверка коточата пройдена")
            await message.answer(text=views.join_message(first_name=user_first_name))
            await state.clear()
        elif message.text.upper() != correct_captcha:
            counter = data.get("counter")
            if counter > 1:
                await state.update_data(counter=counter - 1)
                await message.answer(text=f"Неправильно, осталось {counter-1} попыток")
            else:
                await message.answer(text=f"Ну ффсе  пока пока - валидавай")
                chat_id = message.chat.id
                user_id = message.from_user.id
                await bot.ban_chat_member(chat_id, user_id)
                await state.clear()
    except AttributeError:
        pass
