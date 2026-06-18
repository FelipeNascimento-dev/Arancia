from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import RecurrenceEditForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import recurrence_edit_payload
from crm_api.services import recurrences as recurrences_service
from crm_api.payloads import parse_rrule
from crm.helpers.date_format import format_datetime_br
from crm.views.views_tasks._helpers import load_board_lookups, menu_context


def _recurrence_initial(recurrence):
    if not recurrence:
        return {}
    freq = recurrence.get("frequency") or recurrence.get("recurrence_frequency")
    interval = recurrence.get("interval") or recurrence.get("recurrence_interval") or 1
    rrule = recurrence.get("rrule")
    if not freq and rrule:
        freq, interval = parse_rrule(rrule)
    return {
        "title": recurrence.get("title"),
        "description": recurrence.get("description"),
        "board_id": recurrence.get("board_id")
        or (recurrence.get("board") or {}).get("id"),
        "status_id": recurrence.get("status_id")
        or (recurrence.get("status") or {}).get("id"),
        "priority_id": recurrence.get("priority_id")
        or (recurrence.get("priority") or {}).get("id"),
        "service_type_id": recurrence.get("service_type_id")
        or (recurrence.get("service_type") or {}).get("id"),
        "project_id": recurrence.get("project_id")
        or (recurrence.get("project") or {}).get("id"),
        "customer_gai_id": recurrence.get("customer_gai_id")
        or (recurrence.get("customer") or {}).get("gai_id"),
        "scheduled_start_at": recurrence.get("start_at") or recurrence.get("scheduled_start_at"),
        "recurrence_frequency": freq,
        "recurrence_interval": interval,
        "recurrence_end_at": recurrence.get("end_at") or recurrence.get("recurrence_end_at"),
        "is_active": recurrence.get("is_active", True),
    }


@crm_permission_required("view_task_recurrence")
def form_recorrencia(request, recurrence_id):
    client = CrmApiClient(request)
    lookups = load_board_lookups(client)
    recurrence = None
    runs = []

    try:
        recurrence = recurrences_service.get_recurrence(client, recurrence_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:lista_recorrencias")

    form = RecurrenceEditForm(
        lookups=lookups,
        initial=_recurrence_initial(recurrence),
    )

    if request.method == "POST" and "edit_recurrence" in request.POST:
        if not request.user.has_perm("crm.change_task_recurrence"):
            messages.error(request, "Você não tem permissão para editar recorrências.")
            return redirect("crm:form_recorrencia", recurrence_id=recurrence_id)
        form = RecurrenceEditForm(request.POST, lookups=lookups)
        if form.is_valid():
            try:
                recurrences_service.update_recurrence(
                    client,
                    recurrence_id,
                    recurrence_edit_payload(form.cleaned_data),
                )
                messages.success(request, "Recorrência atualizada com sucesso!")
                return redirect("crm:form_recorrencia", recurrence_id=recurrence_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao salvar. Verifique os campos.")

    elif request.method == "POST" and "delete_recurrence" in request.POST:
        if request.user.has_perm("crm.delete_task_recurrence"):
            try:
                recurrences_service.delete_recurrence(client, recurrence_id)
                messages.success(request, "Recorrência excluída.")
                return redirect("crm:lista_recorrencias")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:form_recorrencia", recurrence_id=recurrence_id)

    try:
        runs, _ = recurrences_service.list_runs(client, recurrence_id, limit=50)
        runs = [
            {
                **run,
                "display_executed_at": format_datetime_br(
                    run.get("executed_at") or run.get("created_at"),
                    default="-",
                ),
            }
            for run in runs
            if isinstance(run, dict)
        ]
    except CrmApiError:
        runs = []

    return render(
        request,
        "crm/templates_tasks/form_recorrencia.html",
        {
            "site_title": f"CRM — Recorrência {recurrence_id}",
            "form": form,
            "recurrence": recurrence,
            "recurrence_id": recurrence_id,
            "runs": runs,
            **menu_context("projetos_tasks", "recorrencias"),
        },
    )
