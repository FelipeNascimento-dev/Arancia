from crm_api.client import CrmApiClient, parse_list_response


def list_tasks(client: CrmApiClient, *, skip=0, limit=50, **filters):
    params = {"skip": skip, "limit": limit}
    for key, value in filters.items():
        if value not in (None, ""):
            params[key] = value
    data = client.get("/tasks/", params=params)
    return parse_list_response(data)


def list_my_tasks(client: CrmApiClient, *, skip=0, limit=50, **filters):
    params = {"skip": skip, "limit": limit}
    for key, value in filters.items():
        if value not in (None, ""):
            params[key] = value
    data = client.get("/tasks/my/", params=params)
    return parse_list_response(data)


def get_task(client: CrmApiClient, task_id):
    return client.get(f"/tasks/{task_id}")


def create_task(client: CrmApiClient, payload):
    return client.post("/tasks/", json=payload)


def update_task(client: CrmApiClient, task_id, payload):
    return client.patch(f"/tasks/{task_id}", json=payload)


def delete_task(client: CrmApiClient, task_id):
    return client.delete(f"/tasks/{task_id}")


def move_task(client: CrmApiClient, task_id, payload):
    return client.patch(f"/tasks/{task_id}/move", json=payload)


def get_move_history(client: CrmApiClient, task_id):
    data = client.get(f"/tasks/{task_id}/move-history")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def list_subtasks(client: CrmApiClient, task_id):
    data = client.get(f"/tasks/{task_id}/subtasks")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def create_subtask(client: CrmApiClient, task_id, payload):
    return client.post(f"/tasks/{task_id}/subtasks", json=payload)


def list_links(client: CrmApiClient, task_id):
    data = client.get(f"/tasks/{task_id}/links")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def create_link(client: CrmApiClient, task_id, payload):
    return client.post(f"/tasks/{task_id}/links", json=payload)


def delete_link(client: CrmApiClient, task_id, link_id):
    return client.delete(f"/tasks/{task_id}/links/{link_id}")


def list_assignees(client: CrmApiClient, task_id):
    data = client.get(f"/tasks/{task_id}/assignees")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def add_assignee(client: CrmApiClient, task_id, payload):
    return client.post(f"/tasks/{task_id}/assignees", json=payload)


def update_assignee(client: CrmApiClient, task_id, assignee_id, payload):
    return client.patch(f"/tasks/{task_id}/assignees/{assignee_id}", json=payload)


def remove_assignee(client: CrmApiClient, task_id, assignee_id):
    return client.delete(f"/tasks/{task_id}/assignees/{assignee_id}")


def list_watchers(client: CrmApiClient, task_id):
    data = client.get(f"/tasks/{task_id}/watchers")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def watch_task(client: CrmApiClient, task_id):
    return client.post(f"/tasks/{task_id}/watch")


def remove_watcher(client: CrmApiClient, task_id, watcher_id):
    return client.delete(f"/tasks/{task_id}/watchers/{watcher_id}")


def add_comment(client: CrmApiClient, task_id, payload):
    return client.post(f"/tasks/{task_id}/comments", json=payload)


def list_attachments(client: CrmApiClient, task_id):
    data = client.get(f"/tasks/{task_id}/attachments")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or []


def upload_attachment(client: CrmApiClient, task_id, *, files, data=None):
    return client.upload(f"/tasks/{task_id}/attachments", files=files, data=data)


def delete_attachment(client: CrmApiClient, task_id, attachment_id):
    return client.delete(f"/tasks/{task_id}/attachments/{attachment_id}")
