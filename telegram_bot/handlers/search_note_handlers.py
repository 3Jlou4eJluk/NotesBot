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


import aiohttp
import base64

class SearchNote(StatesGroup):
    choose_method_state = State()
    enter_query = State()

search_notes_router = Router()


@search_notes_router.message(Command('search_note'))
async def search_note(message: types.Message, state: FSMContext):
    but1 = types.InlineKeyboardButton(text='По названию', 
                                      callback_data='choose_method_name')
    but2 = types.InlineKeyboardButton(text='По тексту', 
                                      callback_data='choose_method_text')
    keyb = InlineKeyboardMarkup(inline_keyboard=[[but1, but2]])
    await state.set_state(SearchNote.choose_method_state)
    await message.reply('Выбери способ поиска заметки:', reply_markup=keyb)


@search_notes_router.callback_query()
async def choose_search_method_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Окей, теперь нужно ввести запрос:')
    if callback.data == 'choose_method_name':
        await state.update_data(chosen_method='name')
    elif callback.data == 'choose_method_text':
        await state.update_data(chosen_method='text')
    await state.set_state(SearchNote.enter_query)





@search_notes_router.message(F.text, SearchNote.enter_query)
async def process_search_query(message: types.Message, state: FSMContext):
    search_type_dict = await state.get_data()
    send_json = {'request_text': message.text}
    async with aiohttp.ClientSession() as session:
        if search_type_dict['chosen_method'] == 'name':
            response = await session.get(ml_api_link + '/' + 'search_note_by_name', json=send_json)
        else:
            response = await session.get(ml_api_link + '/' + 'search_note_by_text', json=send_json)
    res_json = await response.json()
    if response.status != 200:
        await message.answer('Ошибка поиска')
    else:
        await message.answer('Успешно, результат поиска: ' + str(res_json['note_id']))

    await state.clear()



@search_notes_router.message(Command('get_note_by_id'))
async def get_note_by_id(message: types.Message, command: CommandObject, state: FSMContext):
    if command.args:
        note_id_to_search = None
        try:
            note_id_to_search = int(command.args)
        except:
            await message.answer('Некорректный id заметки')
            

        if note_id_to_search is not None:
            get_json = {'note_id': note_id_to_search}
            async with aiohttp.ClientSession() as session:
                response = await session.get(ml_api_link + '/' + 'get_note_by_id', json=get_json)
        
            response_json = await response.json()
            note_name = response_json['note_name']
            note_text = response_json['note_text']

            if (note_name is not None) and (note_text is not None):
                await message.answer('Заметка: \n\n' + note_name)
                await message.answer('Текст: \n\n' + note_text)
            else:
                await message.answer('Данной заметки нет в базе')
        
    else:
        await message.answer("Не указан id заметки")


@search_notes_router.message(Command('get_k_nearest_notes'))
async def get_k_nearest_notes(message: types.Message, command: CommandObject):
    if command.args:
        note_id = None
        try:
            note_id, k = map(int, command.args.split())
        except:
            await message.answer('Некорректные аргументы комманды')

        if note_id is not None:
            get_json = {'note_id': note_id,
                        'k': k}
            async with aiohttp.ClientSession() as session:
                response = await session.get(ml_api_link + '/' + 'get_k_nearest_notes', json=get_json)
            response_json = await response.json()
            note_id_list = response_json['numbers']
            print(note_id_list)
            answer_str = "Вот ближайшие заметки:\n"
            for i in range(len(note_id_list)):
                answer_str += str(i + 1) + ". " + str(note_id_list[i]) + ('\n' if i < len(note_id_list) else "")
            message.answer(answer_str)
        else:
            print('Всё таки None')

    else:
        await message.answer("Не указан id заметки")