from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import TaskEditForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import task_payload
from crm_api.services import tasks as tasks_service
from crm.views.views_tasks._helpers import load_task_lookups, menu_context, task_display_value


def _lookup_id(task, flat_key, nested_key):
    value = task.get(flat_key)
    if value not in (None, ""):
        return value
    nested = task.get(nested_key) or {}
    if isinstance(nested, dict):
        return nested.get("id")
    return None


def _select_initial(value):
    if value in (None, ""):
        return None
    return str(value)


def _task_edit_initial(task):
    if not task:
        return {}
    requester_ids = task.get("requester_gai_ids") or []
    if not requester_ids and task.get("requesters"):
        requester_ids = [
            str(r.get("gai_id"))
            for r in task["requesters"]
            if r.get("gai_id") is not None
        ]
    customer_gai_id = task.get("customer_gai_id") or (task.get("customer") or {}).get("gai_id")
    return {
        "title": task.get("title"),
        "description": task.get("description"),
        "board_id": _select_initial(_lookup_id(task, "board_id", "board")),
        "status_id": _select_initial(_lookup_id(task, "status_id", "status")),
        "priority_id": _select_initial(_lookup_id(task, "priority_id", "priority")),
        "project_id": _select_initial(_lookup_id(task, "project_id", "project")),
        "customer_gai_id": _select_initial(customer_gai_id),
        "scheduled_start_at": task.get("scheduled_start_at"),
        "scheduled_end_at": task.get("scheduled_end_at"),
        "due_at": task.get("due_at") or task.get("due_date"),
        "requester_gai_ids": [str(i) for i in requester_ids],
    }


@crm_permission_required("view_task")
def edit_task(request, task_id):
    if not request.user.has_perm("crm.change_task"):
        raise PermissionDenied

    client = CrmApiClient(request)
    lookups = load_task_lookups(client)

    try:
        task = tasks_service.get_task(client, task_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:lista_tasks")

    if task.get("recurrence_template_id") or task.get("is_recurring_instance"):
        messages.info(
            request,
            "Esta task é instância de recorrência. Edite o template se necessário.",
        )

    form = TaskEditForm(
        lookups=lookups,
        initial=_task_edit_initial(task),
        nome_form="Editar Task",
    )

    if request.method == "POST" and "edit_task" in request.POST:
        form = TaskEditForm(request.POST, lookups=lookups, nome_form="Editar Task")
        if form.is_valid():
            try:
                tasks_service.update_task(
                    client, task_id, task_payload(form.cleaned_data),
                )
                messages.success(request, "Task atualizada com sucesso!")
                return redirect("crm:detalhe_task", task_id=task_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao salvar. Verifique os campos.")

    recurrence_template_id = task.get("recurrence_template_id")

    return render(
        request,
        "crm/templates_tasks/form_task.html",
        {
            "site_title": f"CRM — Editar — {task_display_value(task, 'title', default=task_id)}",
            "form": form,
            "botao_texto": "Salvar",
            "is_edit": True,
            "task_id": task_id,
            "recurrence_template_id": recurrence_template_id,
            **menu_context("projetos_tasks", "editar"),
        },
    )
