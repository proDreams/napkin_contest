from aiogram.fsm.state import StatesGroup, State


class SendFileSteps(StatesGroup):
    get_code_from_user = State()


class GetWeatherSteps(StatesGroup):
    BY_CITY = State()


class CapchaSteps(StatesGroup):
    asking = State()
