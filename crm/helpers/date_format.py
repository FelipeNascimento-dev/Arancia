"""Formatação de datas para exibição no padrão brasileiro (DD/MM/AAAA)."""

from datetime import date, datetime


def format_date_br(value, *, default=""):
    """Converte date, datetime ou ISO (YYYY-MM-DD) para DD/MM/YYYY."""
    if value in (None, ""):
        return default
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    text = str(value).strip()
    if not text or text == "-":
        return default or text

    date_part = text.split("T", 1)[0]
    if len(date_part) >= 10 and date_part[4:5] == "-" and date_part[7:8] == "-":
        year, month, day = date_part[:10].split("-", 2)
        if year.isdigit() and month.isdigit() and day.isdigit():
            return f"{int(day):02d}/{int(month):02d}/{year}"

    return text


def format_datetime_br(value, *, default=""):
    """Converte datetime ou ISO para DD/MM/YYYY HH:MM."""
    if value in (None, ""):
        return default
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")

    text = str(value).strip()
    if not text or text == "-":
        return default or text

    normalized = text.replace("Z", "+00:00")
    if "T" in normalized:
        date_part, time_part = normalized.split("T", 1)
        date_fmt = format_date_br(date_part)
        time_fmt = time_part[:5] if len(time_part) >= 5 else ""
        if date_fmt and time_fmt:
            return f"{date_fmt} {time_fmt}"
        return date_fmt or text

    return format_date_br(text, default=text)


def format_period_br(start, end, *, separator=" — ", default=""):
    """Formata intervalo de datas no padrão brasileiro."""
    start_fmt = format_date_br(start)
    end_fmt = format_date_br(end)
    if start_fmt and end_fmt:
        return f"{start_fmt}{separator}{end_fmt}"
    if start_fmt:
        return start_fmt
    if end_fmt:
        return end_fmt
    return default
