from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import BoardColumnForm, ComercialTaskModalForm
from crm.views.kanban_helpers import build_kanban_context
from crm.views.views_comercial.comercial_column_helpers import (
    handle_column_post,
    load_board_columns,
)
from crm.views.views_tasks._helpers import (
    load_board_lookups,
    load_task_lookups,
    menu_context,
    resolve_comercial_board_id,
)
from crm.views.views_tasks.view_form_task import _can_create_on_board
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import task_payload
from crm_api.services import tasks as tasks_service


def _resolve_comercial_board_id(request, client):
    try:
        return resolve_comercial_board_id(client)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return None


def _columns_ui_state_from_request(request):
    return {
        "manage_columns_modal": request.GET.get("manage_columns") == "1",
        "create_column_modal": False,
        "edit_column_modal": False,
        "edit_column_post": None,
    }


@crm_permission_required("view_board")
def kanban_comercial(request):
    client = CrmApiClient(request)
    board_id = _resolve_comercial_board_id(request, client)
    if board_id is None:
        return redirect("crm:dashboard")

    lookups = load_task_lookups(client)
    board_lookups = load_board_lookups(client)
    task_form = ComercialTaskModalForm(lookups=lookups, board_id=board_id)
    column_form = BoardColumnForm(lookups=board_lookups)
    columns_ui_state = _columns_ui_state_from_request(request)
    board_columns = []

    column_result = handle_column_post(
        request, client, board_id, board_lookups, column_form,
    )
    column_form = column_result["column_form"]
    if column_result["ui_state"]["manage_columns_modal"]:
        columns_ui_state = column_result["ui_state"]
    if column_result["redirect"]:
        return redirect("crm:kanban_comercial")

    if request.user.has_perm("crm.manage_board_columns"):
        try:
            board_columns = load_board_columns(client, board_id, board_lookups)
        except CrmApiError as exc:
            messages.error(request, crm_error_message_pt(exc))

    if request.method == "POST" and "create_task" in request.POST:
        if not request.user.has_perm("crm.add_task"):
            messages.error(request, "Você não tem permissão para criar tasks.")
            return redirect("crm:kanban_comercial")

        task_form = ComercialTaskModalForm(
            request.POST, lookups=lookups, board_id=board_id,
        )
        if not _can_create_on_board(request, board_id):
            messages.error(request, "Você não tem permissão para criar tasks neste board.")
            return redirect("crm:kanban_comercial")

        if task_form.is_valid():
            try:
                created = tasks_service.create_task(
                    client, task_payload(task_form.cleaned_data),
                )
                messages.success(request, "Task criada com sucesso!")
                task_id = (created or {}).get("id")
                if task_id:
                    return redirect("crm:detalhe_task", task_id=task_id)
                return redirect("crm:kanban_comercial")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar task. Verifique os campos.")

    ctx, errors = build_kanban_context(request, client, board_id)
    for msg in errors:
        messages.error(request, msg)
    if ctx is None:
        return redirect("crm:dashboard")

    return render(
        request,
        "crm/templates_comercial/kanban_comercial.html",
        {
            "site_title": "CRM — Projeto CRM Comercial",
            "task_form": task_form,
            "column_form": column_form,
            "board_columns": board_columns,
            "columns_ui_state": columns_ui_state,
            "comercial_page": "kanban",
            **ctx,
            **menu_context("crm_comercial", "kanban", parent_menu="crm"),
        },
    )
