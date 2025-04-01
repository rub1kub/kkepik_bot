# commands/find.py
from aiogram import types
from schedules import group_schedule, teacher_schedule
import global_schedules
import os
import pandas as pd
import re

def find_schedule_file(date: str, schedule_type: str) -> str | None:
    """
    Ищет файл расписания по дате и типу (группы/преподаватели)
    """
    data_dir = "data"
    date_pattern = date.replace(".", "_")
    
    for filename in os.listdir(data_dir):
        if filename.startswith("~$") or filename == ".DS_Store":
            continue
            
        if schedule_type == "groups" and "ГРУППЫ" in filename:
            if date in filename or date_pattern in filename:
                return os.path.join(data_dir, filename)
        elif schedule_type == "teachers" and "ПРЕПОДАВАТЕЛИ" in filename:
            if date in filename or date_pattern in filename:
                return os.path.join(data_dir, filename)
    
    return None

def is_teacher_name(name: str) -> bool:
    """
    Проверяет, является ли строка ФИО преподавателя
    """
    # Паттерн для ФИО: Фамилия И.И. или Фамилия И И
    pattern = r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.[А-ЯЁ]\.$'
    print(f"Проверяем ФИО: '{name}'")  # Отладочная информация
    return bool(re.match(pattern, name))

def is_group_name(name: str) -> bool:
    """
    Проверяет, является ли строка номером группы
    """
    # Паттерн для номера группы: 103-Д9-1ИНС
    pattern = r'^\d{3}-[А-Я]\d{1,2}-\d[А-Я]{2,}$'
    name = name.upper()  # Приводим к верхнему регистру перед проверкой
    print(f"Проверяем группу: '{name}'")  # Отладочная информация
    return bool(re.match(pattern, name))

async def cmd_find(message: types.Message):
    """
    Обработчик команды /find для поиска расписания по номеру группы или фамилии преподавателя
    с опциональной датой.
    """
    # Разбираем команду на части
    parts = message.text.split()
    
    # Отладочная информация
    print(f"Получена команда: {message.text}")
    print(f"Разобранные части: {parts}")
    
    if len(parts) < 2:
        await message.answer("⚠️ Использование команды:\n- Для групп: /find 103-Д9-1ИНС 17.03.2025\n- Для преподавателей: /find Ермолов И.А. 17.03.2025")
        return

    # Проверяем, является ли первый аргумент номером группы
    first_arg = parts[1].strip()
    if is_group_name(first_arg):
        search_name = first_arg
        search_date = parts[2] if len(parts) > 2 else None
    else:
        # Если не группа - считаем что это ФИО
        if len(parts) < 4:  # /find Фамилия И.О. Дата
            await message.answer("⚠️ Для поиска по преподавателю используйте формат:\n/find Фамилия И.О. Дата")
            return
        
        search_name = f"{parts[1]} {parts[2]}"  # Фамилия И.О.
        search_date = parts[3]  # Дата

    # Отладочная информация
    print(f"Поисковое имя: '{search_name}'")
    print(f"Дата: '{search_date}'")

    # Если дата не указана, используем последнее загруженное расписание
    if not search_date:
        if global_schedules.last_groups_df is not None:
            search_date = global_schedules.last_groups_date
        elif global_schedules.last_teachers_df is not None:
            search_date = global_schedules.last_teachers_date
        else:
            await message.answer("⚠️ Нет загруженных расписаний.")
            return

    # Определяем тип расписания (группы или преподаватели)
    if is_group_name(search_name):
        schedule_type = "groups"
        search_name = search_name.upper()
    else:
        schedule_type = "teachers"
        # Форматируем ФИО, если нужно
        if '.' not in search_name:
            parts = search_name.split()
            if len(parts) == 2:
                search_name = f"{parts[0]} {parts[1]}"

    # Отладочная информация
    print(f"Тип расписания: {schedule_type}")
    print(f"Обработанное имя: '{search_name}'")

    # Ищем файл расписания
    schedule_file = find_schedule_file(search_date, schedule_type)
    if not schedule_file:
        await message.answer(f"⚠️ Расписание на {search_date} не найдено.")
        return

    try:
        # Читаем Excel файл
        df = pd.read_excel(schedule_file, sheet_name=search_date, header=None)
        if 0 in df.columns:
            df[0] = df[0].ffill()

        # Ищем расписание
        if schedule_type == "groups":
            lines = group_schedule.get_schedule_for_group(df, search_name)
            if lines:
                msg_text = f"📅 Расписание группы {search_name} на {search_date}:\n\n" + "\n".join(lines)
                await message.answer(msg_text, parse_mode="HTML")
            else:
                await message.answer(f"❌ Не найдено расписание для группы {search_name} на {search_date}.")
        else:
            lines = teacher_schedule.get_schedule_for_teacher(df, search_name)
            if lines:
                msg_text = f"📅 Расписание преподавателя {search_name} на {search_date}:\n\n" + "\n".join(lines)
                await message.answer(msg_text, parse_mode="HTML")
            else:
                await message.answer(f"❌ Не найдено расписание для преподавателя {search_name} на {search_date}.")

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при чтении расписания: {str(e)}")
