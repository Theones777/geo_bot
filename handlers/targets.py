from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from utils.states import *
from utils.variables import AVAIL_TARGET_NAMES, SUM_PROFILES


async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    if str(message.from_user.id) not in SUM_PROFILES.keys():
        await message.answer("У вас нет доступа к этому боту", reply_markup=types.ReplyKeyboardRemove())
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in AVAIL_TARGET_NAMES:
            keyboard.add(name)
        await state.set_state(MarkUps.waiting_for_project_name.state)
        await message.answer("Выберите задачу", reply_markup=keyboard)


def register_handlers_target(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands="start", state="*")
