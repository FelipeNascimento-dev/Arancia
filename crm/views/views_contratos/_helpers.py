from crm_api.exceptions import CrmApiError
from crm_api.services import clients as clients_service
from crm_api.services.lookups import get_crm_lookups


def contract_lookups(client):
    lookups = {"clients": [], "service_types": []}
    try:
        clients, _ = clients_service.list_clients(client, limit=200)
        lookups["clients"] = clients
    except CrmApiError:
        pass
    try:
        crm = get_crm_lookups(client) or {}
        if isinstance(crm, dict):
            lookups["service_types"] = crm.get("service_types") or []
    except CrmApiError:
        pass
    return lookups
