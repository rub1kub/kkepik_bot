# teacher.py

import pandas as pd
import numpy as np
import re

def unify_known_phrases(text: str) -> str:
    """
    Не даём 'РАЗГОВОР О ВАЖНОМ' дробиться на три слова.
    """
    if not isinstance(text, str):
        return ""
    words = text.split()
    new_words = []
    i = 0
    while i < len(words):
        if i+2 < len(words):
            triple = [words[i].upper(), words[i+1].upper(), words[i+2].upper()]
            if triple == ["РАЗГОВОР", "О", "ВАЖНОМ"]:
                new_words.append("РАЗГОВОР О ВАЖНОМ")
                i += 3
                continue
        new_words.append(words[i])
        i += 1
    return " ".join(new_words)

def normalize_audience(val: str) -> str:
    """
    Если val выглядит как число (даже с .0), пробуем привести к int и вернуть строку.
    """
    val = val.strip()
    try:
        f = float(val)
        i = int(f)
        if float(i) == f:
            return str(i)
    except:
        pass
    return val

def is_audience_token(token: str) -> bool:
    """
    Считаем 'token' аудиторией, если есть число, или 'ТИР','ВЦ','ИЦ' и т.д.
    """
    token = token.strip()
    if not token:
        return False
    token_norm = normalize_audience(token)
    if re.match(r'^\d+$', token_norm):
        return True
    pattern = r'(?i)(тир|вц|иц|\d+)'
    return bool(re.search(pattern, token_norm))

def is_likely_teacher_name(text: str) -> bool:
    """
    Проверяем формат 'Иванов И.И.' (или без последней точки).
    """
    text = text.strip()
    if not text:
        return False
    pattern = r'^[А-ЯЁA-Z][а-яёa-z-]+ [А-ЯЁA-Z]\.[А-ЯЁA-Z]\.?$'
    return bool(re.match(pattern, text))

def parse_two_columns(df, row_idx: int, col_idx: int) -> tuple[str, str]:
    """
    Считываем (row_idx, col_idx) и (row_idx, col_idx+1).
    Если val2 — аудитория, возвращаем (val1, val2). Иначе склеиваем.
    """
    ncols = df.shape[1]

    if row_idx < 0 or row_idx >= df.shape[0] or (col_idx + 1) >= ncols:
        return ("", "")

    val1 = df.iat[row_idx, col_idx]
    val2 = df.iat[row_idx, col_idx+1]

    if pd.isna(val1):
        val1 = ""
    if pd.isna(val2):
        val2 = ""

    val1 = unify_known_phrases(str(val1).strip())
    val2 = unify_known_phrases(str(val2).strip())

    if is_audience_token(val2):
        aud = normalize_audience(val2)
        return (val1, aud)
    else:
        combined = (val1 + " " + val2).strip()
        return (combined, "")

def parse_schedule_for_teacher(df, row_t: int, col_t: int, teacher_name: str) -> list[str]:
    schedule_lines = []
    i = row_t + 1
    end_row = min(row_t + 50, df.shape[0])  # ограничение на 50 строк вниз

    while i < end_row:
        pair_val = df.iat[i, 0]
        if pd.isna(pair_val):
            pair_val = ""
        pair_val = str(pair_val).strip()

        # Дисциплина col_t
        disc1, aud1 = parse_two_columns(df, i, col_t)

        # Проверяем, нет ли другого преподавателя на (i+1, col_t)
        teacher_extra = ""
        if i + 1 < end_row:
            raw_val_next = df.iat[i+1, col_t]
            if isinstance(raw_val_next, str):
                teacher_extra = raw_val_next.strip()

            if teacher_extra and is_likely_teacher_name(teacher_extra):
                if teacher_extra != teacher_name:
                    break

        # Подгруппа2 (col_t+2)
        disc2, aud2 = "", ""
        if (col_t + 2) < df.shape[1]:
            disc2, aud2 = parse_two_columns(df, i, col_t+2)

        # Проверка: disc1 не должно быть другим ФИО
        if disc1.strip() and is_likely_teacher_name(disc1.strip()):
            if disc1.strip() != teacher_name:
                break

        # Аналогично disc2
        if disc2.strip() and is_likely_teacher_name(disc2.strip()):
            if disc2.strip() != teacher_name:
                break

        # Формируем запись
        if disc1.strip():
            line1 = f"▪️{pair_val} пара – {disc1.strip()} – {teacher_name}"
            if aud1.strip():
                line1 += f" – {aud1}"
            # Если teacher_extra есть и не похоже на ФИО
            if teacher_extra and not is_likely_teacher_name(teacher_extra):
                line1 += f" – {teacher_extra}"
            schedule_lines.append(line1)

        if disc2.strip():
            line2 = f"▪️{pair_val} пара – {disc2.strip()} – {teacher_name}"
            if aud2.strip():
                line2 += f" – {aud2}"
            schedule_lines.append(line2)

        i += 2

    return schedule_lines

def get_schedule_for_teacher(df, teacher_name: str) -> list[str] | None:
    coords = np.where(df.values == teacher_name)
    if len(coords[0]) == 0:
        return None

    row_t = coords[0][-1]
    col_t = coords[1][-1]
    print(teacher_name)
    lines = parse_schedule_for_teacher(df, row_t, col_t, teacher_name)
    return lines