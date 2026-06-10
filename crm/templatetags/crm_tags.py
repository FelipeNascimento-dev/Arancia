from django import template

register = template.Library()


from crm.decorators import (
    user_has_any_crm_perm,
    user_has_crm_commercial_perm,
    user_has_projects_perm,
)


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
