from crm_api.client import CrmApiClient, parse_list_response


def list_service_types(client: CrmApiClient, *, skip=0, limit=200):
    params = {"skip": skip, "limit": limit}
    data = client.get("/service-types", params=params)
    return parse_list_response(data)


def create_service_type(client: CrmApiClient, payload):
    return client.post("/service-types", json=payload)


def update_service_type(client: CrmApiClient, item_id, payload):
    return client.patch(f"/service-types/{item_id}", json=payload)


def delete_service_type(client: CrmApiClient, item_id):
    return client.delete(f"/service-types/{item_id}")


def list_priorities(client: CrmApiClient, *, skip=0, limit=200):
    params = {"skip": skip, "limit": limit}
    data = client.get("/prioritys", params=params)
    return parse_list_response(data)


def create_priority(client: CrmApiClient, payload):
    return client.post("/prioritys", json=payload)


def update_priority(client: CrmApiClient, item_id, payload):
    return client.patch(f"/prioritys/{item_id}", json=payload)


def delete_priority(client: CrmApiClient, item_id):
    return client.delete(f"/prioritys/{item_id}")


def list_status_tasks(client: CrmApiClient, *, skip=0, limit=200):
    params = {"skip": skip, "limit": limit}
    data = client.get("/status-tasks", params=params)
    return parse_list_response(data)


def create_status_task(client: CrmApiClient, payload):
    return client.post("/status-tasks", json=payload)


def update_status_task(client: CrmApiClient, item_id, payload):
    return client.patch(f"/status-tasks/{item_id}", json=payload)


def delete_status_task(client: CrmApiClient, item_id):
    return client.delete(f"/status-tasks/{item_id}")


def reorder_status_tasks(client: CrmApiClient, payload):
    return client.patch("/status-tasks/reorder", json=payload)
