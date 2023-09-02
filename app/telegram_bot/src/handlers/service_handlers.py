from aiogram import Router, F
from aiogram import types
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