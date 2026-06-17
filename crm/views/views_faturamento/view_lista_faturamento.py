from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse

from crm.decorators import crm_permission_required
from crm.forms import BillingFilterForm
from crm.helpers.api_display import billing_to_json, enrich_billing
from crm.helpers.dashboard import build_summary_cards
from crm.views.views_contratos._helpers import (
    contract_client_gai_id,
    contract_option_label,
)
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import billing as billing_service
from crm_api.services import contracts as contracts_service
from crm_api.services import clients as clients_service

BILLING_LIST_SKIP_KEYS = frozenset({"items", "detail"})


def _billing_lookups(client):
    lookups = {"clients": [], "contracts": []}
    try:
        clients, _ = clients_service.list_clients(client, limit=200)
        lookups["clients"] = clients
    except CrmApiError:
        pass
    try:
        contracts, _ = contracts_service.list_contracts(client, limit=200)
        lookups["contracts"] = contracts
    except CrmApiError:
        pass
    return lookups


def _lookup_options(lookups):
    clients = []
    for client in lookups.get("clients", []):
        gai_id = client.get("gai_id") or client.get("id")
        if gai_id is None:
            continue
        clients.append({
            "id": gai_id,
            "label": client.get("nome") or client.get("name") or str(gai_id),
        })

    contracts = []
    for contract in lookups.get("contracts", []):
        contract_id = contract.get("id")
        if contract_id is None:
            continue
        contracts.append({
            "id": str(contract_id),
            "label": contract_option_label(contract),
            "client_gai_id": contract_client_gai_id(contract),
        })
    return clients, contracts


@crm_permission_required("view_billing")
def lista_faturamento(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    pagination = build_api_pagination(request, [])
    items = []
    summary = {}
    summary_cards = []
    lookups = _billing_lookups(client)

    try:
        summary = billing_service.billing_summary(client) or {}
        summary_cards = build_summary_cards(summary, skip_keys=BILLING_LIST_SKIP_KEYS)
    except CrmApiError:
        summary = {}

    try:
        raw_items, total = billing_service.list_billing(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
            status=status or None,
        )
        items = [enrich_billing(item) for item in raw_items]
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    filter_form = BillingFilterForm(
        initial={"q": q, "status": status},
        nome_form="Consulta de Faturamento",
    )
    client_options, contract_options = _lookup_options(lookups)

    list_config = {
        "items": {
            str(item["id"]): billing_to_json(item)
            for item in items
            if item.get("id") not in (None, "")
        },
        "clients": client_options,
        "contracts": contract_options,
        "urls": {
            "get": reverse("crm:ajax_get_billing", kwargs={"billing_id": "{id}"}),
            "create": reverse("crm:ajax_create_billing"),
            "update": reverse("crm:ajax_update_billing", kwargs={"billing_id": "{id}"}),
            "contract_detail": reverse(
                "crm:detalhe_contrato",
                kwargs={"contract_id": "{id}"},
            ),
        },
    }

    return render(
        request,
        "crm/templates_faturamento/lista_faturamento.html",
        {
            "site_title": "CRM — Faturamento",
            "items": items,
            "pagination": pagination,
            "q": q,
            "status": status,
            "summary": summary,
            "summary_cards": summary_cards,
            "filter_form": filter_form,
            "list_config": list_config,
            "current_parent_menu": "crm",
            "current_menu": "crm_faturamento",
        },
    )
