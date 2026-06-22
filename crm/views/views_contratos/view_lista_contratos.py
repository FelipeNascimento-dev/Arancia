from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from crm.decorators import crm_permission_required
from crm.forms import ContractForm
from crm.helpers.api_display import enrich_contract, service_types_for_config
from crm.views.views_contratos._helpers import contract_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.payloads import contract_api_payload
from crm_api.services import contracts as contracts_service
from crm_api.services.lookups import get_crm_lookups


@crm_permission_required("view_contract")
def lista_contratos(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    pagination = build_api_pagination(request, [])
    items = []
    lookups = contract_lookups(client)
    form = ContractForm(lookups=lookups, nome_form="Novo Contrato")
    show_create_modal = False
    all_service_types = []

    try:
        crm = get_crm_lookups(client) or {}
        if isinstance(crm, dict):
            all_service_types = crm.get("service_types") or []
    except CrmApiError:
        pass

    if request.method == "POST" and "create_contract" in request.POST:
        if not request.user.has_perm("crm.add_contract"):
            messages.error(request, "Você não tem permissão para criar contratos.")
            return redirect("crm:lista_contratos")
        gai_id = request.POST.get("client_gai_id")
        lookups = contract_lookups(client, client_gai_id=gai_id)
        form = ContractForm(request.POST, lookups=lookups, nome_form="Novo Contrato")
        show_create_modal = True
        if form.is_valid():
            try:
                created = contracts_service.create_contract(
                    client,
                    contract_api_payload(form.cleaned_data, is_create=True),
                )
                messages.success(request, "Contrato criado com sucesso!")
                new_id = (created or {}).get("id")
                if new_id:
                    return redirect(f"{reverse('crm:lista_contratos')}?contract={new_id}")
                return redirect("crm:lista_contratos")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar contrato. Verifique os campos.")

    try:
        raw_items, total = contracts_service.list_contracts(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
        )
        items = [enrich_contract(item) for item in raw_items]
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    open_contract = request.GET.get("contract", "").strip()
    open_edit = request.GET.get("edit", "").strip()

    return render(
        request,
        "crm/templates_contratos/lista_contratos.html",
        {
            "site_title": "CRM — Contratos",
            "items": items,
            "pagination": pagination,
            "q": q,
            "form": form,
            "show_create_modal": show_create_modal,
            "list_config": {
                "urls": {
                    "get_contract": reverse(
                        "crm:ajax_get_contract",
                        kwargs={"contract_id": "0"},
                    ).replace("/0/", "/{id}/"),
                    "update_contract": reverse(
                        "crm:ajax_update_contract",
                        kwargs={"contract_id": "0"},
                    ).replace("/0/", "/{id}/"),
                    "detail_contract": reverse(
                        "crm:detalhe_contrato",
                        kwargs={"contract_id": "0"},
                    ).replace("/0/", "/{id}/"),
                },
                "service_types": service_types_for_config(all_service_types),
                "perms": {
                    "change": request.user.has_perm("crm.change_contract"),
                },
                "open_contract": open_contract or None,
                "open_edit": open_edit or None,
            },
            "current_parent_menu": "crm",
            "current_menu": "crm_contratos",
            "current_submenu": "lista",
        },
    )
