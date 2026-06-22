"""Resolve nomes e avatares de usuários Django para exibição CRM."""

from crm.helpers.api_display import entity_key

DEFAULT_AVATAR_URL = "/static/global/images/default-avatar.jpg"

_PERSON_NAME_KEYS = (
    "username",
    "author_username",
    "user_username",
    "name",
    "nome",
    "full_name",
    "display_name",
)

_PERSON_USER_ID_KEYS = (
    "user_id",
    "author_id",
    "author_user_id",
)


def person_initials(label):
    if not label or label == "-":
        return "?"
    parts = str(label).strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    text = str(label).strip()
    return text[:2].upper() if text else "?"


def extract_person_user_id(entity):
    if not isinstance(entity, dict):
        return None
    for key in _PERSON_USER_ID_KEYS:
        value = entity.get(key)
        if value not in (None, ""):
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    nested = entity.get("user") or entity.get("author")
    if isinstance(nested, dict):
        return extract_person_user_id(nested)
    return None


def extract_person_label(entity):
    if not isinstance(entity, dict):
        return ""
    for key in _PERSON_NAME_KEYS:
        value = entity.get(key)
        if value not in (None, ""):
            return str(value).strip()
    nested = entity.get("user") or entity.get("author")
    if isinstance(nested, dict):
        return extract_person_label(nested)
    return ""


def _label_looks_like_raw_id(label, user_id):
    if not label:
        return True
    if user_id is not None and str(label) == str(user_id):
        return True
    try:
        return bool(label.isdigit()) and int(label) == user_id
    except (AttributeError, ValueError, TypeError):
        return False


def django_user_display_map(user_ids):
    ids = set()
    for raw in user_ids or []:
        if raw in (None, ""):
            continue
        try:
            ids.add(int(raw))
        except (TypeError, ValueError):
            continue
    if not ids:
        return {}

    from django.contrib.auth.models import User

    result = {}
    qs = User.objects.filter(id__in=ids).select_related("perfil")
    for user in qs:
        perfil = getattr(user, "perfil", None)
        display_name = user.get_full_name().strip() or user.username
        result[user.id] = {
            "username": user.username,
            "display_name": display_name,
            "avatar_url": perfil.avatar if perfil and perfil.avatar else "",
            "initials": person_initials(display_name),
        }
    return result


def django_designation_display_map(designation_ids):
    ids = set()
    for raw in designation_ids or []:
        if raw in (None, ""):
            continue
        try:
            ids.add(int(raw))
        except (TypeError, ValueError):
            continue
    if not ids:
        return {}

    from logistica.models import UserDesignation

    result = {}
    qs = (
        UserDesignation.objects.filter(id__in=ids)
        .select_related("user", "user__perfil", "informacao_adicional")
    )
    for designation in qs:
        user = designation.user
        perfil = getattr(user, "perfil", None)
        gai = designation.informacao_adicional
        gai_label = (gai.nome or gai.razao_social) if gai else ""
        display_name = user.get_full_name().strip() or user.username
        if gai_label:
            display_name = f"{display_name} — {gai_label}"
        result[designation.id] = {
            "display_name": display_name,
            "avatar_url": perfil.avatar if perfil and perfil.avatar else "",
            "initials": person_initials(display_name),
        }
    return result


def collect_person_resolver_ids(entities):
    user_ids = set()
    designation_ids = set()
    for entity in entities or []:
        if not isinstance(entity, dict):
            continue
        user_id = extract_person_user_id(entity)
        if user_id is not None:
            user_ids.add(user_id)
        designation_id = entity_key(entity, "designation_id", "user_designation_id")
        if designation_id not in (None, ""):
            try:
                designation_ids.add(int(designation_id))
            except (TypeError, ValueError):
                pass
    return user_ids, designation_ids


def build_person_resolver(entities):
    user_ids, designation_ids = collect_person_resolver_ids(entities)
    return {
        "users": django_user_display_map(user_ids),
        "designations": django_designation_display_map(designation_ids),
    }


def resolve_person_display(entity, *, user_map=None, designation_map=None):
    user_map = user_map or {}
    designation_map = designation_map or {}
    user_id = extract_person_user_id(entity)
    designation_id = entity_key(entity, "designation_id", "user_designation_id")
    label = extract_person_label(entity)

    if user_id is not None and user_map.get(user_id):
        if _label_looks_like_raw_id(label, user_id) or not label:
            return dict(user_map[user_id])

    if designation_id not in (None, ""):
        try:
            resolved = designation_map.get(int(designation_id))
        except (TypeError, ValueError):
            resolved = None
        if resolved and (not label or _label_looks_like_raw_id(label, user_id)):
            return dict(resolved)

    if user_id is not None and user_map.get(user_id) and not label:
        return dict(user_map[user_id])

    display_name = label or "-"
    return {
        "display_name": display_name,
        "avatar_url": "",
        "initials": person_initials(display_name if display_name != "-" else ""),
    }
