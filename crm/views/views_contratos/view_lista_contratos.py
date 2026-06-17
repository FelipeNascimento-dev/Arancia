from django.contrib import messages
from django.shortcuts import render

from crm.decorators import crm_permission_required
from crm.helpers.api_display import enrich_contract
from crm.views.views_contratos._helpers import contract_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import contracts as contracts_service


@crm_permission_required("view_contract")
def lista_contratos(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    pagination = build_api_pagination(request, [])
    items = []

    try:
        raw_items, total = contracts_service.list_contracts(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
        )
        items = [enrich_contract(item) for item in raw_items]
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_contratos/lista_contratos.html",
        {
            "site_title": "CRM — Contratos",
            "items": items,
            "pagination": pagination,
            "q": q,
            "current_parent_menu": "crm",
            "current_menu": "crm_contratos",
            "current_submenu": "lista",
        },
    )
