from crm_api.client import CrmApiClient, parse_list_response


def list_clients(client: CrmApiClient, *, skip=0, limit=10, q=None):
    params = {"skip": skip, "limit": limit}
    if q:
        params["q"] = q
    data = client.get("/clients/", params=params)
    return parse_list_response(data)


def get_client(client: CrmApiClient, gai_id):
    return client.get(f"/clients/{gai_id}")


def create_client(client: CrmApiClient, payload):
    return client.post("/clients/", json=payload)


def update_client(client: CrmApiClient, gai_id, payload):
    return client.patch(f"/clients/{gai_id}", json=payload)


def delete_client(client: CrmApiClient, gai_id):
    return client.delete(f"/clients/{gai_id}")


def add_contact(client: CrmApiClient, gai_id, payload):
    return client.post(f"/clients/{gai_id}/contacts", json=payload)


def add_address(client: CrmApiClient, gai_id, payload):
    return client.post(f"/clients/{gai_id}/addresses", json=payload)
