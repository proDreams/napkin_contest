import asyncio
import time
from aiogram import Bot, types
from aiogram.types import (
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatMemberMember,
    ChatMemberLeft,
    ChatMemberUpdated,
)
import os
import random
from PIL import Image, ImageDraw, ImageFont
import logging

# Инициализация логгера
logger = logging.getLogger(__name__)

# Хранилище данных пользователей
users_data = {}


# Генерация капчи
def generate_captcha():
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    result = num1 + num2

    # Создание изображения капчи
    img = Image.new("RGB", (400, 160), color=(255, 255, 255))
    d = ImageDraw.Draw(img)

    font = ImageFont.load_default(90)
    d.text((35, 25), f"{num1} + {num2} = ?", font=font, fill=(0, 0, 0))

    # Создание пути для сохранения изображения
    img_dir = "captcha_images"
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, f"captcha_{num1}_{num2}.png")
    img.save(img_path)

    logger.info(
        f"Каптча сгенерирована: {num1} + {num2} = {result}, сохранена в {img_path}"
    )

    return img_path, result


# Отправка капчи пользователю
async def send_captcha(bot: Bot, chat_id: int, user_id: int, first_name: str):
    img_path, result = generate_captcha()
    users_data[user_id] = {
        "result": result,
        "attempts": 0,
        "start_time": time.time(),
        "captcha_message_id": None,
        "first_name": first_name,  # Сохранение first_name
    }

    photo = FSInputFile(img_path)
    caption = (
        f"{first_name}, приветствуем!\n\nРеши пожалуйста это уравнение, "
        f"чтобы убедиться, что ты не бот.\n\nНа решение тебе дается "
        f"1 минута и 3 попытки"
    )
    sent_message = await bot.send_photo(chat_id, photo, caption=caption)
    users_data[user_id]["captcha_message_id"] = sent_message.message_id
    logger.info(f"Капча отправлена {user_id} в чат {chat_id}")
    asyncio.create_task(check_captcha_timeouts(bot, chat_id, user_id))


# Проверка истечения времени на капчу
async def check_captcha_timeouts(bot: Bot, chat_id: int, user_id: int):
    while True:
        current_time = time.time()
        data = users_data.get(user_id)
        if data:
            elapsed_time = current_time - data["start_time"]
            remaining_time = 60 - elapsed_time
            if elapsed_time > 60:
                try:
                    await bot.delete_message(chat_id, data["captcha_message_id"])
                except Exception as e:
                    logger.warning(f"Ошибка при удалении сообщения с капчей: {e}")

                if "warning_message_id" in data:
                    try:
                        await bot.delete_message(chat_id, data["warning_message_id"])
                    except Exception as e:
                        logger.warning(
                            f"Ошибка при удалении предупреждающего сообщения: {e}"
                        )

                try:
                    await bot.ban_chat_member(chat_id, user_id)
                    first_name = users_data[user_id]["first_name"]
                    await bot.send_message(
                        chat_id,
                        f"Пользователь {first_name} был исключен из чата по причине "
                        "истечения времени на выполнение капчи.\n\n Как думаете, вернется?",
                    )
                    users_data.pop(user_id, None)
                    logger.info(
                        f"Пользователь {user_id} был исключен из чата по причине истечения времени на выполнение капчи"
                    )
                    await bot.unban_chat_member(
                        chat_id, user_id
                    )  # Убираем пользователя из бана
                except Exception as e:
                    if "can't remove chat owner" in str(e):
                        if "warning_message_id" in data:
                            try:
                                await bot.delete_message(
                                    chat_id, data["warning_message_id"]
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Ошибка при удалении предупреждающего сообщения: {e}"
                                )

                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="🪄 Волшебная палочка",
                                        callback_data="admin_warning",
                                    )
                                ]
                            ]
                        )
                        sent_message = await bot.send_message(
                            chat_id,
                            "Кот, ну нельзя удалять админа",
                            reply_markup=keyboard,
                        )
                        users_data[user_id][
                            "warning_message_id"
                        ] = sent_message.message_id
                        logger.info(
                            f"Пользователь {user_id} попытался удалить админа в чате {chat_id}"
                        )
                break  # Выходим из цикла после удаления данных пользователя
            else:
                logger.info(
                    f"Оставшееся время для пользователя {user_id}: {int(remaining_time)} секунд"
                )
        await asyncio.sleep(5)  # Проверяем каждые 5 секунд


# Проверка ответа пользователя на капчу
async def check_user_captcha(
    bot: Bot, chat_id: int, user_id: int, text: str, message: types.Message
):
    if user_id not in users_data:
        logger.warning(f"User {user_id} is not in user_data")
        return

    elapsed_time = time.time() - users_data[user_id]["start_time"]
    if elapsed_time > 60:  # Прописываем условие, если время на выполнение капчи истекло
        await bot.delete_message(chat_id, message.message_id)
        await bot.delete_message(chat_id, users_data[user_id]["captcha_message_id"])
        await bot.send_message(
            chat_id, "Время на выполнение капчи истекло. Попробуйте снова."
        )
        users_data.pop(user_id, None)
        return
    # Если text равен None, просто игнорируем это и только потом переходим к основному решению
    if text is None:
        return
    correct_result = users_data[user_id]["result"]
    if (
        not text.isdigit() or int(text) != correct_result
    ):  # Проверка на неправильный ответ (не цифры или неправильный ответ)
        await bot.delete_message(chat_id, message.message_id)
        users_data[user_id]["attempts"] += 1
        remaining_attempts = 3 - users_data[user_id]["attempts"]
        remaining_time = 60 - elapsed_time

        if users_data[user_id]["attempts"] >= 3:
            try:
                await bot.ban_chat_member(
                    chat_id, user_id
                )  # Исключаем пользователя посредством бана
                first_name = users_data[user_id]["first_name"]
                await bot.send_message(
                    chat_id, f"{first_name} не прошел(а) проверку. Она вернется?"
                )
                users_data.pop(user_id, None)
                logger.info(
                    f"Пользователь {first_name} был исключен из чата по причине отсутствия правильного ответа"
                )
                await bot.unban_chat_member(
                    chat_id, user_id
                )  # Немедленное снятие бана, потому что нужно давать второй шанс
            except Exception as e:
                if "can't remove chat owner" in str(e):
                    if "warning_message_id" in users_data[user_id]:
                        await bot.delete_message(
                            chat_id, users_data[user_id]["warning_message_id"]
                        )
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="🪄 Волшебная палочка",
                                    callback_data="admin_warning",
                                )
                            ]
                        ]
                    )
                    sent_message = await bot.send_message(
                        chat_id, "Кот, ну нельзя удалять админа", reply_markup=keyboard
                    )
                    users_data[user_id]["warning_message_id"] = sent_message.message_id
                    logger.info(
                        f"Пользователь {user_id} попытался удалить админа в чате {chat_id}"
                    )
        else:
            if "warning_message_id" in users_data[user_id]:
                await bot.delete_message(
                    chat_id, users_data[user_id]["warning_message_id"]
                )
                users_data[user_id].pop(
                    "warning_message_id", None
                )  # Удаляем предупреждающее сообщение из данных

            warning_message = await bot.send_message(
                chat_id,
                f"Ответ неправильный, попробуй еще. "
                f"Осталось {remaining_attempts} попыток.\n\n"
                f"Оставшееся время: {int(remaining_time)} секунд",
            )
            users_data[user_id]["warning_message_id"] = warning_message.message_id
        return

    # Если ответ правильный
    await bot.delete_message(chat_id, message.message_id)
    await bot.delete_message(chat_id, users_data[user_id]["captcha_message_id"])
    if "warning_message_id" in users_data[user_id]:
        await bot.delete_message(chat_id, users_data[user_id]["warning_message_id"])

    first_name = users_data[user_id]["first_name"]
    users_data.pop(user_id, None)
    from botlogic.views import join_message

    await join_message(bot, chat_id, user_id, first_name)
    logger.info(f"Пользователь {user_id} дал правильный ответ")


async def handle_message(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    if user_id in users_data:
        await check_user_captcha(message.bot, chat_id, user_id, text, message)


async def test_captcha(message: types.Message, bot):
    # Добавляем имитацию добавления нового пользователя, чтобы пройти отладку без сторонних учеток
    new_member = ChatMemberMember(
        status="member", user=message.from_user, until_date=None, is_member=True
    )
    old_member = ChatMemberLeft(status="left", user=message.from_user, until_date=None)
    event = ChatMemberUpdated(
        chat=message.chat,
        from_user=message.from_user,
        date=message.date,
        old_chat_member=old_member,
        new_chat_member=new_member,
    )

    from botlogic.handlers.events import on_user_join

    await on_user_join(event, bot)


async def delete_admin_warning_callback(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if user_id in users_data:
        data = users_data[user_id]

        # Попробуем удалить сообщения, если они существуют. Но удалить сообщение с /test_captcha
        # все равно никак не выходит, а играться с message_id впадлу

        if "captcha_message_id" in data:
            try:
                await call.bot.delete_message(chat_id, data["captcha_message_id"])
            except Exception as e:
                logger.warning(f"Ошибка при удалении сообщения с капчей: {e}")

        if "warning_message_id" in data:
            try:
                await call.bot.delete_message(chat_id, data["warning_message_id"])
            except Exception as e:
                logger.warning(f"Ошибка при удалении предупреждающего сообщения: {e}")

        if "test_captcha_message_id" in data:
            try:
                await call.bot.delete_message(chat_id, data["test_captcha_message_id"])
            except Exception as e:
                logger.warning(
                    f"Ошибка при удалении сообщения пользователя с командой: {e}"
                )

        # Удаляем сообщение с волшебной палочкой
        try:
            await call.bot.delete_message(chat_id, call.message.message_id)
        except Exception as e:
            logger.warning(f"Ошибка при удалении сообщения с волшебной палочкой: {e}")

        # Удаляем данные пользователя
        users_data.pop(user_id, None)

        await call.answer("Сообщения удалены и данные очищены")
