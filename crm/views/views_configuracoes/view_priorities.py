from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import PriorityForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import settings_item_payload
from crm_api.services import settings as settings_service
from crm.views.views_tasks._helpers import menu_context


@crm_permission_required("view_settings")
def priorities(request):
    client = CrmApiClient(request)
    items = []
    selected = None
    selected_id = request.GET.get("item_id")
    form = PriorityForm()

    if request.method == "POST" and "create_item" in request.POST:
        if not request.user.has_perm("crm.manage_priorities"):
            messages.error(request, "Sem permissão para criar prioridades.")
            return redirect("crm:priorities")
        form = PriorityForm(request.POST)
        if form.is_valid():
            try:
                settings_service.create_priority(
                    client, settings_item_payload(form.cleaned_data),
                )
                messages.success(request, "Prioridade criada!")
                return redirect("crm:priorities")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "edit_item" in request.POST:
        item_id = request.POST.get("item_id")
        if item_id and request.user.has_perm("crm.manage_priorities"):
            payload = {
                "name": request.POST.get("name"),
                "color": request.POST.get("color"),
                "sort_order": request.POST.get("sort_order"),
                "is_active": request.POST.get("is_active") == "on",
            }
            payload = {k: v for k, v in payload.items() if v not in (None, "")}
            try:
                settings_service.update_priority(client, item_id, payload)
                messages.success(request, "Prioridade atualizada.")
                return redirect(f"{request.path}?item_id={item_id}")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

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
        items, _ = settings_service.list_priorities(client)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    if selected_id:
        for item in items:
            if str(item.get("id")) == str(selected_id):
                selected = item
                form = PriorityForm(initial={
                    "name": selected.get("name"),
                    "color": selected.get("color"),
                    "sort_order": selected.get("sort_order"),
                    "is_active": selected.get("is_active", True),
                })
                break

    return render(
        request,
        "crm/templates_configuracoes/priorities.html",
        {
            "site_title": "CRM — Prioridades",
            "items": items,
            "selected": selected,
            "selected_id": selected_id,
            "form": form,
            "resource_label": "Prioridades",
            **menu_context("projetos_config", "priorities"),
        },
    )
