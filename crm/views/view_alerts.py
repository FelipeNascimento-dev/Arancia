from django.shortcuts import render

from crm.decorators import crm_module_required
from crm.services.client import CrmApiClient
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.gates import require_gai_or_render
from crm.services.lookups import fetch_crm_lookups
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)

CRM_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_alerts',
}


def _require_gai_or_render(request, template, extra_context=None):
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Alertas',
        menu_context=CRM_MENU,
        extra_context=extra_context,
    )


@crm_module_required
def alert_list(request):
    """GET /alerts/ — listagem de alertas de contrato."""
    blocked = _require_gai_or_render(request, 'crm/alerts/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    client = CrmApiClient(request.user)
    alerts = []
    api_error = None
    lookups = None

    try:
        lookups = fetch_crm_lookups(request.user)
    except CrmApiError as exc:
        handle_crm_error(request, exc)

    try:
        raw = client.get('/alerts/', params={'skip': skip, 'limit': limit})
        alerts = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    pagination = build_pagination_context(skip, limit, alerts)
    return render(request, 'crm/alerts/list.html', {
        'site_title': 'CRM — Alertas',
        'alerts': alerts,
        'pagination': pagination,
        'api_error': api_error,
        'lookups': lookups,
        **CRM_MENU,
    })
