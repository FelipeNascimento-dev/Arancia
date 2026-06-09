from django.conf import settings

from .client import CrmApiClient


def get_pagination_params(request, *, default_limit=None):
    """Extrai skip/limit da query string para listagens CRM."""
    default_limit = default_limit or settings.CRM_DEFAULT_LIMIT
    try:
        skip = max(0, int(request.GET.get('skip', 0)))
    except (TypeError, ValueError):
        skip = 0
    try:
        limit = max(1, min(int(request.GET.get('limit', default_limit)), default_limit))
    except (TypeError, ValueError):
        limit = default_limit
    return skip, limit


def build_pagination_context(skip, limit, items):
    """Monta contexto de paginação sem total count (gap API)."""
    count = len(items) if items is not None else 0
    has_prev = skip > 0
    has_next = count >= limit
    return {
        'skip': skip,
        'limit': limit,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_skip': max(0, skip - limit),
        'next_skip': skip + limit,
    }


def normalize_list_response(data):
    """Normaliza resposta de listagem da API (lista ou dict com items/results)."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get('items') or data.get('results') or []
    return []


def find_record_by_id(user, path, record_id, *, page_size=500):
    """Busca um registro em listagem paginada quando a API não expõe GET por id."""
    client = CrmApiClient(user)
    skip = 0
    while True:
        raw = client.get(path, params={'skip': skip, 'limit': page_size})
        items = normalize_list_response(raw)
        for item in items:
            if str(item.get('id')) == str(record_id):
                return item
        if len(items) < page_size:
            break
        skip += page_size
    return None
