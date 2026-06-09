from .client import CrmApiClient


def fetch_crm_lookups(user):
    """GET /lookups/crm — clientes elegíveis, service_types, boards, etc."""
    return CrmApiClient(user).get('/lookups/crm')


def build_gai_choices(lookups):
    """Monta choices (gai_id, label) a partir de lookups.customers."""
    return build_customer_choices(lookups)


def build_customer_choices(lookups):
    """Choices (gai_id, label) para clientes CRM."""
    customers = (lookups or {}).get('customers') or []
    choices = []
    for item in customers:
        gai_id = item.get('gai_id')
        if gai_id is None:
            continue
        label = item.get('razao_social') or item.get('nome') or f'GAI {gai_id}'
        if item.get('cnpj'):
            label = f'{label} ({item["cnpj"]})'
        choices.append((str(gai_id), label))
    return choices


def build_service_type_choices(lookups):
    """Choices (uuid, label) para tipos de serviço."""
    items = (lookups or {}).get('service_types') or []
    choices = []
    for item in items:
        item_id = item.get('id')
        if not item_id:
            continue
        label = item.get('name') or item.get('code') or str(item_id)
        choices.append((str(item_id), label))
    return choices


def build_contract_choices(contracts):
    """Choices (uuid, label) a partir de listagem de contratos."""
    choices = []
    for item in contracts or []:
        item_id = item.get('id')
        if not item_id:
            continue
        title = item.get('title') or str(item_id)
        gai = item.get('customer_gai_id')
        label = f'{title}' + (f' (GAI {gai})' if gai else '')
        choices.append((str(item_id), label))
    return choices


def customer_label(lookups, gai_id):
    """Retorna label legível para um GAI ou o próprio id."""
    if gai_id is None:
        return '—'
    for value, label in build_customer_choices(lookups):
        if str(value) == str(gai_id):
            return label
    return f'GAI {gai_id}'


def _build_uuid_choices(items, *, label_keys=('name', 'title', 'code')):
    choices = []
    for item in items or []:
        item_id = item.get('id')
        if not item_id:
            continue
        label = None
        for key in label_keys:
            if item.get(key):
                label = item[key]
                break
        choices.append((str(item_id), label or str(item_id)))
    return choices


def build_board_choices(lookups):
    return _build_uuid_choices((lookups or {}).get('boards'))


def build_priority_choices(lookups):
    return _build_uuid_choices((lookups or {}).get('priorities'))


def build_status_choices(lookups):
    return _build_uuid_choices((lookups or {}).get('status_tasks'))


def build_project_choices(lookups):
    return _build_uuid_choices((lookups or {}).get('projects'))


def fetch_team_gais(user):
    """GET /lookups/team-gais — equipes (GAI) para membros de projeto."""
    return CrmApiClient(user).get('/lookups/team-gais')


def fetch_member_lookups(user):
    """GET /lookups/members — usuários e designações elegíveis."""
    return CrmApiClient(user).get('/lookups/members')


def build_team_gai_choices(team_gais):
    choices = []
    for item in team_gais or []:
        gai_id = item.get('team_gai_id') or item.get('gai_id') or item.get('id')
        if gai_id is None:
            continue
        label = item.get('name') or item.get('nome') or f'Equipe {gai_id}'
        choices.append((str(gai_id), label))
    return choices


def build_user_choices(members_lookup):
    choices = []
    for item in (members_lookup or {}).get('users') or []:
        user_id = item.get('id')
        if user_id is None:
            continue
        label = item.get('username') or item.get('full_name') or str(user_id)
        choices.append((str(user_id), label))
    return choices


def build_designation_choices(members_lookup):
    choices = []
    for item in (members_lookup or {}).get('designations') or []:
        des_id = item.get('id')
        if des_id is None:
            continue
        label = item.get('label') or item.get('username') or str(des_id)
        choices.append((str(des_id), label))
    return choices
