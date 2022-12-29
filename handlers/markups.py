import os

from aiogram import Dispatcher, types
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext

from utils.log import logging
from utils.states import MarkUps
from utils.data import get_markup_data, get_synthesis_audio, insert_synthesis_audio_solution
from utils.variables import AVAIL_AUD_PROJECTS_NAMES, SUM_PROFILES, VERIFICATION_SOLUTIONS


async def project_chosen(message: types.Message, state: FSMContext):
    logging(message)
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    if message.text not in AVAIL_AUD_PROJECTS_NAMES:
        await message.answer("Пожалуйста, выберите проект, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_project=message.text)
    await state.set_state(MarkUps.waiting_for_project_info.state)
    if message.text == AVAIL_AUD_PROJECTS_NAMES[0]:
        await message.answer("Сколько аудио хотите разметить?", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == AVAIL_AUD_PROJECTS_NAMES[1]:
        await message.answer("Ожидание аудио...", reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for solution in VERIFICATION_SOLUTIONS:
            keyboard.add(solution)

        audio_path, text, wav_name = get_synthesis_audio(message, marker_id, message.text)
        await state.update_data(wav_name=wav_name)
        await state.set_state(MarkUps.waiting_for_solution.state)
        audio = InputFile(audio_path)
        await message.answer_audio(audio, caption=text, reply_markup=keyboard)


async def solution_inserted(message: types.Message, state: FSMContext):
    logging(message)
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    user_data = await state.get_data()
    project_name = user_data['chosen_project']
    wav_name = user_data['wav_name']

    insert_synthesis_audio_solution(message.text, wav_name)
    if message.text == VERIFICATION_SOLUTIONS[-1]:
        await state.finish()
        await message.answer("Разметка завершена", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Ожидание аудио...", reply_markup=types.ReplyKeyboardRemove())
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for solution in VERIFICATION_SOLUTIONS:
            keyboard.add(solution)
        audio_path, text, wav_name = get_synthesis_audio(message, marker_id, project_name)
        await state.update_data(wav_name=wav_name)
        await state.set_state(MarkUps.waiting_for_solution.state)
        audio = InputFile(audio_path)
        await message.answer_audio(audio, caption=text, reply_markup=keyboard)


async def info_inserted(message: types.Message, state: FSMContext):
    logging(message)
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    user_data = await state.get_data()
    project_name = user_data['chosen_project']

    arc_path = get_markup_data(message, int(message.text), marker_id, project_name)
    arc = InputFile(arc_path)
    await message.reply_document(arc)
    os.remove(arc_path)
    await state.finish()


def register_handlers_markups(dp: Dispatcher):
    dp.register_message_handler(project_chosen, state=MarkUps.waiting_for_project_name)
    dp.register_message_handler(info_inserted, state=MarkUps.waiting_for_project_info)
    dp.register_message_handler(solution_inserted, state=MarkUps.waiting_for_solution)
