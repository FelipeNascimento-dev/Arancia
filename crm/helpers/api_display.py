"""Helpers para exibir objetos aninhados retornados pela API CRM."""

import re

from crm.helpers.date_format import format_date_br, format_datetime_br, format_period_br

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_OPAQUE_ID_MIN_LEN = 12


def is_opaque_id(value):
    """True para UUIDs e identificadores longos que não devem aparecer na UI."""
    if value in (None, ""):
        return False
    s = str(value).strip()
    if _looks_like_uuid(s):
        return True
    if s.isdigit() and len(s) >= _OPAQUE_ID_MIN_LEN:
        return True
    return len(s) >= 24 and "-" in s


def short_ref(value, length=8):
    """Prefixo curto de um ID opaco (ex.: primeiros 8 chars de UUID)."""
    if value in (None, ""):
        return ""
    s = str(value).strip()
    if not is_opaque_id(s):
        return s
    return s[:length]


def display_label(value, default="-"):
    """Exibe valor legível ou default quando o identificador é opaco."""
    if value in (None, ""):
        return default
    if is_opaque_id(value):
        return default
    return str(value)


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
        "display_name": entity_key(board, "name", "nome", default="-"),
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
        column.get("kanban_position")
        if column.get("kanban_position") is not None
        else column.get("sort_order")
        if column.get("sort_order") is not None
        else column.get("position")
        if column.get("position") is not None
        else 0
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
        "display_vencimento": format_date_br(
            entity_key(alert, "due_date", "data_vencimento", default=""),
            default="-",
        ),
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
    from crm.helpers.contract_meta import (
        contract_money_display,
        parse_contract_meta,
    )

    description_raw = entity_key(contract, "descricao", "description", default="")
    meta, clean_description = parse_contract_meta(description_raw)
    api_numero = entity_key(contract, "numero", "number", default="")
    api_valor = entity_key(contract, "valor", "value", default="")
    numero = api_numero or meta.get("numero", "")
    valor_raw = api_valor or meta.get("valor", "")
    customer = contract.get("customer") or {}
    service_type = contract.get("service_type") or {}
    return {
        **contract,
        "descricao": clean_description,
        "display_customer": nested_label(customer, "nome", "name")
        or contract.get("client_name")
        or "",
        "display_service_type": nested_label(
            service_type, "description", "name", "nome", "type",
        )
        or contract.get("service_type_name")
        or "",
        "display_numero": numero,
        "display_titulo": entity_key(contract, "titulo", "title", default=""),
        "display_data_inicio": format_date_br(
            entity_key(contract, "data_inicio", "start_date", default=""),
            default="-",
        ),
        "display_data_fim": format_date_br(
            entity_key(contract, "data_fim", "end_date", default=""),
            default="-",
        ),
        "display_valor": contract_money_display(valor_raw),
        "display_descricao": clean_description or "",
        "display_status": contract.get("status") or "",
        "valor": valor_raw,
        "numero": numero,
    }


_AUDIO_EXTENSIONS = frozenset({"mp3", "wav", "ogg", "m4a", "aac", "flac", "webm"})
_VIDEO_EXTENSIONS = frozenset({"mp4", "webm", "mov", "m4v", "avi", "mkv"})
_IMAGE_EXTENSIONS = frozenset({"jpg", "jpeg", "png", "gif", "webp", "svg", "bmp"})


def _contract_file_extension(arquivo):
    extension = str(arquivo.get("extension") or "").lower().lstrip(".")
    if extension:
        return extension
    filename = str(arquivo.get("filename") or "")
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return ""


def _contract_file_preview_kind(arquivo, extension):
    content_type = str(arquivo.get("content_type") or "").lower()
    if content_type.startswith("image/") or extension in _IMAGE_EXTENSIONS:
        return "image"
    if content_type.startswith("audio/") or extension in _AUDIO_EXTENSIONS:
        return "audio"
    if content_type.startswith("video/") or extension in _VIDEO_EXTENSIONS:
        return "video"
    if content_type == "application/pdf" or extension == "pdf":
        return "pdf"
    return "download"


def _format_file_size(size):
    if size in (None, ""):
        return ""
    try:
        bytes_size = int(size)
    except (TypeError, ValueError):
        return str(size)
    if bytes_size < 1024:
        return f"{bytes_size} B"
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    return f"{bytes_size / (1024 * 1024):.1f} MB"


def enrich_contract_file(arquivo):
    if not isinstance(arquivo, dict):
        return arquivo
    extension = _contract_file_extension(arquivo)
    preview_url = (
        arquivo.get("firebase_url")
        or arquivo.get("url")
        or arquivo.get("download_url")
        or ""
    )
    return {
        **arquivo,
        "preview_url": preview_url,
        "preview_kind": _contract_file_preview_kind(arquivo, extension),
        "display_extension": extension.upper() if extension else "-",
        "display_file_size": _format_file_size(arquivo.get("file_size")),
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
        "numero": contract.get("display_numero") or entity_key(contract, "numero", "number"),
        "display_numero": contract.get("display_numero") or "",
        "status": contract.get("status") or "",
        "data_inicio": entity_key(contract, "data_inicio", "start_date"),
        "data_fim": entity_key(contract, "data_fim", "end_date"),
        "display_data_inicio": contract.get("display_data_inicio")
        or format_date_br(entity_key(contract, "data_inicio", "start_date"), default="-"),
        "display_data_fim": contract.get("display_data_fim")
        or format_date_br(entity_key(contract, "data_fim", "end_date"), default="-"),
        "valor": contract.get("valor") or entity_key(contract, "valor", "value"),
        "display_valor": contract.get("display_valor") or "",
        "service_type_id": contract.get("service_type_id") or service_type.get("id") or "",
        "descricao": contract.get("descricao") or entity_key(contract, "descricao", "description"),
        "display_descricao": contract.get("display_descricao") or "",
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


def _service_type_label_key(service_type):
    return str(service_type_option_label(service_type) or "").strip().casefold()


def service_types_for_gai(service_types, gai_id):
    """Tipos de serviço para um cliente: específicos do GAI + globais sem repetir rótulo."""
    items = [
        item
        for item in (service_types or [])
        if isinstance(item, dict) and item.get("id") is not None
    ]
    if gai_id in (None, ""):
        return [
            item
            for item in items
            if service_type_client_gai_id(item) in (None, "")
        ]

    gai_key = str(gai_id)
    client_specific = []
    global_items = []
    for item in items:
        client_id = service_type_client_gai_id(item)
        if client_id in (None, ""):
            global_items.append(item)
        elif str(client_id) == gai_key:
            client_specific.append(item)

    client_labels = {_service_type_label_key(item) for item in client_specific}
    deduped_globals = []
    seen_global_labels = set()
    for item in global_items:
        label_key = _service_type_label_key(item)
        if not label_key or label_key in client_labels or label_key in seen_global_labels:
            continue
        seen_global_labels.add(label_key)
        deduped_globals.append(item)

    return client_specific + deduped_globals


def service_types_for_config(service_types):
    options = []
    for item in service_types or []:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if item_id is None:
            continue
        label = service_type_option_label(item)
        if not label:
            label = display_label(item_id, default="Sem descrição")
        options.append({
            "id": item_id,
            "label": label,
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
        "display_name": entity_key(project, "name", "nome", default="-"),
        "display_customer": nested_label(customer, "nome", "name")
        or project.get("customer_gai_name")
        or "",
    }


def enrich_task_lookups(lookups):
    """Preenche aliases e normaliza catálogos usados nos filtros/forms de tasks."""
    from crm.helpers.lookup_entities import (
        merge_gai_candidate_lists,
        normalize_lookup_designations,
        normalize_lookup_gais,
        normalize_lookup_users,
    )

    if not isinstance(lookups, dict):
        return lookups or {}
    result = dict(lookups)

    for key in ("status_tasks", "priorities", "boards", "column_templates", "projects"):
        items = result.get(key)
        if isinstance(items, list):
            result[key] = [
                with_label_aliases(item, ("nome", "name"))
                for item in items
                if isinstance(item, dict)
            ]

    users = result.get("users")
    if isinstance(users, list):
        result["users"] = normalize_lookup_users(users)

    designations = result.get("designations")
    if isinstance(designations, list):
        result["designations"] = normalize_lookup_designations(designations)

    gais = merge_gai_candidate_lists(
        result.get("gais"),
        result.get("customers"),
    )
    if gais:
        result["gais"] = gais
    elif isinstance(result.get("gais"), list):
        result["gais"] = normalize_lookup_gais(result["gais"])

    team_gais = result.get("team_gais")
    if isinstance(team_gais, list):
        result["team_gais"] = normalize_lookup_gais(team_gais)

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
        return format_period_br(period_start, period_end)
    if period_start:
        return format_date_br(period_start)
    if period_end:
        return format_date_br(period_end)

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
        display_period = format_period_br(period_start, period_end)
    elif period_start:
        display_period = format_date_br(period_start)
    elif period_end:
        display_period = format_date_br(period_end)
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
        "display_period_start": format_date_br(period_start, default="-"),
        "display_period_end": format_date_br(period_end, default="-"),
        "display_period": display_period or "-",
        "display_planned_amount": _format_billing_money(planned_raw),
        "display_actual_amount": _format_billing_money(actual_raw),
        "display_valor": _format_billing_money(value_raw),
        "display_vencimento": format_date_br(
            entity_key(record, "data_vencimento", "due_date", default=""),
            default="-",
        ),
        "display_status": record.get("status") or "-",
        "display_observacoes": entity_key(record, "observacoes", "notes", default="") or "-",
    }


def enrich_billing_with_lookups(record, *, clients_by_gai=None, contracts_by_id=None):
    """Completa exibição quando a listagem da API não traz objetos aninhados."""
    from crm.views.views_contratos._helpers import contract_client_gai_id, contract_option_label

    record = enrich_billing(record)
    clients_by_gai = clients_by_gai or {}
    contracts_by_id = contracts_by_id or {}

    if not record.get("display_customer"):
        gai_id = (
            record.get("customer_gai_id")
            or record.get("client_gai_id")
            or (record.get("customer") or {}).get("gai_id")
            or (record.get("customer") or {}).get("id")
        )
        if gai_id not in (None, ""):
            client = clients_by_gai.get(str(gai_id))
            if client:
                record["display_customer"] = (
                    client.get("nome") or client.get("name") or str(gai_id)
                )

    contract_id = record.get("contract_id") or record.get("display_contract_id")
    contract = None
    if contract_id not in (None, ""):
        record.setdefault("contract_id", contract_id)
        contract = contracts_by_id.get(str(contract_id))
        if contract and not record.get("display_contract"):
            record["display_contract"] = contract_option_label(contract)
            record["display_contract_id"] = contract_id

    if contract:
        period_start = entity_key(record, "period_start", default="")
        period_end = entity_key(record, "period_end", default="")
        if not period_start:
            period_start = contract.get("start_date") or contract.get("data_inicio") or ""
        if not period_end:
            period_end = contract.get("end_date") or contract.get("data_fim") or ""
        if period_start and record.get("display_period_start") in (None, "", "-"):
            record["display_period_start"] = format_date_br(period_start, default="-")
        if period_end and record.get("display_period_end") in (None, "", "-"):
            record["display_period_end"] = format_date_br(period_end, default="-")
        if period_start and period_end:
            record["display_period"] = format_period_br(period_start, period_end)
            if record.get("display_referencia") in (None, "", "Sem referência"):
                record["display_referencia"] = format_period_br(period_start, period_end)

    if contract:
        gai_id = contract_client_gai_id(contract)
        if gai_id not in (None, ""):
            record.setdefault("customer_gai_id", gai_id)
            record.setdefault("client_gai_id", gai_id)

    reference = entity_key(record, "referencia", "reference")
    if reference and not _looks_like_uuid(reference):
        record["display_referencia"] = str(reference)

    raw_value = entity_key(record, "valor", "value")
    if raw_value not in (None, "") and record.get("display_valor") in (None, "", "-"):
        record["display_valor"] = _format_billing_money(raw_value)

    planned_raw = entity_key(record, "planned_amount", default="")
    if planned_raw in (None, "") and raw_value not in (None, ""):
        if record.get("display_planned_amount") in (None, "", "-"):
            record["display_planned_amount"] = _format_billing_money(raw_value)

    due_raw = entity_key(record, "data_vencimento", "due_date", default="")
    if due_raw and record.get("display_vencimento") in (None, "", "-"):
        record["display_vencimento"] = format_date_br(due_raw, default="-")

    return record


def billing_to_json(record, *, already_enriched=False):
    """Serializa faturamento enriquecido para respostas AJAX / modal."""
    if not already_enriched:
        record = enrich_billing(record or {})
    elif not record:
        record = {}
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
    from crm.helpers.contract_meta import parse_contract_meta

    customer = data.get("customer") or {}
    service_type = data.get("service_type") or {}
    description_raw = data.get("descricao") or data.get("description") or ""
    meta, clean_description = parse_contract_meta(description_raw)
    return {
        "client_gai_id": data.get("client_gai_id")
        or data.get("customer_gai_id")
        or customer.get("gai_id")
        or customer.get("id"),
        "service_type_id": data.get("service_type_id")
        or service_type.get("id"),
        "titulo": data.get("titulo") or data.get("title"),
        "numero": data.get("numero") or data.get("number") or meta.get("numero", ""),
        "status": data.get("status"),
        "data_inicio": data.get("data_inicio") or data.get("start_date"),
        "data_fim": data.get("data_fim") or data.get("end_date"),
        "valor": data.get("valor") or data.get("value") or meta.get("valor", ""),
        "descricao": clean_description,
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
    referencia = data.get("referencia") or data.get("reference")
    if not referencia or _looks_like_uuid(referencia):
        display_ref = data.get("display_referencia")
        if (
            display_ref
            and display_ref not in ("-", "Sem referência")
            and not _looks_like_uuid(display_ref)
        ):
            referencia = display_ref

    return {
        "client_gai_id": data.get("client_gai_id")
        or data.get("customer_gai_id")
        or customer.get("gai_id")
        or customer.get("id"),
        "contract_id": data.get("contract_id") or contract.get("id") or data.get("display_contract_id"),
        "referencia": referencia,
        "valor": data.get("valor") or data.get("value") or data.get("planned_amount"),
        "data_vencimento": data.get("data_vencimento") or data.get("due_date"),
        "status": data.get("status"),
        "observacoes": data.get("observacoes") or data.get("notes"),
    }
