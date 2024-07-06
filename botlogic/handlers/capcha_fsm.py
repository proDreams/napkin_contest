from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
import io
from botlogic import views
from botlogic.settings import bot
from botlogic.utils.statesform import CapchaSteps
from botlogic.utils.capcha_gen import generate_example
from aiogram.types import ChatMemberUpdated
from asyncio import sleep


async def get_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user = message.from_user.first_name
    if message.text == str(data["answer"]):
        await message.answer(text="Верно!")
        await message.answer(text=views.join_message(user))
        await state.clear()
    elif message.from_user.id == data["new_user_id"]:
        await message.answer(text="Неверно")
        number = data["try_number"]
        data["messages_list"].append(message.message_id)
        await state.update_data(message_list=data["messages_list"])
        if number > 1:
            await message.answer(text=f"Осталось попыток: {number-1}")
            await state.update_data(try_number=number - 1)
        else:
            await message.answer(text="Вы не прошли проверку!")
            chat_id = message.chat.id
            user_id = message.from_user.id
            await bot.send_message(
                chat_id=chat_id, text=f"Ахтунг! Бот {user} детектед!"
            )
            await bot.delete_messages(chat_id, message_ids=data["messages_list"])
            await bot.ban_chat_member(chat_id, user_id)
            await state.clear()


async def on_user_join_request(event: ChatMemberUpdated, state: FSMContext) -> None:
    user = event.from_user.first_name
    image_bytes = io.BytesIO()
    image_bytes.name = "image.png"
    example = generate_example()
    example["image"].save(image_bytes, format="PNG")
    image_bytes.seek(0)
    user_id = event.from_user.id
    await state.update_data(answer=example["answer"])
    await state.update_data(try_number=3)
    await state.update_data(new_user_id=user_id)
    await state.update_data(messages_list=[])
    await event.answer_photo(
        BufferedInputFile(image_bytes.read(), filename="img.png"),
        caption=f"{user}, для вступления в группу необходимо"
        " вычислить результат математического выражения. На решение вам дается 3 минуты.",
    )
    await state.set_state(state=CapchaSteps.asking)
    # Ограничение по времени
    await sleep(180)
    if (await state.get_state()) == CapchaSteps.asking:
        await event.answer("Время вышло. К сожалению вам не разрешено присоединиться.")
        chat_id = event.chat.id
        await bot.send_message(chat_id=chat_id, text=f"Ахтунг! Бот {user} детектед!")
        await bot.delete_messages(
            chat_id, message_ids=(await state.get_data())["messages_list"]
        )
        await bot.ban_chat_member(chat_id, user_id)
        await state.clear()
