import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from PIL import Image, ImageDraw
import botlogic.settings as token
import io

dp = Dispatcher()
bot = token
# Словарь для хранения капчи и попыток
captcha_sessions = {}

# Генерация капчи
def generate_captcha():
    number_1 = random.randint(1, 100)
    number_2 = random.randint(1, 100)

    sum_nums = number_1 + number_2

    # Создания изображения 
    image = Image.new('RGB', (100, 40), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.text((10, 5), f"{number_1} + {number_2} =", fill=(0, 0, 0))

    bytes = io.BytesIO()
    image.save(bytes, 'PNG')
    bytes.seek(0)


    return bytes, sum_nums


async def send_welcome(event: types.ChatMemberUpdated, message: types.Message):
    await message.reply("Привет! Пожалуйста, решите капчу, чтобы продолжить.")

    # Генерация капчи
    captcha_image, solution = generate_captcha()
    captcha_sessions[message.from_user.id] = {'solution': solution, 'attempts': 0, 'messages': []}
    
    # Отправка капчи пользователю
    photo = types.BufferedInputFile(captcha_image.read(), filename="captcha.png")
    captcha_message = await message.answer_photo(photo=photo, caption="Решите задачу на изображении и отправьте ответ:")
    captcha_sessions[message.from_user.id]['messages'].append(captcha_message.message_id)



@dp.message()
async def check_captcha(message: types.Message):
    user_id = message.from_user.id
    
    if user_id in captcha_sessions:
        try:
            user_answer = int(message.text)
            if user_answer == captcha_sessions[user_id]['solution']:
                await message.reply("Капча пройдена успешно!")
                for msg_id in captcha_sessions[user_id]['messages']:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                del captcha_sessions[user_id]
            else:
                captcha_sessions[user_id]['attempts'] += 1
                captcha_sessions[user_id]['messages'].append(message.message_id)
                if captcha_sessions[user_id]['attempts'] >= 3:

                    await message.reply("Слишком много неверных попыток. Вы будете исключены из группы.")

                    for msg_id in captcha_sessions[user_id]['messages']:

                        await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
                        
                    await bot.kick_chat_member(chat_id=message.chat.id, user_id=user_id)

                    del captcha_sessions[user_id]
                else:
                    await message.reply("Неверный ответ. Попробуйте ещё раз.")
        except ValueError:
            await message.reply("Пожалуйста, введите числовой ответ.")
    else:
        await message.reply("Пожалуйста, используйте команду /start для начала.")