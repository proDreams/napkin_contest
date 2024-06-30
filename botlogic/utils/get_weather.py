import requests

from botlogic.settings import secrets


def request_weather(city: str) -> str | None:
    result = requests.get(
        url="https://api.openweathermap.org/data/2.5/find",
        params={
            "q": city,
            "type": "like",
            "units": "metric",
            "lang": "ru",
            "APPID": secrets.weather_key.get_secret_value(),
        },
    ).json()
    if result.get("count") == 0:
        return

    return generate_result(data=result, city=city)


def generate_result(data: dict, city: str) -> str:
    temp = int(data["list"][0]["main"]["temp"])
    feels_like = data["list"][0]["main"]["feels_like"]
    pressure = int(data["list"][0]["main"]["pressure"]) * 0.75
    humidity = data["list"][0]["main"]["humidity"]
    wind_speed = int(data["list"][0]["wind"]["speed"])
    rain = "не ожидается" if data["list"][0]["rain"] is None else "ожидается"
    snow = "не ожидается" if data["list"][0]["snow"] is None else "ожидается"
    weather = data["list"][0]["weather"][0]["description"]

    return f"""
<b>Прогноз погоды в городе {city}</b>

Сейчас температура {temp}°C
Ощущается как {feels_like}°
⛅️{weather}⛅️  
💨 Скорость ветра {wind_speed}м/с 💨
Давление {pressure} мм рт.ст.
Влажность {humidity}%
💦 Дождь {rain}
❄️ Снег {snow}
"""
