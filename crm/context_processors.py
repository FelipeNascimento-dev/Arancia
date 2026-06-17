from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError
from crm_api.services.auth import get_me_context


def _empty_crm_context():
    return {
        "has_any_access": False,
        "permission_codenames": [],
        "modules": [],
        "accessible_boards": [],
        "accessible_projects": [],
    }


def crm_menu_context(request):
    if not request.user.is_authenticated:
        return {"crm_context": _empty_crm_context()}

    try:
        client = CrmApiClient(request)
        data = get_me_context(client) or {}
    except CrmApiError:
        data = _fallback_context_from_django(request.user)
    except Exception:
        data = _fallback_context_from_django(request.user)

    permission_codenames = data.get("permission_codenames") or []
    if not permission_codenames:
        permission_codenames = _django_crm_permissions(request.user)

    has_any_access = bool(permission_codenames) or data.get("has_any_access", False)

    return {
        "crm_context": {
            "has_any_access": has_any_access,
            "permission_codenames": permission_codenames,
            "modules": data.get("modules") or [],
            "user": data.get("user") or {},
            "accessible_boards": data.get("accessible_boards") or [],
            "accessible_projects": data.get("accessible_projects") or [],
        }
    }


def _django_crm_permissions(user):
    return [
        perm.split(".", 1)[1]
        for perm in user.get_all_permissions()
        if perm.startswith("crm.")
    ]


def _fallback_context_from_django(user):
    codenames = _django_crm_permissions(user)
    return {
        "has_any_access": bool(codenames),
        "permission_codenames": codenames,
        "modules": [],
        "accessible_boards": [],
        "accessible_projects": [],
    }
