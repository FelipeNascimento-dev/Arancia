from crm_api.client import CrmApiClient


def get_me_context(client):
    return client.get("/me/context")


def validate_context(client):
    return client.post("/auth/validate-context")


def health_check(client):
    return client.health()
