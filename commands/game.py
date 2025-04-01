from aiogram import types
from aiogram.filters import Command

async def cmd_game(message: types.Message):
    """Отправляет сообщение с кнопкой для открытия мини-приложения с играми"""
    webapp_url = "https://sosalton.fun/game/index.html"
    
    # Создаем инлайн кнопку для открытия веб-приложения
    webapp_button = types.InlineKeyboardButton(
        text="🎮 Открыть игры",
        web_app=types.WebAppInfo(url=webapp_url)
    )
    
    # Создаем клавиатуру с кнопкой
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[webapp_button]])
    
    # Отправляем сообщение с кнопкой
    await message.answer(
        "🎮 Добро пожаловать в KKEPIK Игры!\n\n"
        "Нажмите на кнопку ниже, чтобы начать играть!",
        reply_markup=keyboard
    ) 