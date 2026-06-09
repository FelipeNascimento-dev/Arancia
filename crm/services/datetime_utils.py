from datetime import datetime
from zoneinfo import ZoneInfo

BR_TZ = ZoneInfo('America/Sao_Paulo')
UTC_TZ = ZoneInfo('UTC')


def parse_api_datetime(value):
    if not value:
        return None
    try:
        value = str(value).strip()
        if value.endswith('Z'):
            value = value.replace('Z', '+00:00')
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC_TZ)
        return dt
    except Exception:
        return None


def format_datetime(value):
    """API -> tela (dd/mm/YYYY HH:MM em horário de Brasília)."""
    dt = parse_api_datetime(value)
    if not dt:
        return value or ''
    return dt.astimezone(BR_TZ).strftime('%d/%m/%Y %H:%M')


def format_datetime_to_input(value):
    """API -> input datetime-local."""
    dt = parse_api_datetime(value)
    if not dt:
        return ''
    return dt.astimezone(BR_TZ).strftime('%Y-%m-%dT%H:%M')


def format_datetime_to_api(value):
    """input datetime-local -> API UTC ISO."""
    if not value:
        return None
    try:
        dt_br = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        dt_br = dt_br.replace(tzinfo=BR_TZ)
        dt_utc = dt_br.astimezone(UTC_TZ)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    except Exception:
        return None
