from aiogram.dispatcher.filters.state import StatesGroup, State


class Targets(StatesGroup):
    waiting_for_target = State()


class MarkUps(StatesGroup):
    waiting_for_project_name = State()
    waiting_for_solution = State()
    waiting_for_confirm = State()

