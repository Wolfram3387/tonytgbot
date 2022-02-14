from aiogram.dispatcher.filters.state import StatesGroup, State


class AnswerTaker(StatesGroup):
    Q1 = State()
    Q2 = State()
