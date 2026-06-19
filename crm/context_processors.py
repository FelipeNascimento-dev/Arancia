from __future__ import annotations

import time

from django.conf import settings

from crm.helpers.lookup_cache import get_user_scoped_lookup
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError
from crm_api.services.auth import get_me_context

SESSION_CRM_CONTEXT_KEY = "_crm_menu_context_cache"
SESSION_CRM_CONTEXT_TS_KEY = "_crm_menu_context_cache_ts"
SESSION_USER_HAS_CRM_MODULE_KEY = "_user_has_crm_module"


def _cache_ttl() -> int:
    return int(getattr(settings, "CRM_MENU_CONTEXT_CACHE_TTL", 90))


def _empty_crm_context():
    return {
        "has_any_access": False,
        "permission_codenames": [],
        "modules": [],
        "accessible_boards": [],
        "accessible_projects": [],
    }


def clear_crm_context_cache(request) -> None:
    """Invalida cache de /me/context na sessão (login/logout)."""
    request.session.pop(SESSION_CRM_CONTEXT_KEY, None)
    request.session.pop(SESSION_CRM_CONTEXT_TS_KEY, None)
    request.session.pop(SESSION_USER_HAS_CRM_MODULE_KEY, None)


def sync_crm_module_session(request) -> None:
    """Grava flag de módulo CRM na sessão (login) — evita has_module_perms fora do CRM."""
    if not request.user.is_authenticated:
        return
    request.session[SESSION_USER_HAS_CRM_MODULE_KEY] = request.user.has_module_perms(
        "crm"
    )
    request.session.modified = True


def _user_has_crm_module(request) -> bool:
    if SESSION_USER_HAS_CRM_MODULE_KEY in request.session:
        return bool(request.session[SESSION_USER_HAS_CRM_MODULE_KEY])
    if not request.user.is_authenticated:
        return False
    return request.user.has_module_perms("crm")


def _path_needs_full_crm_context(request) -> bool:
    """Carrega /me/context apenas em páginas CRM ou Projetos."""
    path = request.path.lower()
    for segment in ("/crm/", "/projetos/"):
        if segment in path:
            return True
    return False


def _get_cached_context(request):
    data = request.session.get(SESSION_CRM_CONTEXT_KEY)
    ts = request.session.get(SESSION_CRM_CONTEXT_TS_KEY)
    if not data or ts is None:
        return None
    if time.time() - float(ts) > _cache_ttl():
        return None
    return data


def _set_cached_context(request, data: dict) -> None:
    request.session[SESSION_CRM_CONTEXT_KEY] = data
    request.session[SESSION_CRM_CONTEXT_TS_KEY] = time.time()
    request.session.modified = True


def _django_crm_permissions(user):
    """Permissões CRM locais (gates) — não usar permission_codenames da API."""
    if not user.has_module_perms("crm"):
        return []
    return [
        perm.split(".", 1)[1]
        for perm in user.get_all_permissions()
        if perm.startswith("crm.")
    ]


def _fetch_me_context(request) -> dict:
    """Carrega /me/context só para accessible_boards/projects (não para gates)."""

    def _load():
        try:
            client = CrmApiClient(request)
            return get_me_context(client) or {}
        except CrmApiError:
            return {}
        except Exception:
            return {}

    ttl = int(getattr(settings, "CRM_ME_CONTEXT_REDIS_CACHE_TTL", 300))
    return get_user_scoped_lookup(request, "me_context", _load, redis_ttl=ttl)


def resolve_crm_context_data(request) -> dict:
    """Resolve dados de contexto CRM (cache, API ou fallback leve)."""
    if not request.user.is_authenticated:
        return _empty_crm_context()

    permission_codenames = _django_crm_permissions(request.user)

    cached = _get_cached_context(request)
    if cached is not None:
        api_data = cached
    elif _path_needs_full_crm_context(request):
        api_data = _fetch_me_context(request)
        _set_cached_context(request, api_data)
    else:
        api_data = {}

    has_any_access = bool(permission_codenames) or _user_has_crm_module(request)

    return {
        "has_any_access": has_any_access,
        "permission_codenames": permission_codenames,
        "modules": api_data.get("modules") or [],
        "user": api_data.get("user") or {},
        "accessible_boards": api_data.get("accessible_boards") or [],
        "accessible_projects": api_data.get("accessible_projects") or [],
    }


def crm_menu_context(request):
    data = resolve_crm_context_data(request)
    request._crm_context_data = data
    return {"crm_context": data}
