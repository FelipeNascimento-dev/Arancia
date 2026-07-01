import json


def _parse_targets(raw):
    if not raw or not str(raw).strip():
        return []

    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return []

    if not isinstance(parsed, list):
        return []

    return parsed


def extract_create_form_draft(post_data):
    """Extrai rascunho do formulário de criação para reexibir após erro de validação/API."""
    return {
        "form": "create",
        "title": post_data.get("title") or "",
        "summary": post_data.get("summary") or "",
        "content": post_data.get("content") or "",
        "item_type": post_data.get("item_type") or "notice",
        "severity": post_data.get("severity") or "informational",
        "target_type": post_data.get("target_type") or "all",
        "targets": _parse_targets(post_data.get("targets_json")),
        "starts_at": post_data.get("starts_at") or "",
        "ends_at": post_data.get("ends_at") or "",
        "external_link": post_data.get("external_link") or "",
        "is_active": post_data.get("is_active") == "on",
        "is_pinned": post_data.get("is_pinned") == "on",
        "is_indefinite": post_data.get("is_indefinite") == "on",
        "until_read": post_data.get("until_read") == "on",
    }


def extract_created_item_id(create_resp):
    if not isinstance(create_resp, dict):
        return None

    for key in ("id", "item_id", "mural_item_id"):
        value = create_resp.get(key)
        if value is not None:
            return value

    nested = create_resp.get("item") or create_resp.get("data")
    if isinstance(nested, dict):
        return extract_created_item_id(nested)

    return None
