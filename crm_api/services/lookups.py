from crm_api.client import CrmApiClient, parse_list_response


def unwrap_lookup_items(data):
    """Normaliza respostas de lookup (lista ou envelope paginado)."""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        items, _ = parse_list_response(data)
        return items
    return []


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


def get_users(client: CrmApiClient):
    return client.get("/lookups/users")


def get_designations(client: CrmApiClient):
    return client.get("/lookups/designations")
