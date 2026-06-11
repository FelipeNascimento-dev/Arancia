from django import template

from crm.decorators import (
    user_has_any_crm_perm,
    user_has_crm_commercial_perm,
    user_has_projects_perm,
)
from crm.services.refs import (
    board_ref_label,
    client_ref_label,
    contract_ref_label,
    customer_ref_label,
    moved_by_label,
    move_status_label,
    priority_ref_label,
    project_ref_label,
    requester_ref_label,
    service_type_ref_label,
    status_ref_label,
    subject_ref_label,
    task_ref_label,
    template_ref_label,
    user_ref_label,
)

register = template.Library()


@register.simple_tag(takes_context=True)
def crm_any_perm(context):
    """True se o usuário possui ao menos uma permissão CRM ou Projetos."""
    request = context.get('request')
    if not request:
        return False
    return user_has_any_crm_perm(request.user)


@register.simple_tag(takes_context=True)
def crm_commercial_perm(context):
    """True se o usuário pode ver o menu CRM comercial."""
    request = context.get('request')
    if not request:
        return False
    return user_has_crm_commercial_perm(request.user)


@register.simple_tag(takes_context=True)
def projects_any_perm(context):
    """True se o usuário pode ver o menu Projetos."""
    request = context.get('request')
    if not request:
        return False
    return user_has_projects_perm(request.user)


@register.simple_tag(takes_context=True)
def crm_perm(context, perm_codename):
    """Verifica permissão CRM (ex.: {% crm_perm 'view_clients' %})."""
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    django_perm = perm_codename if perm_codename.startswith('crm.') else f'crm.{perm_codename}'
    return request.user.has_perm(django_perm)


@register.filter
def crm_get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def boards_of_type(boards, board_type):
    """Filtra accessible_boards por board_type (crm, project, internal_public)."""
    if not boards:
        return []
    return [board for board in boards if board.get('board_type') == board_type]


def _resolve_lookups(record, lookups):
    if isinstance(lookups, dict):
        return lookups
    if isinstance(record, dict):
        return record.get('_lookups')
    return None


@register.filter
def crm_customer_label(record, lookups=None):
    return customer_ref_label(record, lookups=_resolve_lookups(record, lookups))


@register.filter
def crm_client_label(record, lookups=None):
    return client_ref_label(record, lookups=_resolve_lookups(record, lookups))


@register.filter
def crm_contract_label(record, lookups=None):
    return contract_ref_label(record)


@register.filter
def crm_board_label(record, lookups=None):
    return board_ref_label(record)


@register.filter
def crm_status_label(record, lookups=None):
    return status_ref_label(record)


@register.filter
def crm_priority_label(record, lookups=None):
    return priority_ref_label(record)


@register.filter
def crm_project_label(record, lookups=None):
    return project_ref_label(record)


@register.filter
def crm_user_label(record, lookups=None):
    return user_ref_label(record)


@register.filter
def crm_service_type_label(record, lookups=None):
    return service_type_ref_label(record)


@register.filter
def crm_subject_label(record, lookups=None):
    return subject_ref_label(record)


@register.filter
def crm_task_label(record, lookups=None):
    return task_ref_label(record)


@register.filter
def crm_template_label(record, lookups=None):
    return template_ref_label(record)


@register.filter
def crm_requester_label(requester, lookups=None):
    return requester_ref_label(requester)


@register.filter
def crm_move_status_label(entry, direction='from'):
    return move_status_label(entry, direction=direction)


@register.filter
def crm_moved_by_label(entry, lookups=None):
    return moved_by_label(entry)
