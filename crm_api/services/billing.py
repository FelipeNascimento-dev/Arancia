from crm_api.client import CrmApiClient, parse_list_response


def list_billing(client: CrmApiClient, *, skip=0, limit=10, q=None, status=None):
    params = {"skip": skip, "limit": limit}
    if q:
        params["q"] = q
    if status:
        params["status"] = status
    data = client.get("/billing/", params=params)
    return parse_list_response(data)


def get_billing(client: CrmApiClient, billing_id):
    return client.get(f"/billing/{billing_id}")


def billing_summary(client: CrmApiClient):
    return client.get("/billing/summary")


def create_billing(client: CrmApiClient, payload):
    return client.post("/billing/", json=payload)


def update_billing(client: CrmApiClient, billing_id, payload):
    return client.patch(f"/billing/{billing_id}", json=payload)
