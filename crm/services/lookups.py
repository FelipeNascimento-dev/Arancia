from django.contrib.auth.models import User

from .client import CrmApiClient
from .exceptions import CrmApiError


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


def _user_operational_gai(user):
    designacao = getattr(user, 'designacao', None)
    if designacao is None:
        return None
    return designacao.informacao_adicional


def _designation_label(user, gai):
    if gai is None:
        return user.username
    name = (gai.nome or gai.razao_social or '').strip()
    if name:
        return f'{user.username} — {name}'
    return f'{user.username} — GAI {gai.id}'


def _scoped_member_users_qs(requesting_user):
    """Usuários ARC ativos com GAI, filtrados pelo escopo operacional."""
    qs = (
        User.objects.filter(username__startswith='ARC', is_active=True)
        .select_related('designacao__informacao_adicional')
        .filter(designacao__informacao_adicional__isnull=False)
        .order_by('username')
    )
    if requesting_user.has_perm('logistica.gestao_total'):
        return qs

    gai = _user_operational_gai(requesting_user)
    if gai is None:
        return qs.none()

    sales_channel = (gai.sales_channel or '').strip()
    if sales_channel == 'all':
        return qs

    if sales_channel:
        return qs.filter(designacao__informacao_adicional__sales_channel=sales_channel)

    return qs.filter(designacao__informacao_adicional_id=gai.id)


def fetch_member_lookups_django(user):
    """
    Monta lookups de membros a partir do banco Django (User + UserDesignation + GAI).
    Formato compatível com GET /lookups/members da API.
    """
    users = []
    designations = []
    for member in _scoped_member_users_qs(user):
        designacao = getattr(member, 'designacao', None)
        gai = designacao.informacao_adicional if designacao else None
        full_name = member.get_full_name().strip()
        users.append({
            'id': member.id,
            'username': member.username,
            'full_name': full_name or None,
        })
        if designacao:
            designations.append({
                'id': designacao.id,
                'username': member.username,
                'label': _designation_label(member, gai),
            })
    return {'users': users, 'designations': designations}


def _member_lookups_need_fallback(data):
    if not isinstance(data, dict):
        return True
    users = data.get('users')
    designations = data.get('designations')
    if users is None and designations is None:
        return True
    return not (users or designations)


def resolve_member_lookups(user):
    """
    Tenta GET /lookups/members; se ausente, vazio ou com erro, usa Django.
    """
    try:
        data = fetch_member_lookups(user)
        if not _member_lookups_need_fallback(data):
            return data
    except CrmApiError:
        pass
    return fetch_member_lookups_django(user)


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
