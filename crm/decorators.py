from functools import wraps

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied

# Menu CRM comercial (clientes, contratos, faturamento, configurações).
CRM_COMMERCIAL_PERMISSIONS = (
    'crm.view_clients',
    'crm.view_contracts',
    'crm.view_billing',
    'crm.view_settings',
)

# Menu Projetos (tarefas, projetos, boards, recorrências).
PROJECTS_PERMISSIONS = (
    'crm.view_tasks',
    'crm.view_projects',
    'crm.view_boards',
    'crm.view_task_recurrences',
    'crm.view_teams',
)

CRM_ENTRY_PERMISSIONS = CRM_COMMERCIAL_PERMISSIONS + PROJECTS_PERMISSIONS


def user_has_any_crm_perm(user):
    if not user.is_authenticated:
        return False
    return any(user.has_perm(perm) for perm in CRM_ENTRY_PERMISSIONS)


def user_has_crm_commercial_perm(user):
    if not user.is_authenticated:
        return False
    return any(user.has_perm(perm) for perm in CRM_COMMERCIAL_PERMISSIONS)


def user_has_projects_perm(user):
    if not user.is_authenticated:
        return False
    return any(user.has_perm(perm) for perm in PROJECTS_PERMISSIONS)


def crm_access_required(view_func):
    """Baseline: login + logistica.acesso_arancia."""
    decorated = login_required(login_url='logistica:login')(view_func)
    decorated = permission_required('logistica.acesso_arancia', raise_exception=True)(decorated)
    return decorated


def crm_module_required(view_func):
    """Baseline + ao menos uma permissão crm.view_*."""
    @crm_access_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not user_has_any_crm_perm(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped


def crm_perm_required(perm_codename):
    """Empilha permissão CRM específica (ex.: view_clients)."""
    django_perm = perm_codename if perm_codename.startswith('crm.') else f'crm.{perm_codename}'

    def decorator(view_func):
        @crm_access_required
        @permission_required(django_perm, raise_exception=True)
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
