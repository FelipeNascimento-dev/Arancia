from django.shortcuts import render

from crm.decorators import crm_module_required
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.lookups import customer_label, fetch_crm_lookups
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)

CRM_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_alerts',
}


@crm_module_required
def alert_list(request):
    """GET /alerts/ — listagem de alertas de contrato."""
    if get_user_gai_id(request.user) is None:
        return render(request, 'crm/alerts/list.html', {
            'site_title': 'CRM — Alertas',
            'missing_gai': True,
            **CRM_MENU,
        })

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
        for item in alerts:
            item['customer_label'] = customer_label(lookups, item.get('customer_gai_id'))
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
