from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone

from crm.decorators import crm_permission_required
from crm.forms import UnifiedTaskForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import recurrence_payload, task_payload
from crm_api.services import recurrences as recurrences_service
from crm_api.services import tasks as tasks_service
from crm.views.views_tasks._helpers import load_task_lookups, menu_context


def _can_create_on_board(client, board_id):
    if not board_id:
        return True
    try:
        access = client.get(f"/boards/{board_id}/access/me")
        return access.get("can_create_tasks", True)
    except CrmApiError:
        return True


@crm_permission_required("view_task")
def form_task(request):
    if not request.user.has_perm("crm.add_task") and not request.user.has_perm(
        "crm.add_task_recurrence"
    ):
        raise PermissionDenied

    client = CrmApiClient(request)
    lookups = load_task_lookups(client)
    form = UnifiedTaskForm(lookups=lookups, nome_form="Nova Task")

    if request.method == "POST" and "create_task" in request.POST:
        form = UnifiedTaskForm(request.POST, lookups=lookups, nome_form="Nova Task")
        is_recurring = request.POST.get("is_recurring") == "on"

        if is_recurring and not request.user.has_perm("crm.add_task_recurrence"):
            messages.error(request, "Você não tem permissão para criar recorrências.")
            return redirect("crm:form_task")

        if not is_recurring and not request.user.has_perm("crm.add_task"):
            messages.error(request, "Você não tem permissão para criar tasks.")
            return redirect("crm:form_task")

        if form.is_valid():
            board_id = form.cleaned_data.get("board_id")
            if not _can_create_on_board(client, board_id):
                messages.error(request, "Você não tem permissão para criar tasks neste board.")
            else:
                try:
                    if is_recurring:
                        created = recurrences_service.create_recurrence(
                            client, recurrence_payload(form.cleaned_data),
                        )
                        recurrence_id = (created or {}).get("id")
                        start_at = form.cleaned_data.get("scheduled_start_at")
                        task_id = None
                        if start_at and start_at <= timezone.now() and recurrence_id:
                            task_id = recurrences_service.run_scheduler_for_template(
                                recurrence_id,
                            )
                        if task_id:
                            messages.success(
                                request,
                                "Recorrência criada. Primeira ocorrência já disponível no Kanban.",
                            )
                            return redirect("crm:detalhe_task", task_id=task_id)
                        messages.success(request, "Template de recorrência criado com sucesso!")
                        if recurrence_id:
                            return redirect("crm:form_recorrencia", recurrence_id=recurrence_id)
                        return redirect("crm:lista_tasks")

                    created = tasks_service.create_task(
                        client, task_payload(form.cleaned_data),
                    )
                    task_id = (created or {}).get("id")
                    messages.success(request, "Task criada com sucesso!")
                    if task_id:
                        return redirect("crm:detalhe_task", task_id=task_id)
                    return redirect("crm:lista_tasks")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar task. Verifique os campos.")

    board_id = request.GET.get("board_id")
    if board_id and not request.method == "POST":
        form.fields["board_id"].initial = board_id

    return render(
        request,
        "crm/templates_tasks/form_task.html",
        {
            "site_title": "CRM — Nova Task",
            "form": form,
            "botao_texto": "Criar",
            "can_add_recurrence": request.user.has_perm("crm.add_task_recurrence"),
            **menu_context("projetos_tasks", "novo"),
        },
    )
