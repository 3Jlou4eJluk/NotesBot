from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from bot_settings import ml_api_link

from handlers.add_note_handlers import AddNote as AddNoteStates
from handlers.delete_note_handlers import DeleteNote
from handlers.link_note_handlers import LinkNote

from handlers.search_note_handlers import search_note


import aiohttp
import base64

menu_router = Router()


@menu_router.message(Command('menu'))
async def send_menu(message: types.Message):
    add_note_button = types.InlineKeyboardButton(text='Добавить заметку', callback_data='add_note_callback')
    search_nearest_note_button = types.InlineKeyboardButton(text='Смысловой поиск', callback_data='search_nearest_note_callback')
    remove_note_button = types.InlineKeyboardButton(text='Удалить заметку', callback_data='delete_note_button')
    link_note_button = types.InlineKeyboardButton(text='Связать заметку', callback_data='link_last_note_button')

    keyb = types.InlineKeyboardMarkup(inline_keyboard=[[add_note_button], 
                                                       [search_nearest_note_button],
                                                       [remove_note_button, link_note_button]])

    await message.answer("Вот ваше меню", reply_markup=keyb)


@menu_router.callback_query(lambda c: c.data == 'add_note_callback')
async def add_note_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Хорошо, теперь введите имя заметки')
    await state.set_state(AddNoteStates.enter_name)
    await callback.answer()

@menu_router.callback_query(lambda c: c.data == 'search_nearest_note_callback')
async def search_nearest_note_callback(callback: types.CallbackQuery, state: FSMContext):
    await search_note(callback.message, state)
    callback.answer()



@menu_router.callback_query(lambda c: c.data == 'link_last_note_button')
async def link_last_note_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Окей, теперь необходимо выбрать заметки, с которыми будет установлена связь')


@menu_router.callback_query(lambda c: c.data == 'delete_note_button')
async def delete_note(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Хорошо, теперь нужно введи название заметки:')
    await state.set_state(DeleteNote.enter_query_state)
    await callback.answer()


@menu_router.callback_query(lambda c: c.data == 'link_note_button')
async def link_note(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Выбери заметку для линковки')
    await state.set_state(LinkNote.choose_note)
    await callback.answer()
