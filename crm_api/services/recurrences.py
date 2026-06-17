from crm_api.client import CrmApiClient, parse_list_response


def list_recurrences(client: CrmApiClient, *, skip=0, limit=50, **filters):
    params = {"skip": skip, "limit": limit}
    for key, value in filters.items():
        if value not in (None, ""):
            params[key] = value
    data = client.get("/task-recurrences/", params=params)
    return parse_list_response(data)


def get_recurrence(client: CrmApiClient, recurrence_id):
    return client.get(f"/task-recurrences/{recurrence_id}")


def create_recurrence(client: CrmApiClient, payload):
    return client.post("/task-recurrences/", json=payload)


def update_recurrence(client: CrmApiClient, recurrence_id, payload):
    return client.patch(f"/task-recurrences/{recurrence_id}", json=payload)


def delete_recurrence(client: CrmApiClient, recurrence_id):
    return client.delete(f"/task-recurrences/{recurrence_id}")


def generate_due_tasks(client: CrmApiClient):
    return client.post("/internal/scheduler/generate-due-tasks")


def run_scheduler_for_template(template_id):
    """Dispara scheduler (Bearer) e retorna task_id gerada para o template, se houver."""
    from crm_api.client import CrmApiClient

    client = CrmApiClient(scheduler=True)
    result = generate_due_tasks(client) or {}
    template_key = str(template_id)
    for item in result.get("results") or []:
        if str(item.get("template_id")) == template_key and item.get("task_id"):
            return item["task_id"]
    return None


def list_runs(client: CrmApiClient, recurrence_id, *, skip=0, limit=50):
    params = {"skip": skip, "limit": limit}
    data = client.get(f"/task-recurrences/{recurrence_id}/runs", params=params)
    return parse_list_response(data)
