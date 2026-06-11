"""Helpers de recorrência: payloads, scheduler one-shot e acesso ao board."""

from typing import Optional

from django.utils import timezone

from .client import CrmApiClient
from .datetime_utils import format_datetime_to_api, parse_api_datetime
from .exceptions import CrmApiError

FREQ_MAP = {
    'daily': 'DAILY',
    'weekly': 'WEEKLY',
    'monthly': 'MONTHLY',
}


def frequency_to_rrule(frequency, interval=1):
    """Converte frequência simplificada da UI para RRULE da API."""
    freq = FREQ_MAP.get((frequency or '').lower())
    if not freq:
        raise ValueError(f'Frequência inválida: {frequency}')
    interval = max(int(interval or 1), 1)
    parts = [f'FREQ={freq}']
    if interval > 1:
        parts.append(f'INTERVAL={interval}')
    return ';'.join(parts)


def recurrence_start_at_from_form(data):
    """Retorna start_at ISO UTC a partir dos campos do formulário."""
    scheduled_at = format_datetime_to_api(data.get('scheduled_at'))
    if scheduled_at:
        return scheduled_at
    raw = data.get('recurrence_start')
    if raw:
        return format_datetime_to_api(f'{raw}T00:00')
    return None


def recurrence_end_at_from_form(data):
    raw = data.get('recurrence_end')
    if not raw:
        return None
    return format_datetime_to_api(f'{raw}T23:59')


def recurrence_start_is_due(start_at):
    """True se start_at <= agora (UTC), alinhado à API."""
    if not start_at:
        return False
    dt = parse_api_datetime(start_at)
    if dt is None:
        return False
    return dt <= timezone.now()


def build_recurrence_create_payload(data, *, fields_present=None):
    """Monta payload TaskRecurrenceCreate para POST /task-recurrences/."""
    payload = {
        'title': data['title'].strip(),
        'rrule': frequency_to_rrule(data['frequency'], data.get('interval') or 1),
        'is_active': True,
    }
    if data.get('description'):
        payload['description'] = data['description']

    for field, key in (
        ('board_id', 'board_id'),
        ('status_id', 'status_id'),
        ('priority_id', 'priority_id'),
        ('project_id', 'project_id'),
    ):
        if fields_present is not None and field not in fields_present:
            continue
        if data.get(field):
            payload[key] = data[field]

    if data.get('customer_gai_id'):
        payload['customer_gai_id'] = int(data['customer_gai_id'])

    requester_ids = data.get('requester_gai_ids')
    if requester_ids:
        payload['requester_gai_ids'] = [int(gai_id) for gai_id in requester_ids]

    start_at = recurrence_start_at_from_form(data)
    if start_at:
        payload['start_at'] = start_at

    end_at = recurrence_end_at_from_form(data)
    if end_at:
        payload['end_at'] = end_at

    return payload


def board_access_can_create_tasks(user, board_id):
    """
    Consulta GET /boards/{id}/access/me.
    Retorna True/False ou None se indeterminado.
    """
    if not board_id:
        return None
    try:
        access = CrmApiClient(user).get(f'/boards/{board_id}/access/me') or {}
    except CrmApiError:
        return None
    if 'can_create_tasks' not in access:
        return None
    return bool(access.get('can_create_tasks'))


def validate_board_can_create(user, board_id):
    """Mensagem amigável se o usuário não pode criar tasks no board."""
    allowed = board_access_can_create_tasks(user, board_id)
    if allowed is False:
        return 'Você não tem permissão para criar tarefas neste board.'
    return None


def run_scheduler_for_template(template_id, *, client=None):
    """
    Dispara POST /internal/scheduler/generate-due-tasks e retorna task_id
    gerada para o template informado, se houver.
    """
    if not template_id:
        return None
    api = client or CrmApiClient(service=True)
    try:
        result = api.post('/internal/scheduler/generate-due-tasks', json={}) or {}
    except CrmApiError:
        return None

    template_key = str(template_id)
    for item in result.get('results') or []:
        if not isinstance(item, dict):
            continue
        if str(item.get('template_id')) == template_key and item.get('task_id'):
            return str(item['task_id'])
    return None
