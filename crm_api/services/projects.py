from crm_api.client import CrmApiClient, parse_list_response


def list_projects(client: CrmApiClient, *, skip=0, limit=50, q=None):
    params = {"skip": skip, "limit": limit}
    if q:
        params["q"] = q
    data = client.get("/projects/", params=params)
    return parse_list_response(data)


def get_project(client: CrmApiClient, project_id):
    return client.get(f"/projects/{project_id}")


def create_project(client: CrmApiClient, payload):
    return client.post("/projects/", json=payload)


def update_project(client: CrmApiClient, project_id, payload):
    return client.patch(f"/projects/{project_id}", json=payload)


def delete_project(client: CrmApiClient, project_id):
    return client.delete(f"/projects/{project_id}")


def list_members(client: CrmApiClient, project_id):
    data = client.get(f"/projects/{project_id}/members")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def add_member(client: CrmApiClient, project_id, payload):
    return client.post(f"/projects/{project_id}/members", json=payload)


def update_member(client: CrmApiClient, project_id, member_id, payload):
    return client.patch(f"/projects/{project_id}/members/{member_id}", json=payload)


def remove_member(client: CrmApiClient, project_id, member_id):
    return client.delete(f"/projects/{project_id}/members/{member_id}")


def list_project_tasks(client: CrmApiClient, project_id, *, skip=0, limit=50, **filters):
    params = {"skip": skip, "limit": limit}
    for key, value in filters.items():
        if value not in (None, ""):
            params[key] = value
    data = client.get(f"/projects/{project_id}/tasks", params=params)
    return parse_list_response(data)
