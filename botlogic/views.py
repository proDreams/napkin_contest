def start_bot_msg() -> str:
    return "Бот запущен"


def stop_bot_msg() -> str:
    return "Бот остановлен"


def send_file_start_msg() -> str:
    return """Для получения файла с дополнительными материалами к посту,
пожалуйста введите код из поста."""


def send_file_wrong_input() -> str:
    return """Неверный код файла.
Повторите ввод.

Код файла состоит только из цифр"""


def send_file_please_wait() -> str:
    return """Запрос обрабатывается.
Пожалуйста, ожидайте"""


def send_file_not_found() -> str:
    return """Файл с указанным цифровым кодом не найден.
Убедитесь в правильности введённого кода."""


def file_caption(file_title: str, post_url: str, post_telegram_link: str) -> str:
    if post_url:
        return f'Файл к посту: {file_title}\nПост на сайте: <a href="{post_url}">pressanybutton.ru</a>\nПост на канале: <a href="{post_telegram_link}">Код на салфетке</a>'
    return f"Файл к посту: {file_title}"


def start_message() -> str:
    return """Добро пожаловать

Здесь вы можете получить дополнительные материалы к посту на канале "Код на салфетке".
Для получения материала, необходимо отправить команду /get_file. 
Затем отправить цифровой код из поста. 
В ответ будет прислано сообщение содержащее архив с материалами к посту.

Узнать все доступные команды можно отправив /help"""


def about_message() -> str:
    return """\"Бот на салфетке' создан для канала \"Код на салфетке\"
Ссылка на канал: https://t.me/press_any_button
Чат канала: https://t.me/+cm-ITbA-JTczMTRi
Сайт канала: https://pressanybutton.ru

Автор: proDream"""


def help_message() -> str:
    return """Помощь по доступным командам:
/start - запуск бота и регистрация пользователя
/get_file - получение файла с материалами к посту с канала
/help - помощь по доступным командам. Вы сейчас здесь 😉
/about - информация о боте"""


def help_chat_message() -> str:
    return """Помощь по доступным командам:
/help - помощь по доступным командам. Вы сейчас здесь 😉
/about - информация о боте"""


def enter_city() -> str:
    return """Введите название города на русском языке
Или 'Отмена' для отмены запроса."""


def weather_request_done() -> str:
    return "Рад был помочь. До встречи 🫶🏻"


def abort_weather() -> str:
    return "Запрос погоды отменён. До встречи 🫶🏻"


def weather_wrong_city() -> str:
    return "Неправильный город, повторите ввод или введите 'Отмена' для отмены запроса."


def filtered_message(username: str, message: str) -> str:
    return f"""Отфильтровано сообщение от пользователя @{username}:
            
<code>{message}</code>"""


def join_message(first_name: str) -> str:
    return f"""Добро пожаловать в нашу группу, {first_name}!

Давай знакомиться. 

Расскажи немного о себе, своих увлечениях и о своём пути в программировании."""


def left_message(first_name: str) -> str:
    return f"""С прискорбием сообщаю, что {first_name} решил(а) покинуть наш уютный чатик.
    
(предатель(ница))"""

def captcha_message(firs_name: str) -> str:
    return f"Сначла проверим тебя на человечность {firs_name} - у тебя 3 попытки ответить))"

def captcha_message_succsess(first_name: str) -> str:
    return f"Поздравляю {first_name}, ты ответил верно можешь остаться в нашемм уютном чатике!"

def capcha_message_failure(first_name: str) -> str:
    return f"Не получилось,{first_name},  попробуй еще раз"
