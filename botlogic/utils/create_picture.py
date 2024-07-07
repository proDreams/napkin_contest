# -*- coding: utf-8 -*-


# Импорт необходимых модулей.
from PIL import Image, ImageDraw, ImageFont


# Функция генерации изображения с капчей.
def generate_image(operation: int, result: int) -> str:
    """Генерирует изображение с капчей."""

    width = 400
    height = 300
    text = f"{operation} + {result} = ?"
    path = "botlogic/pictures/checking_user.png"

    image = Image.new("RGB", (width, height), color=(240, 220, 200))

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("arial.ttf", 43)

    draw.text((200, 150), text, fill="black", font=font, anchor="mb")

    image.save(path)

    return path
