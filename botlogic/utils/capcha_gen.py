import random
from PIL import Image, ImageDraw, ImageFont


def generate_example(
    width=200, height=50, font_path="arial.ttf", font_size=30, noise_level=0.1
):
    """
    Генерирует изображение с примером и правильный ответ
    """
    num1 = random.randint(1, 50)
    num2 = random.randint(1, 50)
    example = f"{num1} + {num2}"
    answer = num1 + num2
    background_color = (
        random.randint(160, 255),
        random.randint(160, 255),
        random.randint(160, 255),
    )
    font_color = (random.randint(0, 80), random.randint(0, 80), random.randint(0, 80))
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    text_width = draw.textlength(example, font=font)
    text_height = font.font.ascent
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), example, font=font, fill=font_color)
    for _ in range(int(width * height * noise_level)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        image.putpixel(
            (x, y),
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
    return {"image": image, "answer": answer}
