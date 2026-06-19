from crm_api.client import CrmApiClient


def get_dashboard_summary(client: CrmApiClient):
    """GET /dashboard/summary — billing, alerts and my_tasks widgets."""
    return client.get("/dashboard/summary")
