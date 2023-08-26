from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from bot_settings import ml_api_link

from handlers.add_note_handlers import AddNote as AddNoteStates
from handlers.delete_note_handlers import DeleteNote
from handlers.link_note_handlers import LinkNote

from handlers.search_note_handlers import search_note


import aiohttp
import base64

menu_router = Router()

current_page = 0

@menu_router.message(Command('menu'))
async def send_menu(message: types.Message):
    await update_page(message)

@menu_router.message(F.text.regexp(r'Отменить операцию'))
async def cancel_oper_handler(message: types.Message, state: FSMContext):
    await message.reply('Сделано')
    await state.clear()

async def update_page(message: types.Message):
    global current_page

    if current_page == 0:
        add_note_button = types.KeyboardButton(text='Добавить заметку', callback_data='/add_note')
        search_nearest_note_button = types.KeyboardButton(text='Смысловой поиск', callback_data='/search_note')
        remove_note_button = types.KeyboardButton(text='Удалить заметку', callback_data='/delete_note')
        link_note_button = types.KeyboardButton(text='Связать заметку', callback_data='/link_last_note')
        cancel_oper_button = types.KeyboardButton(text='Отменить операцию')
        next_page = types.KeyboardButton(text='След. страница')

        keyb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[add_note_button], 
                                                          [search_nearest_note_button],
                                                          [remove_note_button, link_note_button],
                                                          [cancel_oper_button],
                                                          [next_page]
                                                      ])
        await message.answer('Страница 1', reply_markup=keyb)

    elif current_page == 1:
        
        show_notes_list = types.KeyboardButton(text='Показать список заметок')
        prev_button = types.KeyboardButton(text='Пред. страница')
        next_button = types.KeyboardButton(text='След. страница')
        get_plot_button = types.KeyboardButton(text='Получить изображение', callback_data='/get_plot')
        keyb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[get_plot_button],
                                                                         [prev_button, next_button]])
        await message.answer('Страница 2', reply_markup=keyb)
    elif current_page > 1:
        current_page = 1
        await update_page()
    elif current_page < 0 :
        current_page = 0
        await update_page()


@menu_router.message(F.text.regexp(r'След. страница'))
async def increment_handler(message: types.Message, state: FSMContext):
    global current_page

    current_page += 1

    await update_page(message)

@menu_router.message(F.text.regexp(r'Пред. страница'))
async def decrement_handler(message: types.Message, state: FSMContext):
    global current_page

    current_page -= 1
    if current_page < 0:
        current_page = 0
    
    await update_page(message)


@menu_router.message(F.text.regexp(r'Показать список заметок'))
async def show_notes_list(message: types.Message, state: FSMContext):
    pass