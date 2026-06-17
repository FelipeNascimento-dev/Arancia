"""Helpers para montar payloads enviados à API CRM."""

from decimal import Decimal


def client_payload(cleaned_data):
    return {k: v for k, v in cleaned_data.items() if v not in (None, "")}


def contact_payload(cleaned_data):
    return client_payload(cleaned_data)


def address_payload(cleaned_data):
    return client_payload(cleaned_data)


def _iso_datetime(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _json_safe_value(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def contract_payload(cleaned_data):
    data = client_payload(cleaned_data)
    mapped = {}
    for key, value in data.items():
        api_key = _CONTRACT_API_KEYS.get(key, key)
        mapped[api_key] = _json_safe_value(value)
    return mapped


_CONTRACT_API_KEYS = {
    "client_gai_id": "customer_gai_id",
    "titulo": "title",
    "numero": "number",
    "data_inicio": "start_date",
    "data_fim": "end_date",
    "valor": "value",
    "descricao": "description",
}


_BILLING_API_KEYS = {
    "client_gai_id": "customer_gai_id",
    "referencia": "reference",
    "valor": "value",
    "data_vencimento": "due_date",
    "observacoes": "notes",
}


def billing_payload(cleaned_data):
    data = client_payload(cleaned_data)
    mapped = {}
    for key, value in data.items():
        api_key = _BILLING_API_KEYS.get(key, key)
        mapped[api_key] = _json_safe_value(value)
    return mapped


_RECURRENCE_KEYS = {
    "is_recurring",
    "recurrence_frequency",
    "recurrence_interval",
    "recurrence_end_at",
    "requester_gai_ids",
}


def _iso_datetime(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def build_rrule(frequency, interval=1):
    freq_map = {"daily": "DAILY", "weekly": "WEEKLY", "monthly": "MONTHLY"}
    freq = freq_map.get((frequency or "").lower(), (frequency or "DAILY").upper())
    parts = [f"FREQ={freq}"]
    if interval and int(interval) > 1:
        parts.append(f"INTERVAL={int(interval)}")
    return ";".join(parts)


def parse_rrule(rrule_str):
    """Converte RRULE da API em (frequency, interval) para formulários."""
    if not rrule_str:
        return None, 1
    freq_map = {"DAILY": "daily", "WEEKLY": "weekly", "MONTHLY": "monthly"}
    frequency = None
    interval = 1
    for part in str(rrule_str).split(";"):
        if part.startswith("FREQ="):
            raw = part.split("=", 1)[1]
            frequency = freq_map.get(raw.upper(), raw.lower())
        elif part.startswith("INTERVAL="):
            try:
                interval = int(part.split("=", 1)[1])
            except (TypeError, ValueError):
                interval = 1
    return frequency, interval


def task_payload(cleaned_data):
    data = {
        k: v
        for k, v in cleaned_data.items()
        if v not in (None, "") and k not in _RECURRENCE_KEYS
    }
    requester_ids = cleaned_data.get("requester_gai_ids")
    if requester_ids and data.get("project_id"):
        data["requester_gai_ids"] = list(requester_ids)
    for dt_key in ("scheduled_start_at", "scheduled_end_at", "due_at"):
        if dt_key in data:
            data[dt_key] = _iso_datetime(data[dt_key])
    return data


def recurrence_payload(cleaned_data):
    base = task_payload(cleaned_data)
    freq = cleaned_data.get("recurrence_frequency")
    interval = cleaned_data.get("recurrence_interval") or 1
    if freq:
        base["rrule"] = build_rrule(freq, interval)
    start_at = cleaned_data.get("scheduled_start_at")
    if start_at:
        base["start_at"] = _iso_datetime(start_at)
    end_at = cleaned_data.get("recurrence_end_at")
    if end_at:
        base["end_at"] = _iso_datetime(end_at)
    return base


def project_payload(cleaned_data):
    return client_payload(cleaned_data)


def project_member_payload(cleaned_data):
    return client_payload(cleaned_data)


def comment_payload(cleaned_data):
    data = client_payload(cleaned_data)
    if "body" in data and "content" not in data:
        data["content"] = data.pop("body")
    return data


def subtask_payload(cleaned_data):
    return client_payload(cleaned_data)


def link_payload(cleaned_data):
    return client_payload(cleaned_data)


def assignee_payload(cleaned_data):
    return client_payload(cleaned_data)


def board_payload(cleaned_data):
    return client_payload(cleaned_data)


def board_column_payload(cleaned_data):
    return client_payload(cleaned_data)


def recurrence_edit_payload(cleaned_data):
    return recurrence_payload(cleaned_data)


def board_access_payload(cleaned_data):
    grant_type = cleaned_data.get("grant_type")
    subject_map = {
        "user": "user",
        "designation": "designation",
        "group": "group",
        "team_gai": "customer_gai",
        "customer_gai": "customer_gai",
    }
    id_field = {
        "user": "user_id",
        "designation": "designation_id",
        "group": "group_id",
        "team_gai": "team_gai_id",
        "customer_gai": "customer_gai_id",
    }.get(grant_type)
    payload = {}
    if grant_type and id_field and cleaned_data.get(id_field) not in (None, ""):
        payload["subject_type"] = subject_map[grant_type]
        payload["subject_id"] = cleaned_data[id_field]
    access_level = cleaned_data.get("access_level")
    if access_level:
        payload["access_level"] = access_level
    return payload


def service_type_payload(cleaned_data):
    return client_payload(cleaned_data)


def settings_item_payload(cleaned_data):
    return client_payload(cleaned_data)
