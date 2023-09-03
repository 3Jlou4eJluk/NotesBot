from aiogram import types
from aiogram.filters import Filter
from bot_settings import white_list
from bot_settings import admin_list

class AuthorisationFilter(Filter):
    def __init__(self) -> None:
        global white_list
        self.white_list = white_list
    
    async def __call__(self, message: types.Message) -> bool:
        filter_result = message.from_user.id in self.white_list
        # print('Filter result: ', filter_result)
        if not filter_result:
            await message.answer('Нет доступа, необходима авторизация')
        return filter_result

class AdministratorFilter(Filter):
    def __init__(self) -> None:
        global admin_list
        self.admin_list = admin_list

    async def __call__(self, message: types.Message) -> bool:
        filter_result = message.from_user.id in self.admin_list
        if not filter_result:
            await message.answer('Нет доступа, данная команда доступна только администратору.')
        return filter_result