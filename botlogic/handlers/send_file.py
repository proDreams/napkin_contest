from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from botlogic import views
from botlogic.settings import bot, secrets
from botlogic.utils import api_actions
from botlogic.utils.statesform import SendFileSteps


async def send_file_start(message: Message, state: FSMContext) -> None:
    if message.chat.id != secrets.group_id:
        await message.answer(text=views.send_file_start_msg())
        await state.set_state(state=SendFileSteps.get_code_from_user)


async def send_file_get_data(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        await message.answer(text=views.send_file_please_wait())
        data = api_actions.get_path(code=message.text)
        if data:
            file = FSInputFile(path=data.get("file_path"))
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id + 1
            )
            await bot.send_document(
                chat_id=message.chat.id,
                document=file,
                caption=views.file_caption(
                    file_title=data.get("title"),
                    post_url=data.get("post_url"),
                    post_telegram_link=data.get("post_telegram_link"),
                ),
            )
            await state.clear()
        else:
            await message.answer(text=views.send_file_not_found())
    else:
        await message.answer(text=views.send_file_wrong_input())
