from crm_api.client import CrmApiClient


def get_crm_lookups(client: CrmApiClient):
    return client.get("/lookups/crm")


def get_column_templates(client: CrmApiClient):
    return client.get("/lookups/column-templates")


def get_team_gais(client: CrmApiClient):
    return client.get("/lookups/team-gais")


def get_groups(client: CrmApiClient):
    return client.get("/lookups/groups")


def get_gais(client: CrmApiClient):
    return client.get("/lookups/gais")
