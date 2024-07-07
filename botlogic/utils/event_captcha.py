import random
import string
from PIL import Image, ImageDraw, ImageFont


async def create_captcha():
    width, height = 200, 100
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 40)
    captcha_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    draw.text((10, 10), captcha_code, fill="black", font=font)
    image_path = "capture.png"
    image.save(image_path, format="PNG")
    return image_path, captcha_code
