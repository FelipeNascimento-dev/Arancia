"""Catálogos de audiência do mural (usuários ARC*, grupos arancia_*, GAIs)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from logistica.models import Group, GroupAditionalInformation

MURAL_TARGET_CATALOGS_CACHE_KEY = "mural:target_catalogs:v1"


def _cache_ttl() -> int:
    return int(getattr(settings, "MURAL_TARGET_CATALOGS_CACHE_TTL", 600))


def _load_target_catalogs() -> tuple[list, list, list]:
    User = get_user_model()

    target_users = list(
        User.objects.filter(username__istartswith="ARC")
        .order_by("username")
        .values("id", "username", "first_name", "last_name")
    )

    target_groups = list(
        Group.objects.filter(name__istartswith="arancia_")
        .order_by("name")
        .values("id", "name")
    )

    target_gais_raw = list(
        GroupAditionalInformation.objects.select_related("group")
        .filter(group__name__istartswith="arancia_")
        .order_by("nome")
        .values("id", "nome", "group_id", "group__name")
    )

    target_gais = [
        {
            "id": gai["id"],
            "nome": gai["nome"],
            "group_id": gai["group_id"],
            "group_name": gai["group__name"],
        }
        for gai in target_gais_raw
    ]

    return target_users, target_groups, target_gais


def get_mural_target_catalogs() -> tuple[list, list, list]:
    """Catálogos globais com cache Redis (gerenciamento / usuários com ger_mural)."""
    try:
        cached = cache.get(MURAL_TARGET_CATALOGS_CACHE_KEY)
        if cached is not None:
            return cached
    except Exception:
        pass

    data = _load_target_catalogs()
    try:
        cache.set(MURAL_TARGET_CATALOGS_CACHE_KEY, data, _cache_ttl())
    except Exception:
        pass
    return data


def empty_target_catalogs() -> tuple[list, list, list]:
    return [], [], []
