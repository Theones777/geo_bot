from aiogram import Dispatcher, types
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext

from utils.log import logging
from utils.states import MarkUps
from utils.data import get_synthesis_audio, insert_synthesis_audio_solution
from utils.variables import SUM_PROFILES, VERIFICATION_SOLUTIONS, AVAIL_TARGET_NAMES


async def project_chosen(message: types.Message, state: FSMContext):
    logging(message)
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    if message.text not in AVAIL_TARGET_NAMES:
        await message.answer("Пожалуйста, выберите проект, используя клавиатуру ниже.")
        return

    await message.answer("Ожидание аудио...", reply_markup=types.ReplyKeyboardRemove())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for solution in VERIFICATION_SOLUTIONS:
        keyboard.add(solution)

    audio_path, text, wav_name = get_synthesis_audio(message, marker_id)
    await state.update_data(wav_name=wav_name)
    await state.set_state(MarkUps.waiting_for_solution.state)
    audio = InputFile(audio_path)
    await message.answer_audio(audio, caption=text, reply_markup=keyboard)


async def solution_inserted(message: types.Message, state: FSMContext):
    logging(message)
    if message.text == VERIFICATION_SOLUTIONS[-1]:
        user_data = await state.get_data()
        wav_name = user_data['wav_name']
        await state.finish()
        await message.answer("Разметка завершена", reply_markup=types.ReplyKeyboardRemove())
        insert_synthesis_audio_solution(message.text, wav_name)
    else:
        await state.update_data(solution=message.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button in ['Подтвердить', 'Изменить решение']:
            keyboard.add(button)
        await state.set_state(MarkUps.waiting_for_confirm.state)
        await message.answer("Подтвердите выбор", reply_markup=keyboard)


async def confirm_inserted(message: types.Message, state: FSMContext):
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    user_data = await state.get_data()
    wav_name = user_data['wav_name']
    solution1 = user_data['solution']

    if message.text == 'Подтвердить':
        solution = VERIFICATION_SOLUTIONS[0] if solution1 == VERIFICATION_SOLUTIONS[0] else VERIFICATION_SOLUTIONS[1]
    else:
        solution = VERIFICATION_SOLUTIONS[1] if solution1 == VERIFICATION_SOLUTIONS[0] else VERIFICATION_SOLUTIONS[0]

    insert_synthesis_audio_solution(solution, wav_name)

    await message.answer("Ожидание аудио...", reply_markup=types.ReplyKeyboardRemove())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for solution in VERIFICATION_SOLUTIONS:
        keyboard.add(solution)
    audio_path, text, wav_name = get_synthesis_audio(message, marker_id)
    await state.update_data(wav_name=wav_name)
    await state.set_state(MarkUps.waiting_for_solution.state)
    audio = InputFile(audio_path)
    await message.answer_audio(audio, caption=text, reply_markup=keyboard)


def register_handlers_markups(dp: Dispatcher):
    dp.register_message_handler(project_chosen, state=MarkUps.waiting_for_project_name)
    dp.register_message_handler(solution_inserted, state=MarkUps.waiting_for_solution)
    dp.register_message_handler(confirm_inserted, state=MarkUps.waiting_for_confirm)
