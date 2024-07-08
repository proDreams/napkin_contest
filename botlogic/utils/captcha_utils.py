import os
from datetime import timedelta

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from PIL import Image, ImageDraw, ImageFont

from botlogic.settings import secrets


async def ban_user(message: Message, state: FSMContext = None):
    remove_captcha(user_id=message.from_user.id)
    await message.bot.ban_chat_member(
        chat_id=secrets.group_id,
        user_id=message.from_user.id,
        until_date=timedelta(seconds=35),
    )

    if state:
        await state.clear()


def remove_captcha(user_id):
    os.remove(f"files/{user_id}.png")


def generate_image(expression: str, user_id: int):
    image = Image.new(mode="RGB", size=(800, 600), color="white")
    draw = ImageDraw.Draw(im=image)
    text = expression + " = ?"
    font_size = 50
    try:
        font = ImageFont.truetype(
            font="res/Gilroy-Medium.ttf",
            size=font_size,
        )
    except IOError:
        font = ImageFont.load_default()
    text_box = draw.textbbox(xy=(0, 0), text=text, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    text_x = (800 - text_width) // 2
    text_y = (600 - text_height) // 2
    draw.text(xy=(text_x, text_y), text=text, font=font, fill="black")
    path = f"files/{user_id}.png"
    image.save(fp=path)
