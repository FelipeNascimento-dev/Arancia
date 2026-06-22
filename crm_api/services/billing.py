from crm_api.client import CrmApiClient, parse_list_response
from crm_api.exceptions import CrmApiError, CrmNotFoundError


def list_billing(client: CrmApiClient, *, skip=0, limit=10, q=None, status=None):
    params = {"skip": skip, "limit": limit}
    if q:
        params["q"] = q
    if status:
        params["status"] = status
    data = client.get("/billing/", params=params)
    return parse_list_response(data)


def _find_billing_in_list(client: CrmApiClient, billing_id):
    """Fallback quando a API não expõe GET /billing/{id}."""
    billing_key = str(billing_id)
    skip = 0
    limit = 100
    total = None
    while total is None or skip < total:
        items, total = list_billing(client, skip=skip, limit=limit)
        for item in items:
            item_id = item.get("id")
            if item_id is not None and str(item_id) == billing_key:
                return item
        if not items:
            break
        skip += limit
    raise CrmNotFoundError(
        "Faturamento não encontrado.",
        status_code=404,
        detail="Faturamento não encontrado.",
    )


def get_billing(client: CrmApiClient, billing_id):
    try:
        return client.get(f"/billing/{billing_id}")
    except CrmApiError as exc:
        if getattr(exc, "status_code", None) != 405:
            raise
    return _find_billing_in_list(client, billing_id)


def billing_summary(client: CrmApiClient):
    return client.get("/billing/summary")


def create_billing(client: CrmApiClient, payload):
    return client.post("/billing/", json=payload)


def update_billing(client: CrmApiClient, billing_id, payload):
    return client.patch(f"/billing/{billing_id}", json=payload)
