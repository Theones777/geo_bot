from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from utils.curators_check import enter_curator_data
from utils.log import logging
from utils.states import CuratorsChecks
from utils.variables import AVAIL_AUD_PROJECTS_NAMES


async def project_chosen(message: types.Message, state: FSMContext):
    logging(message)
    if message.text not in AVAIL_AUD_PROJECTS_NAMES:
        await message.answer("Пожалуйста, выберите проект, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_project=message.text)
    await state.set_state(CuratorsChecks.waiting_for_sample.state)
    if message.text in AVAIL_AUD_PROJECTS_NAMES:
        await message.answer("Введите номер проверяемой записи", reply_markup=types.ReplyKeyboardRemove())


async def sample_inserted(message: types.Message, state: FSMContext):
    logging(message)
    sample = f"{message.text}.wav"
    await state.update_data(sample=sample)
    await state.set_state(CuratorsChecks.waiting_for_conclusion.state)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in ['Ошибок не найдено', 'Найдены ошибки']:
        keyboard.add(name)
    await message.answer("Выберите результат проверки", reply_markup=keyboard)


async def conclusion_inserted(message: types.Message, state: FSMContext):
    logging(message)
    if message.text == 'Ошибок не найдено':
        await state.finish()
        await message.answer('Проверка завершена', reply_markup=types.ReplyKeyboardRemove())
    else:
        await state.set_state(CuratorsChecks.waiting_for_incorrect_info.state)
        await message.answer('Введите допущенные ошибки', reply_markup=types.ReplyKeyboardRemove())


async def mistakes_inserted(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    sample = user_data['sample']
    project_name = user_data['chosen_project']
    out_str = enter_curator_data(message, sample, project_name)
    await state.finish()
    await message.answer(out_str)


def register_handlers_curators(dp: Dispatcher):
    dp.register_message_handler(project_chosen, state=CuratorsChecks.waiting_for_project_name)
    dp.register_message_handler(sample_inserted, state=CuratorsChecks.waiting_for_sample)
    dp.register_message_handler(conclusion_inserted, state=CuratorsChecks.waiting_for_conclusion)
    dp.register_message_handler(mistakes_inserted, state=CuratorsChecks.waiting_for_incorrect_info)
