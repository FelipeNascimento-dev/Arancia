from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import ComercialTaskModalForm
from crm.views.kanban_helpers import build_kanban_context
from crm.views.views_tasks._helpers import load_task_lookups, menu_context
from crm.views.views_tasks.view_form_task import _can_create_on_board
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import task_payload
from crm_api.services import boards as boards_service
from crm_api.services import tasks as tasks_service


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

    lookups = load_task_lookups(client)
    task_form = ComercialTaskModalForm(lookups=lookups, board_id=board_id)

    if request.method == "POST" and "create_task" in request.POST:
        if not request.user.has_perm("crm.add_task"):
            messages.error(request, "Você não tem permissão para criar tasks.")
            return redirect("crm:kanban_comercial")

        task_form = ComercialTaskModalForm(
            request.POST, lookups=lookups, board_id=board_id,
        )
        if not _can_create_on_board(client, board_id):
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
            "comercial_page": "kanban",
            **ctx,
            **menu_context("crm_comercial", "kanban", parent_menu="crm"),
        },
    )
