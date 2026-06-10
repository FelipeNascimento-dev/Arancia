from .client import CrmApiClient


def parse_customer_gai_id(value):
    if value is None or value == '':
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _lookup_params(customer_gai_id=None):
    gai_id = parse_customer_gai_id(customer_gai_id)
    if gai_id is None:
        return None
    return {'customer_gai_id': gai_id}


def fetch_crm_lookups(user, customer_gai_id=None):
    """GET /lookups/crm — clientes elegíveis, service_types, boards, etc."""
    params = _lookup_params(customer_gai_id)
    return CrmApiClient(user).get('/lookups/crm', params=params)


def fetch_service_types(user, *, customer_gai_id=None, skip=0, limit=100):
    """GET /service-types/ — tipos de serviço filtrados por GAI cliente."""
    params = {'skip': skip, 'limit': limit}
    gai_params = _lookup_params(customer_gai_id)
    if gai_params:
        params.update(gai_params)
    return CrmApiClient(user).get('/service-types/', params=params)


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


def build_service_type_choices(lookups, customer_gai_id=None):
    """Choices (id int, label) para tipos de serviço (schema order_types)."""
    items = (lookups or {}).get('service_types') or []
    gai_filter = parse_customer_gai_id(customer_gai_id)
    choices = []
    for item in items:
        item_id = item.get('id')
        if item_id is None:
            continue
        if gai_filter is not None:
            item_gai = item.get('client_id') or item.get('customer_gai_id')
            if item_gai is not None and str(item_gai) != str(gai_filter):
                continue
        label = item.get('description') or item.get('type') or str(item_id)
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


def fetch_column_templates(user):
    """GET /lookups/column-templates — templates para colunas de board."""
    return CrmApiClient(user).get('/lookups/column-templates')


def build_column_template_choices(templates):
    return _build_uuid_choices(
        templates if isinstance(templates, list) else normalize_column_templates(templates),
        label_keys=('name', 'title', 'code'),
    )


def normalize_column_templates(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get('items') or raw.get('results') or []
    return []


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
