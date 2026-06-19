"""Normalização de catálogos de lookup (usuários, GAIs, designações) para forms CRM/Projetos."""

from crm.helpers.api_display import entity_key, with_label_aliases


def normalize_lookup_user(item):
    if not isinstance(item, dict):
        return item
    user_id = entity_key(item, "id", "user_id", "pk")
    username = entity_key(item, "username", "user_username")
    name = entity_key(item, "name", "full_name", "display_name") or username
    if user_id in (None, ""):
        return item
    return {
        **item,
        "id": user_id,
        "user_id": user_id,
        "username": username,
        "name": name,
    }


def normalize_lookup_gai(item):
    if not isinstance(item, dict):
        return item
    gai_id = entity_key(item, "id", "gai_id", "customer_gai_id", "client_id")
    nome = entity_key(item, "nome", "name", "razao_social", "title", "label")
    if gai_id in (None, ""):
        return item
    return {
        **item,
        "id": gai_id,
        "gai_id": gai_id,
        "nome": nome,
        "name": nome,
    }


def normalize_lookup_designation(item):
    if not isinstance(item, dict):
        return item
    designation_id = entity_key(item, "id", "designation_id", "user_designation_id")
    username = entity_key(item, "username", "user_username")
    label = entity_key(item, "label", "name", "nome") or username
    if designation_id in (None, ""):
        return item
    return {
        **item,
        "id": designation_id,
        "designation_id": designation_id,
        "label": label,
        "username": username,
    }


def normalize_lookup_users(items):
    result = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        normalized = normalize_lookup_user(with_label_aliases(item, ("name", "nome")))
        if normalized.get("id") not in (None, ""):
            result.append(normalized)
    return result


def normalize_lookup_gais(items):
    result = []
    seen = set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        normalized = normalize_lookup_gai(with_label_aliases(item, ("nome", "name")))
        gai_id = normalized.get("id")
        if gai_id in (None, "") or gai_id in seen:
            continue
        seen.add(gai_id)
        result.append(normalized)
    return result


def normalize_lookup_designations(items):
    result = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        normalized = normalize_lookup_designation(
            with_label_aliases(item, ("label", "username", "nome", "name"))
        )
        if normalized.get("id") not in (None, ""):
            result.append(normalized)
    return result


def django_system_users():
    from django.contrib.auth.models import User

    return normalize_lookup_users([
        {
            "id": user.id,
            "username": user.username,
            "name": user.get_full_name() or user.username,
        }
        for user in User.objects.filter(is_active=True).order_by("username")
    ])


def django_system_gais():
    from logistica.models import GroupAditionalInformation

    return normalize_lookup_gais([
        {
            "id": gai.id,
            "gai_id": gai.id,
            "nome": gai.nome or gai.razao_social or f"GAI {gai.id}",
            "name": gai.nome or gai.razao_social or f"GAI {gai.id}",
            "is_active": True,
        }
        for gai in GroupAditionalInformation.objects.select_related("group").order_by("nome", "id")
    ])


def django_designations():
    from logistica.models import UserDesignation

    items = []
    qs = (
        UserDesignation.objects.select_related("user", "informacao_adicional")
        .filter(user__is_active=True)
        .order_by("user__username")
    )
    for designation in qs:
        user = designation.user
        gai = designation.informacao_adicional
        gai_label = (gai.nome or gai.razao_social) if gai else "—"
        items.append({
            "id": designation.id,
            "username": user.username,
            "label": f"{user.username} — {gai_label}",
        })
    return normalize_lookup_designations(items)


def merge_gai_candidate_lists(*sources):
    """Unifica listas de GAIs/clientes de várias fontes (board-page, CRM, Django)."""
    merged = []
    for source in sources:
        if not source:
            continue
        if isinstance(source, dict):
            source = source.get("items") or source.get("results") or []
        if isinstance(source, list):
            merged.extend(source)
    return normalize_lookup_gais(merged)
