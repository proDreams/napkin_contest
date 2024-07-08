from asyncio import sleep
from datetime import timedelta, datetime
from random import choice

from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, Message, FSInputFile
from apscheduler.triggers.date import DateTrigger

from botlogic.settings import bot, secrets, scheduler
from botlogic.utils.captcha_utils import ban_user, generate_image, remove_captcha
from botlogic.utils.commands import set_commands
from botlogic import views
from botlogic.utils.statesform import CheckJoin


async def start_bot() -> None:
    await set_commands(bot=bot)
    await bot.send_message(chat_id=secrets.admin_id, text=views.start_bot_msg())


async def stop_bot() -> None:
    await bot.send_message(chat_id=secrets.admin_id, text=views.stop_bot_msg())


async def on_user_join(event: ChatMemberUpdated, state: FSMContext) -> None:
    if event.chat.id == secrets.group_id:
        ban_job = scheduler.add_job(
            func=ban_user,
            trigger=DateTrigger(run_date=datetime.now() + timedelta(minutes=1)),
            kwargs={"message": event, "state": state},
        )
        await sleep(delay=5)
        first_name = event.new_chat_member.user.first_name
        numbers = range(1, 10)
        expression = f"{choice(numbers)} + {choice(numbers)}"
        generate_image(expression=expression, user_id=event.from_user.id)
        image = FSInputFile(path=f"files/{event.from_user.id}.png")
        await event.answer_photo(
            photo=image,
            caption=views.pre_join_message(
                first_name=first_name,
            ),
            show_caption_above_media=True,
        )
        await state.set_data(
            data={"expression": expression, "tries": 0, "ban_job": ban_job.id}
        )
        await state.set_state(state=CheckJoin.WAIT_ANSWER)


async def wait_join_answer(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    tries = data.get("tries")

    if tries == 3:
        await message.delete()
        await ban_user(message=message)
        return

    if message.text and message.text.isdigit():
        if int(message.text) == eval(data.get("expression")):
            await message.answer(
                text=views.join_message(first_name=message.from_user.first_name)
            )
            remove_captcha(user_id=message.from_user.id)
            scheduler.remove_job(job_id=data.get("ban_job"))
            await state.clear()
            return

    await message.delete()
    await message.answer(text=views.wrong_answer_join_message(tries=tries + 1))
    await state.update_data(tries=tries + 1)
    await state.set_state(state=CheckJoin.WAIT_ANSWER)


async def on_user_left(event: ChatMemberUpdated) -> None:
    if event.chat.id == secrets.group_id:
        await sleep(delay=5)
        await event.answer(
            text=views.left_message(first_name=event.old_chat_member.user.first_name)
        )
