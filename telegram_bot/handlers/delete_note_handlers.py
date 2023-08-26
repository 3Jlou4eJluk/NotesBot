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



class DeleteNote(StatesGroup):
    enter_query_state = State()
    confirm_oper_state = State()


delete_router = Router()

@delete_router.message(F.text.regexp(r'Удалить заметку'), State(None))
async def delete_note_command(message: types.Message, state: FSMContext):
    await state.set_state(DeleteNote.enter_query_state)
    await message.reply('А теперь, введи имя заметки:')

@delete_router.message(F.text, DeleteNote.enter_query_state)
async def enter_note_to_delete(message: types.Message, state: FSMContext):
    send_json = {'request_text': message.text}

    res_json1 = None
    res_status1 = None
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
            res_status2 = response.status
            res_json2 = await response.json()
        await session.close()
        
        if res_status2 != 200:
            await message.answer('Ошибка поиска')
            await state.clear()
        else:
            # Предлагаем заметку на удаление
            note_name = res_json2['note_name']
            note_text = res_json2['note_text']
            await message.answer('Заметка: \n' + note_name + '\n\n' + 'Текст: \n' + note_text)

            yes_button = types.InlineKeyboardButton(text='Да', callback_data='accept_note_delete_button')
            no_button = types.InlineKeyboardButton(text='Нет', callback_data='decline_note_delete_button')
            keyb = types.InlineKeyboardMarkup(inline_keyboard=[[yes_button, no_button]])
            await message.answer("Подтвердите удаление", reply_markup=keyb)
            await state.update_data(note_id=res_json1['note_id'])
            await state.set_state(DeleteNote.confirm_oper_state)


@delete_router.callback_query(lambda c: c.data == 'accept_note_delete_button', DeleteNote.confirm_oper_state)
async def accept_delete(callback: types.CallbackQuery, state: FSMContext):
    note_id_json = await state.get_data()
    note_id = note_id_json['note_id']
    send_json = {'note_id': note_id}

    res_json = None
    res_status = None
    async with aiohttp.ClientSession() as session:
        response = await session.post(ml_api_link + '/' + 'delete_note', json=send_json)
        res_json = await response.json()
        res_status = response.status
    await session.close()
    
    if res_status != 200:
        await callback.message.answer('Возникла ошибка при удалении')
    else:
        await callback.message.answer('Удаление прошло успешно')

    await state.clear()
    await callback.answer()


@delete_router.callback_query(lambda c: c.data == 'decline_note_delete_button', DeleteNote.confirm_oper_state)
async def accept_delete(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Удаление отменено')
    await state.clear()
    await callback.answer()

