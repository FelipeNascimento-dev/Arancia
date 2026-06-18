"""Helpers para exibir objetos aninhados retornados pela API CRM."""

import re

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def entity_key(entity, *keys, default=""):
    """Retorna o primeiro identificador disponível no dict da API."""
    if not isinstance(entity, dict):
        return default
    for key in keys:
        value = entity.get(key)
        if value not in (None, ""):
            return value
    return default


def with_id_alias(entity, *id_keys):
    """
    Garante chave ``id`` para templates.

    Evita ``{{ x|default:y }}`` no template — o Django resolve o fallback
    mesmo quando não é usado, gerando VariableDoesNotExist.
    """
    if not isinstance(entity, dict):
        return entity
    primary = entity_key(entity, *id_keys)
    if primary in (None, ""):
        return entity
    if entity.get("id") in (None, ""):
        return {**entity, "id": primary}
    return entity


def nested_label(entity, *flat_keys):
    if not entity or not isinstance(entity, dict):
        return ""
    for key in flat_keys:
        value = entity.get(key)
        if value not in (None, ""):
            return value
    return ""


def with_label_aliases(entity, *key_groups):
    """
    Preenche aliases de label ausentes (ex.: nome/name) para evitar
    ``{{ a|default:b }}`` no template.
    """
    if not isinstance(entity, dict):
        return entity
    result = dict(entity)
    for keys in key_groups:
        value = entity_key(entity, *keys)
        if value in (None, ""):
            continue
        for key in keys:
            if result.get(key) in (None, ""):
                result[key] = value
    return result


def enrich_client(client):
    if not isinstance(client, dict):
        return client
    client = with_id_alias(client, "gai_id", "id")
    client = with_label_aliases(client, ("nome", "name"))
    contacts = [
        with_label_aliases(c, ("nome", "name"), ("telefone", "phone"), ("cargo", "role"))
        for c in (client.get("contacts") or [])
        if isinstance(c, dict)
    ]
    addresses = [
        with_label_aliases(
            a,
            ("logradouro", "street"),
            ("cidade", "city"),
            ("uf", "state"),
            ("cep", "zip_code"),
        )
        for a in (client.get("addresses") or [])
        if isinstance(a, dict)
    ]
    if contacts:
        client = {**client, "contacts": contacts}
    if addresses:
        client = {**client, "addresses": addresses}
    return client


def client_to_json(client):
    """Serializa cliente enriquecido para respostas AJAX."""
    client = enrich_client(client or {})
    contacts = []
    for item in client.get("contacts") or []:
        if not isinstance(item, dict):
            continue
        contacts.append({
            "nome": nested_label(item, "nome", "name"),
            "email": item.get("email") or "",
            "telefone": nested_label(item, "telefone", "phone"),
            "cargo": nested_label(item, "cargo", "role"),
        })
    addresses = []
    for item in client.get("addresses") or []:
        if not isinstance(item, dict):
            continue
        addresses.append({
            "logradouro": nested_label(item, "logradouro", "street"),
            "numero": nested_label(item, "numero", "number"),
            "cidade": nested_label(item, "cidade", "city"),
            "uf": nested_label(item, "uf", "state"),
            "cep": nested_label(item, "cep", "zip_code"),
        })
    return {
        "gai_id": entity_key(client, "gai_id", "id"),
        "nome": nested_label(client, "nome", "name"),
        "razao_social": client.get("razao_social") or "",
        "cnpj": client.get("cnpj") or "",
        "email": client.get("email") or "",
        "telefone": client.get("telefone") or "",
        "sales_channel": client.get("sales_channel") or "",
        "cod_iata": client.get("cod_iata") or "",
        "notes": client.get("notes") or "",
        "contacts": contacts,
        "addresses": addresses,
    }


def enrich_board(board):
    if not isinstance(board, dict):
        return board
    board = with_label_aliases(board, ("nome", "name"), ("descricao", "description"))
    return {
        **board,
        "display_name": entity_key(board, "name", "nome", default=str(board.get("id") or "")),
    }


def _status_task_label(status_id, lookups=None):
    if status_id in (None, ""):
        return ""
    if not isinstance(lookups, dict):
        return ""
    for item in lookups.get("status_tasks") or []:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if item_id is not None and str(item_id) == str(status_id):
            return nested_label(item, "name", "nome", "label")
    return ""


def enrich_board_column(column, lookups=None):
    if not isinstance(column, dict):
        return column
    column = with_label_aliases(column, ("nome", "name"))
    kanban_status_id = entity_key(column, "status_task_id", "status_id", "id")
    status_name = nested_label(column, "status_name", "name", "nome")
    if not status_name:
        status_name = _status_task_label(kanban_status_id, lookups)
    code = column.get("code")
    display_status = status_name or (str(code) if code not in (None, "") else "") or "-"
    display_position = (
        column.get("position")
        or column.get("sort_order")
        or column.get("kanban_position")
        or 0
    )
    return {
        **column,
        "display_name": entity_key(column, "name", "nome", "status_name", default="Coluna"),
        "display_status": display_status,
        "display_position": display_position,
        "kanban_status_id": kanban_status_id,
        "status_task_id": kanban_status_id if kanban_status_id not in (None, "") else None,
    }


def enrich_alert(alert):
    if not isinstance(alert, dict):
        return alert
    alert = with_label_aliases(
        alert,
        ("titulo", "title"),
        ("data_vencimento", "due_date"),
    )
    customer = alert.get("customer") or {}
    contract = alert.get("contract") or {}
    contract_id = alert.get("contract_id") or contract.get("id")
    display_title = (
        alert.get("message")
        or entity_key(alert, "title", "titulo")
        or alert.get("alert_type")
        or "Alerta"
    )
    return {
        **alert,
        "display_title": display_title,
        "display_customer": nested_label(customer, "nome", "name")
        or alert.get("customer_name")
        or alert.get("client_name")
        or "",
        "display_contract": nested_label(contract, "titulo", "title", "numero", "number")
        or alert.get("contract_number")
        or "",
        "display_contract_id": contract_id,
        "display_status": alert.get("status") or alert.get("alert_type") or "",
        "display_vencimento": entity_key(alert, "due_date", "data_vencimento", default=""),
    }


def enrich_contract(contract):
    if not isinstance(contract, dict):
        return contract
    contract = with_label_aliases(
        contract,
        ("numero", "number"),
        ("titulo", "title"),
        ("descricao", "description"),
        ("data_inicio", "start_date"),
        ("data_fim", "end_date"),
        ("valor", "value"),
    )
    customer = contract.get("customer") or {}
    service_type = contract.get("service_type") or {}
    return {
        **contract,
        "display_customer": nested_label(customer, "nome", "name")
        or contract.get("client_name")
        or "",
        "display_service_type": nested_label(
            service_type, "description", "name", "nome", "type",
        )
        or contract.get("service_type_name")
        or "",
        "display_numero": entity_key(contract, "numero", "number", default=""),
        "display_titulo": entity_key(contract, "titulo", "title", default=""),
        "display_data_inicio": entity_key(contract, "data_inicio", "start_date", default=""),
        "display_data_fim": entity_key(contract, "data_fim", "end_date", default=""),
        "display_valor": entity_key(contract, "valor", "value", default=""),
        "display_status": contract.get("status") or "",
    }


def contract_to_json(contract):
    """Serializa contrato enriquecido para respostas AJAX."""
    contract = enrich_contract(contract or {})
    customer = contract.get("customer") or {}
    service_type = contract.get("service_type") or {}
    return {
        "id": entity_key(contract, "id"),
        "client_gai_id": contract.get("client_gai_id")
        or contract.get("customer_gai_id")
        or customer.get("gai_id")
        or customer.get("id"),
        "titulo": entity_key(contract, "titulo", "title"),
        "numero": entity_key(contract, "numero", "number"),
        "status": contract.get("status") or "",
        "data_inicio": entity_key(contract, "data_inicio", "start_date"),
        "data_fim": entity_key(contract, "data_fim", "end_date"),
        "valor": entity_key(contract, "valor", "value"),
        "service_type_id": contract.get("service_type_id") or service_type.get("id") or "",
        "descricao": entity_key(contract, "descricao", "description"),
        "display_customer": contract.get("display_customer") or "",
        "display_service_type": contract.get("display_service_type") or "",
    }


def service_type_option_label(service_type):
    if not isinstance(service_type, dict):
        return ""
    return nested_label(service_type, "description", "type", "name", "nome")


def service_type_client_gai_id(service_type):
    if not isinstance(service_type, dict):
        return None
    for key in ("client_id", "customer_gai_id", "client_gai_id"):
        value = service_type.get(key)
        if value not in (None, ""):
            return value
    return None


def service_types_for_config(service_types):
    options = []
    for item in service_types or []:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if item_id is None:
            continue
        options.append({
            "id": item_id,
            "label": service_type_option_label(item) or str(item_id),
            "client_id": service_type_client_gai_id(item),
        })
    return options


def enrich_project(project):
    if not isinstance(project, dict):
        return project
    project = with_label_aliases(
        project,
        ("nome", "name"),
        ("descricao", "description"),
    )
    customer = project.get("customer") or {}
    contract = project.get("contract") or {}
    default_board = project.get("default_board") or {}
    if customer:
        customer = with_label_aliases(customer, ("nome", "name"))
        project = {**project, "customer": customer}
    if contract:
        contract = with_label_aliases(contract, ("titulo", "title"))
        project = {**project, "contract": contract}
    if default_board:
        default_board = with_label_aliases(default_board, ("nome", "name"))
        project = {**project, "default_board": default_board}
    return {
        **project,
        "display_name": entity_key(project, "name", "nome", default=str(project.get("id") or "")),
        "display_customer": nested_label(customer, "nome", "name")
        or project.get("customer_gai_name")
        or "",
    }


def enrich_task_lookups(lookups):
    """Preenche aliases nome/name nos catálogos usados nos filtros de tasks."""
    if not isinstance(lookups, dict):
        return lookups or {}
    result = dict(lookups)
    for key in ("status_tasks", "priorities", "boards", "column_templates", "gais", "users"):
        items = result.get(key)
        if isinstance(items, list):
            result[key] = [
                with_label_aliases(item, ("nome", "name"))
                for item in items
                if isinstance(item, dict)
            ]
    designations = result.get("designations")
    if isinstance(designations, list):
        result["designations"] = [
            with_label_aliases(item, ("label", "username", "nome", "name"))
            for item in designations
            if isinstance(item, dict)
        ]
    projects = result.get("projects")
    if isinstance(projects, list):
        result["projects"] = [
            enrich_project(item) for item in projects if isinstance(item, dict)
        ]
    return result


_RECURRENCE_FREQ_LABELS = {
    "daily": "Diária",
    "weekly": "Semanal",
    "monthly": "Mensal",
}


def _recurrence_frequency_label(freq, interval=1):
    if not freq:
        return ""
    label = _RECURRENCE_FREQ_LABELS.get(str(freq).lower(), str(freq))
    try:
        n = int(interval)
    except (TypeError, ValueError):
        n = 1
    if n > 1:
        return f"{label} (a cada {n})"
    return label


def enrich_recurrence(recurrence):
    if not isinstance(recurrence, dict):
        return recurrence
    from crm_api.payloads import parse_rrule

    freq = recurrence.get("frequency") or recurrence.get("recurrence_frequency")
    interval = recurrence.get("interval") or recurrence.get("recurrence_interval") or 1
    rrule = recurrence.get("rrule")
    if not freq and rrule:
        freq, interval = parse_rrule(rrule)

    board = recurrence.get("board") or {}
    if board:
        board = with_label_aliases(board, ("nome", "name"))

    display_frequency = _recurrence_frequency_label(freq, interval) or rrule or "-"

    return {
        **recurrence,
        "frequency": freq,
        "recurrence_frequency": freq,
        "recurrence_interval": interval,
        "board": board,
        "display_title": recurrence.get("title") or "-",
        "display_board": nested_label(board, "name", "nome")
        or recurrence.get("board_name")
        or "",
        "display_frequency": display_frequency,
    }


def _looks_like_uuid(value):
    if value in (None, ""):
        return False
    return bool(_UUID_RE.match(str(value).strip()))


def _billing_reference_label(record, *, period_start, period_end, customer, contract):
    """Rótulo legível para faturamento — nunca exibe UUID bruto."""
    ref = entity_key(record, "referencia", "reference")
    if ref and not _looks_like_uuid(ref):
        return str(ref)

    if period_start and period_end:
        return f"{period_start} — {period_end}"
    if period_start:
        return str(period_start)
    if period_end:
        return str(period_end)

    contract_label = nested_label(contract, "titulo", "title", "numero", "number")
    if contract_label:
        return contract_label

    customer_label = (
        nested_label(customer, "nome", "name")
        or record.get("client_name")
        or ""
    )
    if customer_label:
        return f"Faturamento — {customer_label}"

    return "Sem referência"


def _format_billing_money(value):
    from crm.helpers.dashboard import format_card_value

    if value in (None, ""):
        return "-"
    return format_card_value("total_value", value)


def enrich_billing(record):
    if not isinstance(record, dict):
        return record
    record = with_label_aliases(
        record,
        ("referencia", "reference"),
        ("valor", "value"),
        ("data_vencimento", "due_date"),
        ("observacoes", "notes"),
    )
    customer = record.get("customer") or {}
    contract = record.get("contract") or {}

    period_start = entity_key(record, "period_start", default="")
    period_end = entity_key(record, "period_end", default="")

    display_referencia = _billing_reference_label(
        record,
        period_start=period_start,
        period_end=period_end,
        customer=customer,
        contract=contract,
    )

    if period_start and period_end:
        display_period = f"{period_start} — {period_end}"
    elif period_start:
        display_period = str(period_start)
    elif period_end:
        display_period = str(period_end)
    else:
        display_period = ""

    planned_raw = entity_key(record, "planned_amount", default="")
    actual_raw = entity_key(record, "actual_amount", default="")
    value_raw = entity_key(record, "valor", "value", default="")

    return {
        **record,
        "display_customer": nested_label(customer, "nome", "name")
        or record.get("client_name")
        or "",
        "display_contract": nested_label(contract, "titulo", "title", "numero", "number")
        or record.get("contract_number")
        or "",
        "display_contract_id": record.get("contract_id") or contract.get("id"),
        "display_referencia": display_referencia,
        "display_period_start": period_start or "-",
        "display_period_end": period_end or "-",
        "display_period": display_period or "-",
        "display_planned_amount": _format_billing_money(planned_raw),
        "display_actual_amount": _format_billing_money(actual_raw),
        "display_valor": _format_billing_money(value_raw),
        "display_vencimento": entity_key(
            record, "data_vencimento", "due_date", default="",
        ) or "-",
        "display_status": record.get("status") or "-",
        "display_observacoes": entity_key(record, "observacoes", "notes", default="") or "-",
    }


def billing_to_json(record):
    """Serializa faturamento enriquecido para respostas AJAX / modal."""
    record = enrich_billing(record or {})
    return {
        "id": entity_key(record, "id"),
        "display_referencia": record.get("display_referencia") or "-",
        "display_customer": record.get("display_customer") or "-",
        "display_contract": record.get("display_contract") or "-",
        "display_contract_id": record.get("display_contract_id") or "",
        "display_period_start": record.get("display_period_start") or "-",
        "display_period_end": record.get("display_period_end") or "-",
        "display_period": record.get("display_period") or "-",
        "display_planned_amount": record.get("display_planned_amount") or "-",
        "display_actual_amount": record.get("display_actual_amount") or "-",
        "display_valor": record.get("display_valor") or "-",
        "display_vencimento": record.get("display_vencimento") or "-",
        "display_status": record.get("display_status") or "-",
        "display_observacoes": record.get("display_observacoes") or "-",
    }


def contract_initial(data):
    customer = data.get("customer") or {}
    service_type = data.get("service_type") or {}
    return {
        "client_gai_id": data.get("client_gai_id")
        or data.get("customer_gai_id")
        or customer.get("gai_id")
        or customer.get("id"),
        "service_type_id": data.get("service_type_id")
        or service_type.get("id"),
        "titulo": data.get("titulo") or data.get("title"),
        "numero": data.get("numero") or data.get("number"),
        "status": data.get("status"),
        "data_inicio": data.get("data_inicio") or data.get("start_date"),
        "data_fim": data.get("data_fim") or data.get("end_date"),
        "valor": data.get("valor") or data.get("value"),
        "descricao": data.get("descricao") or data.get("description"),
    }


def billing_form_json(data):
    """Campos do formulário de faturamento para modais AJAX."""
    initial = billing_initial(data or {})
    due_date = initial.get("data_vencimento")
    if hasattr(due_date, "isoformat"):
        due_date = due_date.isoformat()
    elif isinstance(due_date, str) and "T" in due_date:
        due_date = due_date.split("T", 1)[0]

    contract_id = initial.get("contract_id")
    valor = initial.get("valor")

    return {
        "client_gai_id": initial.get("client_gai_id") or "",
        "contract_id": str(contract_id) if contract_id not in (None, "") else "",
        "referencia": initial.get("referencia") or "",
        "valor": str(valor) if valor not in (None, "") else "",
        "data_vencimento": due_date or "",
        "status": initial.get("status") or "",
        "observacoes": initial.get("observacoes") or "",
    }


def billing_initial(data):
    customer = data.get("customer") or {}
    contract = data.get("contract") or {}
    return {
        "client_gai_id": data.get("client_gai_id")
        or data.get("customer_gai_id")
        or customer.get("gai_id")
        or customer.get("id"),
        "contract_id": data.get("contract_id") or contract.get("id"),
        "referencia": data.get("referencia") or data.get("reference"),
        "valor": data.get("valor") or data.get("value"),
        "data_vencimento": data.get("data_vencimento") or data.get("due_date"),
        "status": data.get("status"),
        "observacoes": data.get("observacoes") or data.get("notes"),
    }
