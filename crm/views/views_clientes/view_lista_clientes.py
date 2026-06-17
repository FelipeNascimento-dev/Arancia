from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from crm.helpers.api_display import enrich_client
from crm.decorators import crm_permission_required
from crm.forms import ClientCreateForm
from crm.services.client_gai import ClientGaiGroupNotConfigured, create_client_with_gai
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import clients as clients_service


@crm_permission_required("view_clients")
def lista_clientes(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    pagination = build_api_pagination(request, [])
    items = []
    form = ClientCreateForm()
    show_create_modal = False

    if request.method == "POST" and "create_client" in request.POST:
        if not request.user.has_perm("crm.add_client"):
            messages.error(request, "Você não tem permissão para criar clientes.")
            return redirect("crm:lista_clientes")
        form = ClientCreateForm(request.POST)
        show_create_modal = True
        if form.is_valid():
            try:
                gai, _ = create_client_with_gai(
                    form.cleaned_data,
                    register_in_api=lambda payload: clients_service.create_client(client, payload),
                )
                messages.success(
                    request,
                    f"Cliente {gai.nome} criado com sucesso (GAI {gai.id}).",
                )
                return redirect("crm:lista_clientes")
            except ClientGaiGroupNotConfigured:
                messages.error(
                    request,
                    "Grupo de clientes não configurado (arancia_client / arancia_CUSTOMER).",
                )
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar cliente. Verifique os campos.")

    try:
        items, total = clients_service.list_clients(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
        )
        items = [enrich_client(item) for item in items]
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    open_client = request.GET.get("client", "").strip()
    open_edit = request.GET.get("edit", "").strip()

    return render(
        request,
        "crm/templates_clientes/lista_clientes.html",
        {
            "site_title": "CRM — Clientes",
            "items": items,
            "pagination": pagination,
            "q": q,
            "form": form,
            "show_create_modal": show_create_modal,
            "list_config": {
                "urls": {
                    "get_client": reverse("crm:ajax_get_client", kwargs={"gai_id": 0}).replace("/0/", "/{id}/"),
                    "update_client": reverse("crm:ajax_update_client", kwargs={"gai_id": 0}).replace("/0/", "/{id}/"),
                    "delete_client": reverse("crm:ajax_delete_client", kwargs={"gai_id": 0}).replace("/0/", "/{id}/"),
                },
                "perms": {
                    "change": request.user.has_perm("crm.change_client"),
                    "delete": request.user.has_perm("crm.delete_client"),
                },
                "open_client": open_client or None,
                "open_edit": open_edit or None,
            },
            "current_parent_menu": "crm",
            "current_menu": "crm_clientes",
            "current_submenu": "lista",
        },
    )
