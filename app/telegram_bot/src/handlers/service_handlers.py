from aiogram import Router, F
from aiogram import types
from aiogram import filters
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from bot_settings import ml_api_link
from aiogram.utils.keyboard import InlineKeyboardMarkup

from filters.authorization_filter import AdministratorFilter
from service_funcs import send_delete_db_request

from bot_settings import white_list

service_router = Router()




@service_router.message(F.animation)
async def return_animation_id(message: types.Message):
    await message.reply("Id этой анимации: " + str(message.animation.file_id))




@service_router.message(Command('set_coolest_avatar'))
async def set_coolest_avatar(message: types.Message):
    photo = types.InputFile(file_name='/home/mishanya/Документы/progs/NotesBot/telegram_bot/resources/animation.mp4')
    await message.bot.set_chat_photo(chat_id=message.chat.id, photo=photo)


@service_router.message(Command('get_my_id'))
async def get_user_id(message: types.Message):
    await message.answer('Your id is ' + str(message.from_user.id))


@service_router.message(Command('erase_db'), AdministratorFilter())
async def erase_db(message: types.Message):
    await message.answer('Erasing db...')
    resp_status = await send_delete_db_request()
    await message.answer('Sent, status: ' + str(resp_status))

@service_router.message(Command('get_white_list'))
async def get_white_list(message: types.Message):
    global white_list
    await message.answer(str(white_list))

@service_router.message(Command('add_to_white_list'))
async def add_to_white_list(message: types.Message, command: filters.CommandObject):
    global white_list
    if command.args is None:
        await message.answer('Не указан id пользователя')
        return None
    try:
        user_id_list = list(map(int, command.args.split()))
    except:
        await message.answer('Некорректные id пользователей')
        return None

    await message.answer("Пользователь добавлен в white list")
    white_list += user_id_list

@service_router.message(Command('delete_users_from_white_list'))
async def delete_from_white_list(message: types.Message, command: filters.CommandObject):
    global white_list
    if command.args is None:
        await message.answer('Ну указан id пользователя')
        return None
    
    try:
        user_id_to_delete = list(map(int, command.args.split()))
        print(user_id_to_delete)
    except:
        await message.answer('Некорректные id пользователей')
        return None
    tmp = white_list.copy()
    white_list = []
    for user_id in tmp:
        if user_id not in user_id_to_delete:
            white_list.append(user_id) 
    await message.answer('Пользователи удалены из white_list: ' + \
                         str(list(set(tmp).intersection(set(user_id_to_delete)))))
