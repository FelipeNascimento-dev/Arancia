from crm.helpers.api_display import (
    enrich_contract,
    service_type_option_label,
    service_types_for_gai,
)
from crm.helpers.lookup_cache import get_cached_lookup_for_client
from crm_api.exceptions import CrmApiError
from crm_api.services import clients as clients_service
from crm_api.services.lookups import get_crm_lookups


def contract_client_gai_id(contract):
    if not isinstance(contract, dict):
        return None
    customer = contract.get("customer") or {}
    for key in ("client_gai_id", "customer_gai_id"):
        value = contract.get(key)
        if value not in (None, ""):
            return value
    for key in ("gai_id", "id"):
        value = customer.get(key)
        if value not in (None, ""):
            return value
    return None


def contract_option_label(contract):
    """Rótulo legível para selects — nunca exibe UUID bruto."""
    enriched = enrich_contract(contract or {})
    numero = enriched.get("display_numero") or ""
    titulo = enriched.get("display_titulo") or ""
    customer = enriched.get("display_customer") or ""

    if numero and titulo:
        return f"{numero} — {titulo}"
    if titulo:
        return titulo
    if numero:
        return str(numero)
    if customer:
        return f"Contrato — {customer}"
    return "Contrato sem identificação"


def filter_contracts_for_gai(contracts, gai_id):
    if gai_id in (None, ""):
        return contracts or []
    gai_key = str(gai_id)
    filtered = []
    for contract in contracts or []:
        client_id = contract_client_gai_id(contract)
        if client_id in (None, "") or str(client_id) == gai_key:
            filtered.append(contract)
    return filtered


def _contract_lookups(client, *, client_gai_id=None):
    lookups = {"clients": [], "service_types": []}
    try:
        clients, _ = clients_service.list_clients(client, limit=200)
        lookups["clients"] = clients
    except CrmApiError:
        pass
    try:
        crm = get_crm_lookups(client) or {}
        if isinstance(crm, dict):
            service_types = crm.get("service_types") or []
            lookups["service_types"] = service_types_for_gai(
                service_types,
                client_gai_id,
            )
    except CrmApiError:
        pass
    return lookups


def contract_lookups(client, *, client_gai_id=None):
    cache_key = f"contract_lookups:{client_gai_id or 'all'}"
    return get_cached_lookup_for_client(
        client,
        cache_key,
        lambda: _contract_lookups(client, client_gai_id=client_gai_id),
    )


def service_type_choices(service_types):
    choices = [("", "---------")]
    for item in service_types or []:
        item_id = item.get("id") if isinstance(item, dict) else None
        label = service_type_option_label(item)
        if item_id is not None:
            choices.append((item_id, label or str(item_id)))
    return choices
