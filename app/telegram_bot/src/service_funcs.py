import aiohttp
from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_settings import ml_api_link



async def get_list_of_nearest_notes(note_id: int, k: int):
    async with aiohttp.ClientSession() as session:
        send_json = {'note_id': note_id, 'k': k}
        response = await session.get(ml_api_link + '/' + 'get_k_nearest_notes', json=send_json)
        result_json = await response.json()
        resp_status = response.status
    await session.close()

    if resp_status == 200:
        note_id_list = result_json['numbers']
        return note_id_list, resp_status
    else:
        return None, resp_status

async def get_server_status():
    async with aiohttp.ClientSession() as session:
        response = await session.get(ml_api_link + '/' + 'get_server_status')
        result_json = await response.json()
        resp_status = response.status
    await session.close()

    return result_json

async def get_segment_of_nearest_notes(note_id: int, k: int, seg_num: int = 0):
    async with aiohttp.ClientSession() as session:
        send_json = {'note_id': note_id, 'k': k, 'seg_num': seg_num}
        response = await session.get(ml_api_link + '/' + 'get_segment_notes', json=send_json)
        result_json = await response.json()
        resp_status = response.status
    
    if resp_status == 200:
        note_id_list = result_json['numbers']
        return note_id_list, resp_status
    else:
        return None, resp_status

async def get_note_by_id(note_id):
    async with aiohttp.ClientSession() as session:
        send_json = {'note_id': int(note_id)}
        response = await session.get(ml_api_link + '/' + 'get_note_by_id', json=send_json)
        result_json = await response.json()
        resp_status = response.status
    await session.close()

    if resp_status == 200:
        note_text = result_json['note_text']
        note_name = result_json['note_name']
        note_date = result_json['date_create']
        return note_name, note_text, note_date, resp_status
    else:
        return None, None, None, resp_status


async def create_link(first_id: int, second_id: int):
    async with aiohttp.ClientSession() as session:
        send_json = {'first_id': first_id, 'second_id': second_id}
        response = await session.post(ml_api_link + '/' + 'create_link', json=send_json)
        result_json = await response.json()
        resp_status = response.status
    await session.close()

    return resp_status


async def process_error(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Возникла ошибка")

async def send_delete_db_request():
    async with aiohttp.ClientSession() as session:
        response = await session.get(ml_api_link + '/' + 'erase_db')
        resp_status = response.status
    await session.close()

    return resp_status


async def get_notes_list(page: int, notes_per_page: int):
    async with aiohttp.ClientSession() as session:
        send_json = {
            'page_num': page,
            'notes_per_page': notes_per_page
            }
        response = await session.get(ml_api_link + '/' + 'get_notes_list', json=send_json)
        resp_status = response.status
        resp_json = await response.json()
    await session.close()


    if resp_status == 200:
        return resp_json['note_id'], resp_json['note_name'], resp_json['note_text'], resp_json['note_date'], resp_json['pages_count']
    else:
        return [], [], [], [], 0

async def answer_with_notes_list(message, note_id_l, note_name_l, note_text_l, note_date_l):
    if note_id_l.__len__() == 0:
        await message.answer('Заметок нет')
    for i in range(len(note_id_l)):
        await message.answer('Note id:\n{}\n\n'.format(note_id_l[i]) +\
                             'Имя заметки:\n{}\n\n'.format(note_name_l[i]) +\
                             'Дата добавления заметки:\n{}\n\n'.format(note_date_l[i]) +\
                             'Текст добавления заметки:\n{}\n\n'.format(note_text_l[i]))