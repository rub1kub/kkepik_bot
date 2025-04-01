# handlers/upload_schedule.py
import re
import sqlite3
import pandas as pd
from aiogram import types
from aiogram.types.input_file import FSInputFile
from aiogram.client.bot import Bot
import config
import os
import shutil
from schedules import group_schedule, teacher_schedule
import global_schedules  # Обновляем глобальные переменные через этот модуль

async def handle_document(message: types.Message, bot: Bot):
    """
    Обработка загруженного XLSX-файла расписания (доступ только админам).
    Из названия файла извлекается дата (формат dd.mm.yyyy или dd_mm_yyyy) и определяется тип расписания (для групп или преподавателей).
    Расписание сохраняется в глобальные переменные и рассылается зарегистрированным пользователям.
    """
    import re
    
    user_id = message.from_user.id
    if user_id not in config.ADMINS:
        await message.reply("🚫 У Вас нет прав для загрузки.")
        return

    doc: types.Document = message.document
    file_name = doc.file_name or "file.xlsx"
    if not file_name.endswith(".xlsx"):
        await message.reply("⚠️ Требуется файл .xlsx.")
        return

    file_id = doc.file_id
    try:
        file_info = await bot.get_file(file_id)
        file_path = f"/tmp/{file_name}"
        await bot.download_file(file_info.file_path, file_path)
        os.makedirs("data", exist_ok=True)
        data_file_path = os.path.join("data", file_name)
        shutil.copy(file_path, data_file_path)
    except Exception as e:
        await message.reply(f"Ошибка загрузки: {e}")
        return

    # Извлекаем дату из названия файла
    mm = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4})", file_name)
    if not mm:
        mm = re.search(r"(\d{1,2}_\d{1,2}_\d{4})", file_name)
    if mm:
        schedule_date = mm.group(1).replace("_", ".")
    else:
        await message.reply("❓ Не удалось извлечь дату (dd.mm.yyyy или dd_mm_yyyy) из названия файла.")
        return

    # Определяем тип расписания
    schedule_type = None
    if "ГРУППЫ" in file_name.upper():
        schedule_type = "groups"
    elif "ПРЕПОДАВАТЕЛИ" in file_name.upper():
        schedule_type = "teachers"
    if not schedule_type:
        await message.reply("❓ Не удалось определить, расписание для групп или преподавателей.")
        return

    await message.reply("⚙️ Принято. Обработка...")

    try:
        df = pd.read_excel(file_path, sheet_name=schedule_date, header=None)
    except Exception as e:
        await message.reply(f"Не удалось открыть лист '{schedule_date}' в файле.\nОшибка: {e}")
        return

    if 0 in df.columns:
        df[0] = df[0].ffill()

    # Проверяем, было ли уже расписание на эту дату
    schedule_changed = False
    if schedule_type == "groups":
        if global_schedules.last_groups_date == schedule_date:
            schedule_changed = True
        global_schedules.last_groups_df = df
        global_schedules.last_groups_date = schedule_date
    else:
        if global_schedules.last_teachers_date == schedule_date:
            schedule_changed = True
        global_schedules.last_teachers_df = df
        global_schedules.last_teachers_date = schedule_date

    # Рассылка расписания зарегистрированным пользователям
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, role, name_or_group FROM users")
    rows = cur.fetchall()
    conn.close()

    success_count = 0
    for (uid, role, namegrp) in rows:
        if schedule_type == "groups" and role == "Я студент":
            lines = group_schedule.get_schedule_for_group(df, namegrp.upper())
            if not lines:
                msg_error = f"🔔 Пришло расписание!\n\nНо бот не нашёл группу '{namegrp}' в таблице."
                if schedule_changed:
                    msg_error = "‼️ РАСПИСАНИЕ ИЗМЕНИЛОСЬ\n\n" + msg_error
                try:
                    await bot.send_message(uid, msg_error)
                    success_count += 1
                except Exception:
                    pass
            else:
                txt = "\n".join(lines)
                msg_text = f"📅 Расписание на <b>{schedule_date}</b>\n\nГруппа <b>{namegrp}</b>:\n\n{txt}"
                if schedule_changed:
                    msg_text = "‼️ РАСПИСАНИЕ ИЗМЕНИЛОСЬ\n\n" + msg_text
                try:
                    await bot.send_message(uid, text=msg_text, parse_mode="HTML")
                    success_count += 1
                except Exception:
                    pass
        elif schedule_type == "teachers" and role == "Я преподаватель":
            lines_raw = teacher_schedule.get_schedule_for_teacher(df, namegrp)
            if not lines_raw:
                msg_error = f"🔔 Пришло расписание!\n\nНо бот не нашёл ФИО '{namegrp}' в таблице."
                if schedule_changed:
                    msg_error = "‼️ РАСПИСАНИЕ ИЗМЕНИЛОСЬ\n\n" + msg_error
                try:
                    await bot.send_message(uid, msg_error)
                    success_count += 1
                except Exception:
                    pass
            else:
                import re
                cleaned_lines = []
                for line in lines_raw:
                    pattern_fio = rf" – {re.escape(namegrp.upper())}"
                    cleaned_line = re.sub(pattern_fio, "", line, count=1)
                    cleaned_lines.append(cleaned_line)
                txt = "\n".join(cleaned_lines)
                msg_text = f"📅 Расписание на <b>{schedule_date}</b>\n\n{txt}"
                if schedule_changed:
                    msg_text = "‼️ РАСПИСАНИЕ ИЗМЕНИЛОСЬ\n\n" + msg_text
                try:
                    await bot.send_message(uid, text=msg_text, parse_mode="HTML")
                    success_count += 1
                except Exception:
                    pass

    # Формируем сообщение о результатах
    msg = f"✅ Готово. Рассылка: {success_count} получателей.\nТип: <b>{schedule_type}</b>, дата: <b>{schedule_date}</b>"
    if schedule_changed:
        msg = "‼️ РАСПИСАНИЕ ИЗМЕНИЛОСЬ\n\n" + msg
    
    await message.reply(msg, parse_mode="HTML")