import requests

from botlogic.settings import secrets


def get_path(code: str) -> dict | None:
    response = requests.get(url=f"{secrets.api_url}/get-file/?code={code}")
    if response:
        return response.json()
    return


def register_user(
    chat_id: int, first_name: str, last_name: str | None, username: str | None
) -> None:
    requests.post(
        url=f"{secrets.api_url}/create-user/",
        data={
            "chat_id": chat_id,
            "first_name": first_name,
            "last_name": last_name if last_name else "",
            "username": username if username else "",
        },
    )
