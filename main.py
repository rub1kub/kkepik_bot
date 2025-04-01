# main.py
import asyncio
import logging
import sqlite3
import os
import re

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineQuery
from aiogram.types.input_file import FSInputFile
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

import config
from commands.find import cmd_find
from commands.start import cmd_start, process_role_callback, process_name
from commands.reset import cmd_reset
from commands.broadcast import cmd_broadcast
from handlers.inline_mode import inline_schedule
from handlers.upload_schedule import handle_document

from global_schedules import (
    last_groups_df, last_groups_date,
    last_teachers_df, last_teachers_date
)

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Удаляем webhook перед запуском бота
    await bot.delete_webhook(drop_pending_updates=True)
    
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем команды /start, /cancel, /reset
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_find, Command(commands=["find"]))
    dp.message.register(cmd_reset, Command(commands=["reset"]))
    dp.message.register(cmd_broadcast, Command(commands=["broadcast"]))

    # Регистрируем callback для выбора роли
    @dp.callback_query(lambda c: c.data in ["role_student", "role_teacher"])
    async def callback_role(callback: types.CallbackQuery, state: FSMContext):
        await callback.answer()  # скрываем анимацию ожидания на кнопке
        await process_role_callback(callback, state)

    # Обработчик ввода номера группы или ФИО
    dp.message.register(
        process_name, 
        cmd_start.__globals__["RegistrationStates"].waiting_name
    )

    # Обработчик загрузки файла расписания
    dp.message.register(handle_document, F.document)

    # Inline‑режим для поиска расписания
    dp.inline_query.register(inline_schedule)

    async def on_startup():
        print("Бот запущен (с inline режимом)")

    async def on_shutdown():
        print("Бот остановлен")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())