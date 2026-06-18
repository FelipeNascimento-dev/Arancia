"""Cache de permissões do menu na sessão — evita has_perm() repetido no header."""

from __future__ import annotations

SESSION_MENU_PERMS_KEY = "_menu_permissions_cache"


class _PermLookupDict:
    def __init__(self, perm_set: set[str], app_label: str):
        self._perm_set = perm_set
        self._app_label = app_label

    def __getattr__(self, perm_name: str) -> bool:
        return f"{self._app_label}.{perm_name}" in self._perm_set

    def __contains__(self, perm_name: str) -> bool:
        return f"{self._app_label}.{perm_name}" in self._perm_set


class SessionCachedPermWrapper:
    """Substituto leve de django.contrib.auth.context_processors.PermWrapper."""

    def __init__(self, request):
        self._request = request
        self._perm_set = _menu_perm_set(request)

    def __getattr__(self, app_label: str) -> _PermLookupDict:
        return _PermLookupDict(self._perm_set, app_label)

    def __iter__(self):
        return iter(self._perm_set)

    def __contains__(self, perm_name: str) -> bool:
        return perm_name in self._perm_set


def _menu_perm_set(request) -> set[str]:
    cached = request.session.get(SESSION_MENU_PERMS_KEY)
    if cached is not None:
        return set(cached)
    perms = list(request.user.get_all_permissions())
    request.session[SESSION_MENU_PERMS_KEY] = perms
    request.session.modified = True
    return set(perms)


def sync_menu_permissions_session(request) -> None:
    """Grava todas as permissões do usuário na sessão (login)."""
    request.session[SESSION_MENU_PERMS_KEY] = list(
        request.user.get_all_permissions()
    )
    request.session.modified = True


def clear_menu_permissions_session(request) -> None:
    request.session.pop(SESSION_MENU_PERMS_KEY, None)
    request.session.modified = True
