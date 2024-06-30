import os
import time

from aiogram.types import Message

from botlogic import views
from botlogic.settings import logger
from botlogic.utils.check_ban_word import check_ban_word
from botlogic.utils.transcribe_voice import (
    get_create_url_response,
    get_query_url_response,
)


async def check_message(message: Message) -> None:
    if message.text:
        contains_ban_word, filtered_message = check_ban_word(message=message.text)

        if contains_ban_word:
            await message.delete()
            logger.info(
                f"Удалено сообщение от пользователя {message.from_user.username}: {message.text}"
            )
            await message.answer(
                views.filtered_message(
                    username=message.from_user.username, message=filtered_message
                )
            )

    elif message.voice:
        create_url, filename = await get_create_url_response(message=message)
        if create_url.status_code == 200:

            while True:
                query_url = await get_query_url_response(create_url)

                if query_url.status_code == 200:
                    query_result = query_url.json()
                    if query_result.get("code") == 11000:
                        if query_result.get("result"):
                            result = query_result.get("result").replace("\n\n", " ")
                            await message.reply(f"<pre><code>{result}</code></pre>")
                            os.remove(filename)
                        break
                    elif query_result.get("code") == 11001:
                        time.sleep(3)
                        continue

                    break

                break
