import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from handlers.add_note_handlers import add_note_router
from handlers.base_handlers import base_router
from handlers.search_note_handlers import search_notes_router


bot_token = None
with open('token.txt', 'r') as file:
    bot_token = file.read().strip()

async def main():
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_routers(base_router, add_note_router, search_notes_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

