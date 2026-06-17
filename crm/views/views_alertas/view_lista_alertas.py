from django.contrib import messages
from django.shortcuts import render

from crm.decorators import crm_permission_required
from crm.helpers.api_display import enrich_alert
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import alerts as alerts_service


@crm_permission_required("view_contract")
def lista_alertas(request):
    client = CrmApiClient(request)
    pagination = build_api_pagination(request, [], limit=20)
    items = []

    try:
        raw_items, total = alerts_service.list_alerts(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
        )
        items = [enrich_alert(item) for item in raw_items]
        pagination = build_api_pagination(request, items, total_items=total, limit=20)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_alertas/lista_alertas.html",
        {
            "site_title": "CRM — Alertas",
            "items": items,
            "pagination": pagination,
            "current_parent_menu": "crm",
            "current_menu": "crm_alertas",
        },
    )
