import os
import shutil

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from utils.check import check_input_files
from utils.log import logging
from utils.states import Uploads
from utils.data import enter_markup_data, insert_incorrect_samples
from utils.variables import AVAIL_AUD_PROJECTS_NAMES, TMP_DOWNLOAD_PATH, SUM_PROFILES


async def project_chosen(message: types.Message, state: FSMContext):
    logging(message)
    if message.text not in AVAIL_AUD_PROJECTS_NAMES:
        await message.answer("Пожалуйста, выберите проект, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_project=message.text)
    await state.set_state(Uploads.waiting_for_file.state)
    # if message.text == AVAIL_AUD_PROJECTS_NAMES[0]:
    #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     keyboard.add('Заполнить неподходящие примеры')
    #     await message.answer("Теперь загрузите zip-архив с файлами"
    #                          "\n\nЕсли файлы уже загружены и необходимо отразить неподходящие файлы - нажмите на "
    #                          "кнопку ниже", reply_markup=keyboard)
    # else:
    await message.answer("Теперь загрузите zip-архив с файлами",
                         reply_markup=types.ReplyKeyboardRemove())


async def incorrect_samples(message: types.Message, state: FSMContext):
    logging(message)
    user_data = await state.get_data()
    project_name = user_data['chosen_project']
    marker_id = SUM_PROFILES[str(message.from_user.id)]

    out_str = insert_incorrect_samples(project_name, marker_id)
    await state.finish()
    await message.answer(out_str, reply_markup=types.ReplyKeyboardRemove())


async def upload_archive(message: types.Message, state: FSMContext):
    await message.answer('Идёт проверка файлов...', reply_markup=types.ReplyKeyboardRemove())
    logging(message)
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    archive_name = message.document.file_name
    download_archive_path = os.path.join(TMP_DOWNLOAD_PATH, marker_id, archive_name)
    os.makedirs(os.path.join(TMP_DOWNLOAD_PATH, marker_id), exist_ok=True)
    await message.document.download(destination_file=download_archive_path)

    check_report, samples_nums = check_input_files(download_archive_path, marker_id)
    await state.update_data({'samples_nums': samples_nums})
    await state.set_state(Uploads.waiting_for_confirm.state)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in ['Подтвердить загрузку', 'Отменить загрузку']:
        keyboard.add(button)
    await message.answer(check_report, reply_markup=keyboard)


async def confirm_upload(message: types.Message, state: FSMContext):
    logging(message)
    user_data = await state.get_data()
    conclusion = message.text
    marker_id = SUM_PROFILES[str(message.from_user.id)]
    if conclusion == 'Подтвердить загрузку':
        await message.answer('Загрузка...', reply_markup=types.ReplyKeyboardRemove())
        project_name = user_data['chosen_project']
        samples_nums = user_data['samples_nums']
        out_str = enter_markup_data(message, marker_id, project_name, samples_nums)
        await message.answer(out_str, reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Загрузка отменена', reply_markup=types.ReplyKeyboardRemove())

    shutil.rmtree(os.path.join(TMP_DOWNLOAD_PATH, marker_id))
    await state.finish()


def register_handlers_uploads(dp: Dispatcher):
    dp.register_message_handler(project_chosen, state=Uploads.waiting_for_project_name)
    dp.register_message_handler(upload_archive, content_types=[types.ContentType.DOCUMENT],
                                state=Uploads.waiting_for_file)
    dp.register_message_handler(incorrect_samples, state=Uploads.waiting_for_file)
    dp.register_message_handler(confirm_upload, state=Uploads.waiting_for_confirm)
