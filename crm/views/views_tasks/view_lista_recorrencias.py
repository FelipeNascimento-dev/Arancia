from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.helpers.api_display import enrich_recurrence
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import recurrences as recurrences_service
from crm.views.views_tasks._helpers import menu_context


@crm_permission_required("view_task_recurrence")
def lista_recorrencias(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    pagination = build_api_pagination(request, [])
    items = []

    try:
        raw_items, total = recurrences_service.list_recurrences(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
        )
        items = [enrich_recurrence(item) for item in raw_items]
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_tasks/lista_recorrencias.html",
        {
            "site_title": "CRM — Recorrências",
            "items": items,
            "pagination": pagination,
            "q": q,
            **menu_context("projetos_tasks", "recorrencias"),
        },
    )
