from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from aiogram.filters import CommandObject
from aiogram import types


base_router = Router()


@base_router.message(Command('about'))
async def explain_about(message : types.Message):
    await message.answer("Здравствуй, это бот, который автоматически обрабатывает твои " +
                         "заметки, его возможности предполагают автоматическое оформление в obsidian, " +
                         "доступ к которому можно получить через облако/git или что-то подобное, " +
                         "предложение заметок на объединение с помощью методов машинного обучения "+
                         "однако некотороые функции пока не были имплементированы. В процессе.")
