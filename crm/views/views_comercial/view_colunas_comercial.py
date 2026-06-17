from django.contrib import messages
from django.shortcuts import redirect, render

from crm.helpers.api_display import enrich_board, enrich_board_column
from crm.decorators import crm_permission_required
from crm.forms import BoardColumnForm
from crm.views.views_tasks._helpers import load_board_lookups, menu_context
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import board_column_payload
from crm_api.services import boards as boards_service
from crm.views.views_comercial.view_kanban_comercial import _resolve_comercial_board_id


@crm_permission_required("view_board")
def colunas_comercial(request):
    client = CrmApiClient(request)
    board_id = _resolve_comercial_board_id(request, client)
    if board_id is None:
        return redirect("crm:dashboard")

    lookups = load_board_lookups(client)
    board = None
    columns = []
    column_form = BoardColumnForm(lookups=lookups)

    try:
        board = enrich_board(boards_service.get_board(client, board_id))
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:kanban_comercial")

    if request.method == "POST" and "add_column" in request.POST:
        if not request.user.has_perm("crm.manage_board_columns"):
            messages.error(request, "Você não tem permissão para gerenciar colunas.")
            return redirect("crm:colunas_comercial")
        column_form = BoardColumnForm(request.POST, lookups=lookups)
        if column_form.is_valid():
            try:
                boards_service.create_column(
                    client, board_id, board_column_payload(column_form.cleaned_data),
                )
                messages.success(request, "Coluna adicionada!")
                return redirect("crm:colunas_comercial")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "edit_column" in request.POST:
        column_id = request.POST.get("column_id")
        if column_id and request.user.has_perm("crm.manage_board_columns"):
            payload = {
                "name": request.POST.get("name"),
                "status_task_id": request.POST.get("status_task_id"),
                "position": request.POST.get("position"),
            }
            payload = {k: v for k, v in payload.items() if v not in (None, "")}
            try:
                boards_service.update_column(client, board_id, column_id, payload)
                messages.success(request, "Coluna atualizada.")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:colunas_comercial")

    try:
        columns = boards_service.list_columns(client, board_id)
        columns = sorted(
            columns,
            key=lambda c: c.get("position") or c.get("sort_order") or c.get("kanban_position") or 0,
        )
        columns = [enrich_board_column(c, lookups) for c in columns]
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_comercial/colunas_comercial.html",
        {
            "site_title": f"CRM — Colunas — {board.get('name') or board_id}",
            "board": board,
            "board_id": board_id,
            "columns": columns,
            "column_form": column_form,
            "lookups": lookups,
            "comercial_page": "columns",
            **menu_context("crm_comercial", parent_menu="crm"),
        },
    )
