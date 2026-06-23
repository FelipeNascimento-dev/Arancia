import json
from datetime import datetime
from zoneinfo import ZoneInfo

BR_TZ = ZoneInfo("America/Sao_Paulo")
UTC_TZ = ZoneInfo("UTC")

VALID_ROOT_TARGET_TYPES = frozenset({"all", "custom"})
VALID_BLOCK_TARGET_TYPES = frozenset({"users", "gais", "groups"})


def _format_datetime_to_api(value):
    if not value:
        return None

    try:
        dt_br = datetime.strptime(value, "%Y-%m-%dT%H:%M")
        dt_br = dt_br.replace(tzinfo=BR_TZ)
        dt_utc = dt_br.astimezone(UTC_TZ)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception:
        return None


def _parse_targets_json(raw):
    if not raw or not str(raw).strip():
        return None

    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(parsed, list):
        return None

    return parsed


def _normalize_block_ids(raw_ids):
    if not isinstance(raw_ids, list):
        return []

    ids = []
    for raw_id in raw_ids:
        if isinstance(raw_id, bool):
            continue
        if isinstance(raw_id, int):
            ids.append(raw_id)
            continue
        text = str(raw_id).strip()
        if text.isdigit():
            ids.append(int(text))

    return ids


def _validate_targets(target_type, targets):
    if target_type == "all":
        if targets:
            return "O campo targets não deve ser enviado quando o público for 'Todos'."
        return None

    if target_type != "custom":
        return "Público alvo inválido. Use 'Todos' ou 'Personalizado'."

    if not targets:
        return "O público personalizado exige pelo menos um tipo com itens selecionados."

    seen_types = set()

    for index, block in enumerate(targets, start=1):
        if not isinstance(block, dict):
            return f"Bloco de público {index} inválido."

        block_type = block.get("target_type")
        if block_type not in VALID_BLOCK_TARGET_TYPES:
            return (
                f"Tipo de público inválido no bloco {index}. "
                "Use usuários, GAIs ou grupos."
            )

        if block_type in seen_types:
            return "Não é permitido repetir o mesmo tipo de público em blocos diferentes."

        seen_types.add(block_type)

        ids = _normalize_block_ids(block.get("ids"))
        if not ids:
            return f"Selecione ao menos um item no bloco {index} ({block_type})."

    return None


def build_create_item_v2_payload(*, post_data, user_id, attachments, image_url):
    """
    Monta o payload de criação v2 e valida targeting antes da chamada à API.

    Retorna (payload, erro_amigavel).
    erro_amigavel preenchido = validação Django antes da API.
    """
    target_type = (post_data.get("target_type") or "").strip()

    if target_type not in VALID_ROOT_TARGET_TYPES:
        return None, "Público alvo inválido. Use 'Todos' ou 'Personalizado'."

    targets = None
    if target_type == "custom":
        targets = _parse_targets_json(post_data.get("targets_json"))
        if targets is None:
            return None, "Dados de público personalizado inválidos."

    target_error = _validate_targets(target_type, targets)
    if target_error:
        return None, target_error

    payload = {
        "title": post_data.get("title"),
        "summary": post_data.get("summary"),
        "content": post_data.get("content"),
        "item_type": post_data.get("item_type"),
        "severity": post_data.get("severity"),
        "target_type": target_type,
        "is_active": post_data.get("is_active") == "on",
        "is_pinned": post_data.get("is_pinned") == "on",
        "is_indefinite": post_data.get("is_indefinite") == "on",
        "until_read": post_data.get("until_read") == "on",
        "starts_at": _format_datetime_to_api(post_data.get("starts_at")),
        "ends_at": _format_datetime_to_api(post_data.get("ends_at")),
        "external_link": post_data.get("external_link") or None,
        "attachments": attachments or [],
        "image_url": image_url,
        "created_by_id": user_id,
    }

    if target_type == "custom":
        normalized_targets = []
        for block in targets:
            normalized_targets.append(
                {
                    "target_type": block["target_type"],
                    "ids": _normalize_block_ids(block.get("ids")),
                }
            )
        payload["targets"] = normalized_targets

    return payload, None
