import os
import random
import string

from PIL import Image, ImageDraw, ImageFont


def generate_captcha() -> str:
    captcha_text = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5
        )
    )
    return captcha_text


def create_captcha_image(captcha_text) -> None:
    width, height = 200, 100
    image = Image.new('RGB', (width, height), color=(73, 109, 137))
    d = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 15)
    text_width, text_height = font.getsize(captcha_text)
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    d.text((x, y), captcha_text, fill=(255, 255, 0), font=font)
    image.save("captcha.png")


def delete_captcha_file(chat_id):
    captcha_image_path = f"captcha_{chat_id}.png"
    if os.path.exists(captcha_image_path):
        os.remove(captcha_image_path)
