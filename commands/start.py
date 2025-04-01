# commands/start.py
import sqlite3
import config
from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import global_schedules
from schedules import group_schedule, teacher_schedule

# Определяем состояния для регистрации
class RegistrationStates(StatesGroup):
    choosing_role = State()
    waiting_name = State()

# Обработчик команды /start
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Создаем таблицу, если её нет, и пытаемся найти пользователя в базе
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            role TEXT,
            name_or_group TEXT
        )
    """)
    cur.execute("SELECT role, name_or_group FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    # Если пользователь найден, отправляем актуальное расписание
    if row:
        role, typed_name = row
        typed_name = (typed_name or "").strip()
        if role == "Я студент":
            typed_name = typed_name.upper()
            if global_schedules.last_groups_df is not None and global_schedules.last_groups_date:
                lines = group_schedule.get_schedule_for_group(global_schedules.last_groups_df, typed_name)
                if lines:
                    txt = "\n".join(lines)
                    msg_text = (
                        f"📅 Ваше последнее расписание (группа <b>{typed_name}</b>):\n\n"
                        f"<b>{global_schedules.last_groups_date}</b>\n\n{txt}"
                    )
                    await message.answer(msg_text, parse_mode="HTML")
                else:
                    await message.answer(
                        f"Вы зарегистрированы как студент '{typed_name}', но бот не нашёл вашу группу в последнем загруженном расписании.\n\n"
                        "Дождитесь нового расписания или смените данные (/reset)."
                    )
            else:
                await message.answer(
                    "Вы зарегистрированы как студент, но расписание для групп не загружено или отсутствует.\n"
                    "Дождитесь загрузки расписания администратором."
                )
        elif role == "Я преподаватель":
            if global_schedules.last_teachers_df is not None and global_schedules.last_teachers_date:
                lines_raw = teacher_schedule.get_schedule_for_teacher(global_schedules.last_teachers_df, typed_name)
                if lines_raw:
                    import re
                    cleaned_lines = []
                    for line in lines_raw:
                        pattern_fio = rf" – {re.escape(typed_name)}"
                        cleaned_line = re.sub(pattern_fio, "", line, count=1)
                        cleaned_lines.append(cleaned_line)
                    txt = "\n".join(cleaned_lines)
                    msg_text = (
                        f"📅 Ваше последнее расписание (преподаватель <b>{typed_name}</b>):\n\n"
                        f"<b>{global_schedules.last_teachers_date}</b>\n\n{txt}"
                    )
                    await message.answer(msg_text, parse_mode="HTML")
                else:
                    await message.answer(
                        f"Вы зарегистрированы как преподаватель '{typed_name}', но бот не нашёл ваше ФИО в последнем загруженном расписании.\n\n"
                        "Дождитесь нового расписания или смените данные (/reset)."
                    )
            else:
                await message.answer(
                    "Вы зарегистрированы как преподаватель, но расписание для преподавателей не загружено или отсутствует.\n"
                    "Дождитесь загрузки расписания администратором."
                )
        return

    await message.answer("👋")
    # Если пользователь не найден, предлагаем выбрать роль
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Я студент 🎓", callback_data="role_student"),
            InlineKeyboardButton(text="Я преподаватель 👨‍🏫", callback_data="role_teacher")
        ]
    ])
    await message.answer("❔Рассылка какого расписания Вас интересует?\nСтуденческое или Преподавательское?", reply_markup=kb)
    await state.set_state(RegistrationStates.choosing_role)

# Обработка выбора роли через callback
async def process_role_callback(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    if data == "role_student":
        await state.update_data(role="Я студент")
        await callback.message.answer("✏️Введите номер Вашей группы (например: 103-Д9-1ИНС).")
        await state.set_state(RegistrationStates.waiting_name)
    elif data == "role_teacher":
        await state.update_data(role="Я преподаватель")
        await callback.message.answer("✏️Введите Вашу Фамилию И.О. (например: Иванов И.И.).")
        await state.set_state(RegistrationStates.waiting_name)

# Обработка ввода номера группы или ФИО
async def process_name(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите текст (номер группы или ФИО).")
        return
    name_or_group = message.text.strip()
    data = await state.get_data()
    role = data.get("role", "")
    user_id = message.from_user.id
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, role TEXT, name_or_group TEXT)")
    cur.execute("INSERT OR REPLACE INTO users (user_id, role, name_or_group) VALUES (?, ?, ?)", (user_id, role, name_or_group))
    conn.commit()
    conn.close()
    if role == "Я студент":
        schedule_type = "студенческое расписание"
    else:
        schedule_type = "преподавательское расписание"
    await message.answer(f"✅ Регистрация завершена! Теперь Вам будет приходить {schedule_type}.\n\nСброс: /reset")
    await state.clear()