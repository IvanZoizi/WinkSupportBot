from aiogram.dispatcher.filters.state import State, StatesGroup


class Help(StatesGroup):
    start_help = State()


class Tech(StatesGroup):
    answer = State()
    feedback = State()
    result = State()