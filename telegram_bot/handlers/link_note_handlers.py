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


class LinkNote(StatesGroup):
    choose_note = State()
    focus_on_note = State()


link_note_router = Router()

@link_note_router.message(F.text, LinkNote.choose_note)
async def choose_note_for_link(message: types.Message, state: FSMContext):
    send_json = {'request_text': message.text}

    async with aiohttp.ClientSession() as session:
        response = await session.get(ml_api_link + '/' + 'search_note_by_name', json=send_json)

    res_json = await response.json()
    if response.status != 200:
        await message.answer('Ошибка поиска')
        await state.clear()
    else:
        send_json = {'note_id': res_json['note_id']}
        async with aiohttp.ClientSession() as session:
            response = await session.get(ml_api_link + '/' + 'get_note_by_id', json=send_json)
        
        if response.status != 200:
            await message.answer('Ошибка поиска')
            await state.clear()
        else:
            # Предлагаем заметку на удаление
            response_json = await response.json()
            note_name = response_json['note_name']
            note_text = response_json['note_text']
            await message.answer('Заметка: \n\n' + note_name)
            await message.answer('Текст: \n\n' + note_text)

            # Предложение для линковки
            # Генерация списка предлагаемых для установления связи заметок (в порядке убывания близости)

