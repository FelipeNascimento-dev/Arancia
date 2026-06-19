"""Helpers compartilhados para montar choices de selects a partir de lookups."""

from crm.helpers.api_display import entity_key, nested_label


def lookup_item_id(item, *extra_keys):
    """Resolve ID de item de lookup (usuário, GAI, designação, etc.)."""
    if not isinstance(item, dict):
        return None
    return entity_key(item, "id", *extra_keys)


def build_select_choices(items, id_keys=("id",), label_keys=("name", "nome"), *, as_str=False):
    choices = [("", "---------")]
    for item in items or []:
        if not isinstance(item, dict):
            continue
        item_id = lookup_item_id(item, *id_keys)
        if item_id in (None, ""):
            continue
        label = nested_label(item, *label_keys) or str(item_id)
        value = str(item_id) if as_str else item_id
        choices.append((value, label))
    return choices


def build_user_choices(items):
    choices = [("", "---------")]
    for item in items or []:
        if not isinstance(item, dict):
            continue
        item_id = lookup_item_id(item, "user_id")
        if item_id in (None, ""):
            continue
        username = nested_label(item, "username", "user_username")
        name = nested_label(item, "name", "full_name", "display_name")
        if username and name and name != username:
            label = f"{username} — {name}"
        else:
            label = username or name or str(item_id)
        choices.append((str(item_id), label))
    return choices
