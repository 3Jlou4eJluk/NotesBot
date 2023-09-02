from aiogram import types
from aiogram.filters import Filter


class AuthorisationFilter(Filter):
    def __init__(self) -> None:
        self.white_list = [6280571470, 900876379, 981215098,]
    
    async def __call__(self, message: types.Message) -> bool:
        filter_result = message.from_user.id in self.white_list
        # print('Filter result: ', filter_result)
        if not filter_result:
            await message.answer('Нет доступа')
        return filter_result