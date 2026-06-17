from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.views.kanban_helpers import build_kanban_context
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from projetos.views._helpers import menu_context


@crm_permission_required("view_board")
def kanban_board(request, board_id):
    client = CrmApiClient(request)
    ctx, errors = build_kanban_context(request, client, board_id)
    for msg in errors:
        messages.error(request, msg)
    if ctx is None:
        return redirect("projetos:lista_boards")

    board = ctx["board"]
    return render(
        request,
        "projetos/templates_boards/kanban_board.html",
        {
            "site_title": f"Projetos — Kanban — {board.get('name') or board_id}",
            "kanban_back_url": "projetos:lista_boards",
            "kanban_access_url": "projetos:acesso_board",
            "kanban_columns_url": "projetos:colunas_board",
            **ctx,
            **menu_context("projetos_boards", "kanban"),
        },
    )
