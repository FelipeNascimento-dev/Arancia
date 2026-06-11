"""Helpers de listagem de tarefas — workaround para bug da API CRM."""

from .client import CrmApiClient
from .datetime_utils import format_datetime
from .exceptions import CrmServerError


def normalize_task_fields(task):
    """
    Unifica aliases da API (homolog usa due_date / scheduled_start_at)
    com os campos flat legados (due_at / scheduled_at) usados no BFF.
    """
    if not isinstance(task, dict):
        return task
    normalized = dict(task)
    if normalized.get('due_at') is None and normalized.get('due_date') is not None:
        normalized['due_at'] = normalized['due_date']
    if normalized.get('scheduled_at') is None and normalized.get('scheduled_start_at') is not None:
        normalized['scheduled_at'] = normalized['scheduled_start_at']
    normalized.setdefault('due_at', None)
    normalized.setdefault('scheduled_at', None)
    return normalized


def enrich_task(task):
    """Normaliza campos de data e adiciona labels formatados para templates."""
    normalized = normalize_task_fields(task)
    if not isinstance(normalized, dict):
        return normalized
    due = normalized.get('due_at')
    if due:
        normalized['due_at_formatted'] = format_datetime(due)
    scheduled = normalized.get('scheduled_at')
    if scheduled:
        normalized['scheduled_at_formatted'] = format_datetime(scheduled)
    return normalized


def enrich_move_history(entries):
    """Normaliza move-history para templates (flat legado + refs aninhados)."""
    enriched = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        row = dict(entry)
        for direction in ('from', 'to'):
            nested = row.get(f'{direction}_status')
            name_key = f'{direction}_status_name'
            if row.get(name_key) is None and isinstance(nested, dict):
                row[name_key] = nested.get('name')
            row.setdefault(name_key, None)
        moved_by = row.get('moved_by')
        if row.get('moved_by_username') is None and isinstance(moved_by, dict):
            row['moved_by_username'] = moved_by.get('username')
        row.setdefault('moved_by_username', None)
        enriched.append(row)
    return enriched


def list_tasks(user, *, params=None):
    """
    Lista tarefas via GET /tasks/ ou fallbacks compatíveis.

    A API CRM retorna HTTP 500 em GET /tasks/ sem ``my_tasks=true`` (com ou
    sem ``board_id``). Mantém ``board_id`` e demais filtros nos fallbacks.
    """
    params = dict(params or {})
    client = CrmApiClient(user)

    try:
        return client.get('/tasks/', params=params), False
    except CrmServerError:
        pass

    with_my_tasks = {**params, 'my_tasks': 'true'}
    try:
        return client.get('/tasks/', params=with_my_tasks), True
    except CrmServerError:
        pass

    my_params = {key: value for key, value in params.items() if key != 'my_tasks'}
    my_params.setdefault('role', 'all')
    return client.get('/tasks/my/', params=my_params), True
