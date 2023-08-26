from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from bot_settings import ml_api_link


import aiohttp
import base64

class AddNote(StatesGroup):
    enter_name = State()
    enter_text = State()


async def get_request(url):
    res_json = None
    status = None
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        res_json = await response.json()
        status = response.status
    await session.close()
    return res_json, status


add_note_router = Router()

@add_note_router.message(F.text.regexp(r'Добавить заметку'), State(None))
async def add_note(message :types.Message, state: FSMContext):
    await message.answer('Введи имя заметки')
    await state.set_state(AddNote.enter_name)


@add_note_router.message(AddNote.enter_name, F.text)
async def add_note_enter_name(message: types.Message, state: FSMContext):
    await state.update_data(note_name=message.text)
    await message.answer('Хорошо, теперь давай введём текст твоей заметки')
    await state.set_state(AddNote.enter_text)

@add_note_router.message(AddNote.enter_text, F.text)
async def add_note_enter_text(message: types.Message, state: FSMContext):
    note_name_dict = await state.get_data()
    note_name = note_name_dict['note_name']
    note_text = message.text
    send_json = {'name': note_name, 'text': note_text}

    resp_status = None
    async with aiohttp.ClientSession() as session:
        response = await session.post(ml_api_link + '/' + 'add_note', json=send_json)
        resp_status = response.status
    await session.close()

    if resp_status == 200:
        await message.answer("Заметка добавлена успешно!")
    else:
        await message.answer("Возникла ошибка. Попробуй позже.")

    await state.clear()


@add_note_router.message(Command('get_picture'))
async def get_picture(message :types.Message, command :CommandObject):
    if command.args:
        await message.answer('Функция не реализована')
    else:
        # There is no arguments, so we shouldn't highlight the note
        response_json, resp_status = await get_request(ml_api_link + '/' + 'get_picture')
        if resp_status != 200:
            message.answer('Ошибка получения изображения')
        else:
            plot_encoded_string = response_json['plot']
            plot_extension = response_json['file_extension']
            image_bytes = base64.b64decode(plot_encoded_string.encode('utf-8'))
            image_file = types.InputFile.from_bytes(image_bytes, filename='image' + plot_extension)
            await message.answer_photo(photo=image_file)


