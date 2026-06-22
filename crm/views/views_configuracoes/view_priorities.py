from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import PriorityForm
from crm.helpers.api_display import enrich_priority
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import settings_item_payload
from crm_api.services import settings as settings_service
from crm.views.views_tasks._helpers import menu_context


def _priority_initial(item):
    if not item:
        return {}
    return {
        "name": item.get("name"),
        "color": item.get("color"),
        "sort_order": item.get("sort_order"),
        "is_active": item.get("is_active", True),
    }


@crm_permission_required("view_settings")
def priorities(request):
    client = CrmApiClient(request)
    items = []
    selected = None
    selected_id = request.GET.get("item_id")
    create_form = PriorityForm()
    edit_form = PriorityForm()

    if request.method == "POST" and "create_item" in request.POST:
        if not request.user.has_perm("crm.manage_priorities"):
            messages.error(request, "Sem permissão para criar prioridades.")
            return redirect("crm:priorities")
        create_form = PriorityForm(request.POST)
        if create_form.is_valid():
            try:
                settings_service.create_priority(
                    client, settings_item_payload(create_form.cleaned_data, is_create=True),
                )
                messages.success(request, "Prioridade criada!")
                return redirect("crm:priorities")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar prioridade. Verifique os campos.")

    elif request.method == "POST" and "edit_item" in request.POST:
        item_id = request.POST.get("item_id")
        if item_id and request.user.has_perm("crm.manage_priorities"):
            edit_form = PriorityForm(request.POST)
            if edit_form.is_valid():
                try:
                    settings_service.update_priority(
                        client, item_id, settings_item_payload(edit_form.cleaned_data),
                    )
                    messages.success(request, "Prioridade atualizada.")
                    return redirect(f"{request.path}?item_id={item_id}")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")
                selected_id = item_id

    elif request.method == "POST" and "delete_item" in request.POST:
        item_id = request.POST.get("item_id")
        if item_id and request.user.has_perm("crm.manage_priorities"):
            try:
                settings_service.delete_priority(client, item_id)
                messages.success(request, "Prioridade excluída.")
                return redirect("crm:priorities")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    try:
        raw_items, _ = settings_service.list_priorities(client)
        items = [enrich_priority(item) for item in raw_items]
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    if selected_id:
        for item in items:
            if str(item.get("id")) == str(selected_id):
                selected = item
                if not (request.method == "POST" and "edit_item" in request.POST):
                    edit_form = PriorityForm(initial=_priority_initial(item))
                break

    return render(
        request,
        "crm/templates_configuracoes/priorities.html",
        {
            "site_title": "CRM — Prioridades",
            "items": items,
            "selected": selected,
            "selected_id": selected_id,
            "form": edit_form,
            "create_form": create_form,
            "resource_label": "Prioridades",
            **menu_context("projetos_config", "priorities"),
        },
    )
