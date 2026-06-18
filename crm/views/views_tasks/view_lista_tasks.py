from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import TaskListModalForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import task_payload
from crm_api.services import tasks as tasks_service
from crm.views.views_tasks._helpers import (
    apply_task_assignees,
    fetch_task_list,
    menu_context,
    task_create_data_from_form,
)
from crm.views.views_tasks.view_form_task import _can_create_on_board


@crm_permission_required("view_task")
def lista_tasks(request):
    client = CrmApiClient(request)
    _, items, pagination, filters, lookups, error_message = fetch_task_list(request)
    if error_message:
        messages.error(request, error_message)

    task_form = TaskListModalForm(lookups=lookups)
    show_create_modal = False

    if request.method == "POST" and "create_task" in request.POST:
        if not request.user.has_perm("crm.add_task"):
            raise PermissionDenied

        task_form = TaskListModalForm(request.POST, lookups=lookups)
        show_create_modal = True
        if task_form.is_valid():
            board_id = task_form.cleaned_data.get("board_id")
            if not _can_create_on_board(client, board_id):
                messages.error(request, "Você não tem permissão para criar tasks neste board.")
            else:
                try:
                    created = tasks_service.create_task(
                        client,
                        task_payload(task_create_data_from_form(task_form.cleaned_data)),
                    )
                    task_id = (created or {}).get("id")
                    if task_id and request.user.has_perm("crm.assign_task"):
                        has_assignee = (
                            task_form.cleaned_data.get("assignee_user_id")
                            or task_form.cleaned_data.get("assignee_customer_gai_id")
                        )
                        if has_assignee:
                            apply_task_assignees(client, task_id, task_form.cleaned_data)
                    messages.success(request, "Task criada com sucesso!")
                    if task_id:
                        return redirect("crm:detalhe_task", task_id=task_id)
                    return redirect("crm:lista_tasks")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar task. Verifique os campos.")

    return render(
        request,
        "crm/templates_tasks/lista_tasks.html",
        {
            "site_title": "CRM — Tasks",
            "items": items,
            "pagination": pagination,
            "filters": filters,
            "lookups": lookups,
            "list_mode": "all",
            "task_form": task_form,
            "show_create_modal": show_create_modal,
            **menu_context("projetos_tasks", "lista"),
        },
    )
