import requests
from aiogram.types import Message
from requests import Response

from botlogic.settings import bot, secrets


async def get_create_url_response(message: Message) -> tuple[Response, str]:
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    filename = f"files/audio{file_id}.mp3"
    await bot.download_file(file_path=file.file_path, destination=filename)
    files = {"file": open(filename, "rb")}

    headers = {"keyId": secrets.audio_key_id, "keySecret": secrets.audio_key_secret}
    create_url = "https://api.speechflow.io/asr/file/v1/create?lang=ru"

    response = requests.post(url=create_url, headers=headers, files=files)

    return response, filename


async def get_query_url_response(response: Response) -> Response:
    headers = {"keyId": secrets.audio_key_id, "keySecret": secrets.audio_key_secret}
    create_result = response.json()
    query_url = "https://api.speechflow.io/asr/file/v1/query?taskId="
    query_url += f"{create_result.get("taskId")}&resultType=4"

    return requests.get(url=query_url, headers=headers)
