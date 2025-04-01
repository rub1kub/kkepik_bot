# handlers/inline_mode.py
import re
import sqlite3
from aiogram import types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
import config
from schedules import group_schedule, teacher_schedule
import global_schedules

async def inline_schedule(inline_query: types.InlineQuery):
    """
    Inline‑режим: поиск последнего загруженного расписания по номеру группы или ФИО.
    Пользователь может ввести, например, "@kkepik_bot 103-Д9-1ИНС" или "@kkepik_bot Иванов И.И.".
    Если запрос пуст, используются данные из регистрации.
    В сообщении добавляется информация о группе/преподавателе и дате.
    """
    query_text = inline_query.query.strip()
    user_id = inline_query.from_user.id

    # Если расписание не загружено, отправляем уведомление
    if (global_schedules.last_groups_df is None) and (global_schedules.last_teachers_df is None):
        no_data = InlineQueryResultArticle(
            id="no_data",
            title="⚠️ Нет загруженных расписаний",
            description="Нажмите, чтобы отправить сообщение",
            input_message_content=InputTextMessageContent(message_text="Администратор ещё не загрузил расписание!")
        )
        return await inline_query.answer([no_data], cache_time=1)

    # Если запрос пустой, пытаемся получить данные из БД
    if not query_text:
        try:
            conn = sqlite3.connect(config.DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT role, name_or_group FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
        except Exception:
            row = None
        finally:
            conn.close()
        if row is None:
            return await inline_query.answer(
                results=[],
                switch_pm_text="Введите группу или ФИО (например: 103-Д9-1ИНС)",
                switch_pm_parameter="inline_usage",
                cache_time=1
            )
        else:
            _, typed_name = row
            typed_name = (typed_name or "").strip().upper()
    else:
        typed_name = query_text.upper()

    lines = None
    found_type = None

    # Пытаемся найти расписание для группы
    if global_schedules.last_groups_df is not None:
        g_lines = group_schedule.get_schedule_for_group(global_schedules.last_groups_df, typed_name)
        if g_lines:
            lines = g_lines
            found_type = "group"

    # Если не найдено, ищем расписание для преподавателя
    if not lines and global_schedules.last_teachers_df is not None:
        t_lines = teacher_schedule.get_schedule_for_teacher(global_schedules.last_teachers_df, typed_name)
        if t_lines:
            # Убираем из строк повторное упоминание ФИО
            cleaned_lines = []
            for line in t_lines:
                pattern_fio = rf" – {re.escape(typed_name)}"
                cleaned_line = re.sub(pattern_fio, "", line, count=1)
                cleaned_lines.append(cleaned_line)
            lines = cleaned_lines
            found_type = "teacher"

    if not lines:
        not_found_res = InlineQueryResultArticle(
            id="not_found",
            title="❌ Ничего не найдено",
            description="(Нажмите, чтобы отправить пустое сообщение)",
            input_message_content=InputTextMessageContent(message_text="Ничего не найдено.")
        )
        return await inline_query.answer([not_found_res], cache_time=1)

    if found_type == "group":
        date_str = global_schedules.last_groups_date or "??.??.????"
        header_str = f"📖 Расписание группы {typed_name} на {date_str}"
    else:
        date_str = global_schedules.last_teachers_date or "??.??.????"
        header_str = f"👨‍🏫 Расписание преподавателя {typed_name} на {date_str}"

    schedule_str = "\n".join(lines)
    msg_text = f"<b>{header_str}</b>\n\n{schedule_str}"

    result_article = InlineQueryResultArticle(
        id="found_schedule",
        title=f"✅ Найдено: {typed_name}",
        description="(Нажмите, чтобы отправить расписание)",
        input_message_content=InputTextMessageContent(message_text=msg_text, parse_mode="HTML")
    )

    return await inline_query.answer([result_article], cache_time=1)