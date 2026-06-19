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


def get_board_page(client: CrmApiClient, *, gais_limit=50):
    """GET /lookups/board-page — CRM + GAIs + groups + column templates."""
    return client.get("/lookups/board-page", params={"gais_limit": gais_limit})


def get_billing_lookups_bundle(client: CrmApiClient):
    """GET /lookups/billing — clients + contracts for faturamento pickers."""
    return client.get("/lookups/billing")
