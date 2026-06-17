from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import ServiceTypeForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import service_type_payload
from crm_api.services import settings as settings_service
from crm.views.views_tasks._helpers import load_task_lookups, menu_context


@crm_permission_required("view_settings")
def service_types(request):
    client = CrmApiClient(request)
    lookups = load_task_lookups(client)
    items = []
    selected = None
    selected_id = request.GET.get("item_id")
    form = ServiceTypeForm(lookups=lookups)

    if request.method == "POST" and "create_item" in request.POST:
        if not request.user.has_perm("crm.manage_service_types"):
            messages.error(request, "Sem permissão para criar tipos de serviço.")
            return redirect("crm:service_types")
        form = ServiceTypeForm(request.POST, lookups=lookups)
        if form.is_valid():
            try:
                settings_service.create_service_type(
                    client, service_type_payload(form.cleaned_data),
                )
                messages.success(request, "Tipo de serviço criado!")
                return redirect("crm:service_types")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "edit_item" in request.POST:
        item_id = request.POST.get("item_id")
        if item_id and request.user.has_perm("crm.manage_service_types"):
            form = ServiceTypeForm(request.POST, lookups=lookups)
            if form.is_valid():
                try:
                    settings_service.update_service_type(
                        client, item_id, service_type_payload(form.cleaned_data),
                    )
                    messages.success(request, "Tipo de serviço atualizado.")
                    return redirect(f"{request.path}?item_id={item_id}")
                except CrmApiError as exc:
                    messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "delete_item" in request.POST:
        item_id = request.POST.get("item_id")
        if item_id and request.user.has_perm("crm.manage_service_types"):
            try:
                settings_service.delete_service_type(client, item_id)
                messages.success(request, "Tipo de serviço excluído.")
                return redirect("crm:service_types")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    try:
        items, _ = settings_service.list_service_types(client)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    if selected_id:
        for item in items:
            if str(item.get("id")) == str(selected_id):
                selected = item
                form = ServiceTypeForm(
                    lookups=lookups,
                    initial={
                        "type": selected.get("type"),
                        "description": selected.get("description"),
                        "status_initial_id": selected.get("status_initial_id")
                        or (selected.get("status_initial") or {}).get("id"),
                        "client_id": selected.get("client_id")
                        or (selected.get("client") or {}).get("gai_id"),
                        "direction": selected.get("direction"),
                    },
                )
                break

    return render(
        request,
        "crm/templates_configuracoes/service_types.html",
        {
            "site_title": "CRM — Tipos de serviço",
            "items": items,
            "selected": selected,
            "selected_id": selected_id,
            "form": form,
            "resource_label": "Tipos de serviço",
            **menu_context("projetos_config", "service_types"),
        },
    )
