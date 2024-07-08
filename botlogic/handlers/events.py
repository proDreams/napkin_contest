from aiogram.types import ChatMemberUpdated, Message, BufferedInputFile, File

from botlogic.settings import bot, secrets
from botlogic.utils.commands import set_commands
from botlogic import views

from aiogram.fsm.state import State, StatesGroup

from aiogram.fsm.context import FSMContext

from aiogram import Bot, Router

import random

from PIL import ImageDraw, Image

import io


async def start_bot() -> None:
    await set_commands(bot=bot)
    await bot.send_message(chat_id=secrets.admin_id, text=views.start_bot_msg())


async def stop_bot() -> None:
    await bot.send_message(chat_id=secrets.admin_id, text=views.stop_bot_msg())


router = Router()


# Хранение капчи
captcha_sessions = {}


def generate_captcha():
    number_1 = random.randint(1, 100)
    number_2 = random.randint(1, 100)

    sum_nums = number_1 + number_2

    # Создания изображения
    image = Image.new("RGB", (100, 40), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.text((10, 5), f"{number_1} + {number_2} =", fill=(255, 255, 255))

    bytes = io.BytesIO()
    image.save(bytes, "PNG")
    bytes.seek(0)

    return bytes, sum_nums


@router.message()
async def on_user_join(event: ChatMemberUpdated, state: FSMContext) -> None:
    await event.answer("Привет! Пожалуйста, решите капчу, чтобы продолжить.")

    # Генерация капчи
    captcha_image, solution = generate_captcha()
    captcha_sessions[event.from_user.id] = {
        "solution": solution,
        "attempts": 0,
        "messages": [],
    }

    # Отправка капчи пользователю
    photo = BufferedInputFile(captcha_image.read(), filename="captcha.png")

    captcha_message = await event.answer_photo(
        photo=photo, caption="Решите задачу на изображении и отправьте ответ:"
    )

    captcha_sessions[event.from_user.id]["messages"].append(captcha_message.message_id)


@router.message()
async def check_captcha(message: Message, bot: Bot):
    user_id = message.from_user.id

    if user_id in captcha_sessions:

        try:
            user_answer = int(message.text)
            if user_answer == captcha_sessions[user_id]["solution"]:
                await message.reply("Капча пройдена успешно!")

                # Here
                # await event.answer(text=views.join_message(first_name=event.from_user.first_name))

                for msg_id in captcha_sessions[user_id]["messages"]:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                del captcha_sessions[user_id]
            else:
                captcha_sessions[user_id]["attempts"] += 1
                captcha_sessions[user_id]["messages"].append(message.message_id)
                if captcha_sessions[user_id]["attempts"] >= 3:

                    await message.reply(
                        "Слишком много неверных попыток. Вы будете исключены из группы."
                    )

                    for msg_id in captcha_sessions[user_id]["messages"]:

                        await bot.ban_chat_member(
                            chat_id=message.chat.id, user_id=user_id
                        )

                    await bot.kick_chat_member(chat_id=message.chat.id, user_id=user_id)

                    del captcha_sessions[user_id]
                else:
                    await message.reply("Неверный ответ. Попробуйте ещё раз.")
        except ValueError:
            await message.reply("Пожалуйста, введите числовой ответ.")
    else:
        await message.reply("Пожалуйста, используйте команду /start для начала.")


async def on_user_left(event: ChatMemberUpdated) -> None:
    await event.answer(text=views.left_message(first_name=event.from_user.first_name))
