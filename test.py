'''Этот скрипт писался в моменте, когда я не понимал почему у меня не стартует бот.
   Ошибка оказалась в неправильном указании GROUP_ID'''

import requests

TOKEN = 'API_BOT_TOKEN'
GROUP_ID = '-100ваштокен ' # Почему-то только с -100 работает
MESSAGE = "Тестовое сообщение"

# Проверка токена
url = f"https://api.telegram.org/bot{TOKEN}/getMe"
response = requests.get(url)
print("Проверка токена:", response.json())

# Получаем информацию о группе
url = f"https://api.telegram.org/bot{TOKEN}/getChat"
payload = {
    'chat_id': GROUP_ID,
}

response = requests.post(url, data=payload)
print("Информация о чате:", response.json())

# Попробуем отправить сообщение
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    'chat_id': GROUP_ID,
    'text': MESSAGE
}

response = requests.post(url, data=payload)
print("Результат отправки сообщения:", response.json())