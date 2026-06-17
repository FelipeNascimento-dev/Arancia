from crm_api.client import CrmApiClient, parse_list_response


def list_alerts(client: CrmApiClient, *, skip=0, limit=50):
    params = {"skip": skip, "limit": limit}
    data = client.get("/alerts/", params=params)
    return parse_list_response(data)


def fire_alert(client: CrmApiClient, alert_id):
    return client.post(f"/alerts/fire/{alert_id}")
