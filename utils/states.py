from aiogram.dispatcher.filters.state import StatesGroup, State


class Targets(StatesGroup):
    waiting_for_target = State()


class MarkUps(StatesGroup):
    waiting_for_project_name = State()
    waiting_for_project_info = State()
    waiting_for_solution = State()


class Uploads(StatesGroup):
    waiting_for_project_name = State()
    waiting_for_file = State()
    waiting_for_report = State()
    waiting_for_confirm = State()


class CuratorsChecks(StatesGroup):
    waiting_for_project_name = State()
    waiting_for_sample = State()
    waiting_for_conclusion = State()
    waiting_for_incorrect_info = State()
