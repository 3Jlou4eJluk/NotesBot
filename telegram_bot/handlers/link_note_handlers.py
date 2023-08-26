import aiohttp

from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from bot_settings import ml_api_link

from service_funcs import get_list_of_nearest_notes
from service_funcs import get_note_by_id
from service_funcs import create_link
from service_funcs import process_error


class LinkNote(StatesGroup):
    choose_note = State()
    accept_linkage = State()
    focus_on_note = State()


link_note_router = Router()

@link_note_router.message(F.text.regexp(r'Связать заметку'), State(None))
async def link_note_command(message: Message, state: FSMContext):
    await message.reply('А теперь введите имя заметки, которую хотите связать')
    await state.set_state(LinkNote.choose_note)

@link_note_router.message(F.text, LinkNote.choose_note)
async def choose_note_for_link(message: types.Message, state: FSMContext):
    send_json = {'request_text': message.text}

    res_status1 = None
    res_json1 = None
    async with aiohttp.ClientSession() as session:
        response = await session.get(ml_api_link + '/' + 'search_note_by_name', json=send_json)
        res_json1 = await response.json()
        res_status1 = response.status
    await session.close()

    if res_status1 != 200:
        await message.answer('Ошибка поиска')
        await state.clear()
    else:
        send_json = {'note_id': res_json1['note_id']}
        res_json2 = None
        res_status2 = None
        async with aiohttp.ClientSession() as session:
            response = await session.get(ml_api_link + '/' + 'get_note_by_id', json=send_json)
            res_json2 = await response.json()
            res_status2 = response.status
        await session.close()
        
        if res_status2 != 200:
            await message.answer('Ошибка поиска')
            await state.clear()
        else:
            # Предлагаем заметку для линковки
            note_name = res_json2['note_name']
            note_text = res_json2['note_text']
            await message.answer('Заметка: \n' + note_name + '\n\n' + 'Текст: \n\n' + note_text)

            # Предложение для линковки
            await state.set_state(LinkNote.accept_linkage)
            await state.update_data(note_id=res_json1['note_id'])
            yes_but = types.InlineKeyboardButton(text='Да', callback_data='accept_linkage_button')
            no_but = types.InlineKeyboardButton(text='Нет', callback_data='decline_linkage_button')
            keyb = types.InlineKeyboardMarkup(inline_keyboard=[[yes_but, no_but]])
            await message.answer('Подтверди корректность заметки для линковки', reply_markup=keyb)


@link_note_router.callback_query(lambda c: c.data == 'accept_linkage_button', LinkNote.accept_linkage)
async def accept_linkage_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(LinkNote.focus_on_note)
    
    # Генерация списка предлагаемых для установления связи заметок (в порядке убывания близости)
    state_data_json = await state.get_data()
    note_id = state_data_json['note_id']
    list_of_nearest_notes, resp_status = await get_list_of_nearest_notes(note_id, 5)
    button_list = []

    if resp_status != 200:
        await process_error(callback.message, state)
        return None
    
    if list_of_nearest_notes.__len__() > 0:
        for note_id in list_of_nearest_notes:
            # print(list_of_nearest_notes)
            note_name, note_text, note_data, resp_status = await get_note_by_id(note_id)
            if resp_status != 200:
                await process_error(callback.message, state)
                return None
            cur_but = types.InlineKeyboardButton(text=note_name[:30], callback_data='set_linkage_with_' + str(note_id))
            button_list.append([cur_but, ])
        keyb = types.InlineKeyboardMarkup(inline_keyboard=button_list)
        await callback.message.answer('Теперь выбери заметки, с которыми будем связывать текущую заметку', reply_markup=keyb)
    else:
        await callback.message.answer('Не найдено ближайших заметок')
        await callback.answer()
        await state.clear()




@link_note_router.callback_query(lambda c: c.data == 'decline_linkage_button', LinkNote.accept_linkage)
async def declinke_linkage_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Отмена линковки')
    await callback.answer()


@link_note_router.callback_query(lambda c: c.data.startswith('set_linkage_with_'), LinkNote.focus_on_note)
async def set_link_handler(callback: types.CallbackQuery, state: FSMContext):
    state_data_json = await state.get_data()
    main_note_id = state_data_json['note_id']
    target_note_id = int(callback.data[len('set_linkage_with_'):])
    await create_link(main_note_id, target_note_id)
    await callback.message.answer('Связь установлена')
    await callback.answer()
    await state.clear()

