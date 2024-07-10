import string

from aiogram import Router, F

from botlogic.settings import BAN_WORDS


router = Router(name=__name__)


@router.message(F.text)
def check_ban_word(message: str) -> tuple[bool, str]:
    contains_ban_word = False
    message_words = set(
        message.translate(str.maketrans("", "", string.punctuation)).split()
    )
    filtered_message = message

    for word in message_words:
        if word.lower() in BAN_WORDS:
            filtered_message = filtered_message.replace(word, "*" * len(word))
            contains_ban_word = True

    return contains_ban_word, filtered_message
