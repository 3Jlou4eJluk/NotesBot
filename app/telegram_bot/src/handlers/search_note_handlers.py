from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from bot_settings import ml_api_link
from bot_settings import note_page_count
from aiogram.utils.keyboard import InlineKeyboardMarkup

from service_funcs import process_error
from service_funcs import get_server_status
from service_funcs import get_notes_list
from service_funcs import answer_with_notes_list

from filters.authorization_filter import AuthorisationFilter

import aiohttp
import base64

class SearchNote(StatesGroup):
    choose_method_state = State()
    enter_query = State()

class GetNotesListStates(StatesGroup):
    choose_page_state = State()

search_notes_router = Router()


@search_notes_router.message(F.text.regexp(r'Показать заметки'), State(None), AuthorisationFilter())
async def show_notes(message: types.Message, state: FSMContext):

    await message.answer('Вот список заметок')



@search_notes_router.message(AuthorisationFilter(), State(None), F.text.regexp(r'Смысловой поиск'))
async def search_note(message: types.Message, state: FSMContext):
    but1 = types.InlineKeyboardButton(text='По названию', 
                                      callback_data='choose_method_name')
    but2 = types.InlineKeyboardButton(text='По тексту', 
                                      callback_data='choose_method_text')
    keyb = InlineKeyboardMarkup(inline_keyboard=[[but1, but2]])
    await state.set_state(SearchNote.choose_method_state)
    await message.reply('Выбери способ поиска заметки:', reply_markup=keyb)


@search_notes_router.callback_query(lambda c: c.data == 'choose_method_name', SearchNote.choose_method_state)
async def choose_search_method_name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Окей, теперь нужно ввести запрос:')
    await state.update_data(chosen_method='name')
    await state.set_state(SearchNote.enter_query)
    await callback.answer()

@search_notes_router.callback_query(lambda c: c.data == 'choose_method_text', SearchNote.choose_method_state)
async def choose_search_method_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Окей, теперь нужно ввести запрос:')
    await state.update_data(chosen_method='text')
    await state.set_state(SearchNote.enter_query)
    await callback.answer()





@search_notes_router.message(F.text, SearchNote.enter_query, AuthorisationFilter())
async def process_search_query(message: types.Message, state: FSMContext):
    search_type_dict = await state.get_data()
    send_json = {'request_text': message.text}
    res_json = None
    async with aiohttp.ClientSession() as session:
        if search_type_dict['chosen_method'] == 'name':
            response = await session.get(ml_api_link + '/' + 'search_note_by_name', json=send_json)
        else:
            response = await session.get(ml_api_link + '/' + 'search_note_by_text', json=send_json)
        res_json = await response.json()
    await session.close()
    if response.status != 200:
        await message.answer('Ошибка поиска')
    else:
        await message.answer('Успешно, результат поиска: ' + str(res_json['note_id']))

    await state.clear()



@search_notes_router.message(Command('get_note_by_id'), AuthorisationFilter())
async def get_note_by_id(message: types.Message, command: CommandObject, state: FSMContext):
    if command.args:
        note_id_to_search = None
        try:
            note_id_to_search = int(command.args)
        except:
            await message.answer('Некорректный id заметки')
            

        if note_id_to_search is not None:
            get_json = {'note_id': note_id_to_search}
            response_json = None
            response_status = None
            async with aiohttp.ClientSession() as session:
                response = await session.get(ml_api_link + '/' + 'get_note_by_id', json=get_json)
                response_json = await response.json()
                response_status = response.status
            # print('До получения json')
            
            await session.close()
            
            if response_status != 200:
                await process_error(message, state)
                return None

            
            note_name = response_json['note_name']
            note_text = response_json['note_text']
            note_date = response_json['date_create']

            if note_name is not None:
                await message.answer('Заметка: \n' + note_name + '\n\n' + note_date + '\n\n' 'Текст: \n' + note_text)
            else:
                await message.answer('Данной заметки не существует')

            
        
    else:
        await message.answer("Не указан id заметки")


@search_notes_router.message(Command('get_k_nearest_notes'), AuthorisationFilter())
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
            await session.close()

            note_id_list = response_json['numbers']
            # print(note_id_list)
            answer_str = "Вот ближайшие заметки:\n"
            for i in range(len(note_id_list)):
                answer_str += str(i + 1) + ". " + str(note_id_list[i]) + ('\n' if i < len(note_id_list) else "")
            await message.answer(answer_str)
        else:
            await message.answer('Ошибка распознавания id заметки')

    else:
        await message.answer("Не указан id заметки")

@search_notes_router.message(F.text.regexp(r'Показать все заметки'))
async def get_all_notes_handler(message: types.Message, state: FSMContext):
    note_id_list, note_name_list, note_text_list, note_date_list, note_pages = await get_notes_list(0, note_page_count)

    await message.answer('Привет, всего страниц: ' + str(note_pages) + '\n' + 'Печатаю первую страницу')
    await answer_with_notes_list(message, note_id_list, note_name_list, note_text_list, note_date_list)
    await message.answer('Введите номер страницы для отображения')
    await state.set_state(GetNotesListStates.choose_page_state)

@search_notes_router.message(F.text, GetNotesListStates.choose_page_state)
async def get_all_notes_print_page(message: types.Message):
    try:
        page = int(message.text)
    except:
        message.answer('Некорректный номер страницы')
        return None
    
    note_id_list, note_name_list, note_text_list, note_date_list, note_pages = await get_notes_list(page, note_page_count)
    await message.answer('Страница номер {}/{}'.format(page, note_pages))
    await answer_with_notes_list(message, note_id_list, note_name_list, note_text_list, note_date_list)
