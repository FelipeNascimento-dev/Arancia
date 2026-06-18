from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from functools import wraps


def crm_permission_required(codename):
    """Empilha login + acesso_arancia + permissão CRM."""

    def decorator(view):
        return permission_required(f"crm.{codename}", raise_exception=True)(
            permission_required("logistica.acesso_arancia", raise_exception=True)(
                login_required(login_url="logistica:login")(view)
            )
        )

    return decorator


def _user_has_crm_access(user):
    return user.has_module_perms("crm")


def crm_any_access_required(view):
    """Login + acesso_arancia + ao menos uma permissão crm.*."""

    @login_required(login_url="logistica:login")
    @permission_required("logistica.acesso_arancia", raise_exception=True)
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if not _user_has_crm_access(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return _wrapped
