from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.views.kanban_helpers import build_kanban_context
from crm.views.views_tasks._helpers import menu_context
from crm_api.client import CrmApiClient


@crm_permission_required("view_board")
def kanban_board(request, board_id):
    client = CrmApiClient(request)
    ctx, errors = build_kanban_context(request, client, board_id)
    for msg in errors:
        messages.error(request, msg)
    if ctx is None:
        return redirect("crm:lista_boards")

    board = ctx["board"]
    return render(
        request,
        "crm/templates_boards/kanban_board.html",
        {
            "site_title": f"CRM — Kanban — {board.get('name') or board_id}",
            **ctx,
            **menu_context("crm_tasks", "kanban"),
        },
    )
