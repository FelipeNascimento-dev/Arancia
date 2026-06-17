from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.views.kanban_helpers import build_kanban_context
from crm.views.views_tasks._helpers import menu_context
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services import boards as boards_service


def _resolve_comercial_board_id(request, client):
    try:
        return boards_service.get_comercial_board_id(client)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return None


@crm_permission_required("view_board")
def kanban_comercial(request):
    client = CrmApiClient(request)
    board_id = _resolve_comercial_board_id(request, client)
    if board_id is None:
        return redirect("crm:dashboard")

    ctx, errors = build_kanban_context(request, client, board_id)
    for msg in errors:
        messages.error(request, msg)
    if ctx is None:
        return redirect("crm:dashboard")

    board = ctx["board"]
    return render(
        request,
        "crm/templates_comercial/kanban_comercial.html",
        {
            "site_title": "CRM — Projeto CRM Comercial",
            **ctx,
            **menu_context("crm_comercial", "kanban", parent_menu="crm"),
        },
    )
