"""Helpers de listagem de tarefas — workaround para bug da API CRM."""

from .client import CrmApiClient
from .exceptions import CrmServerError


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
