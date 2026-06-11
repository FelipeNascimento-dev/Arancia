"""Conversão de tarefas CRM para eventos FullCalendar."""

from datetime import datetime, timedelta

from django.urls import reverse

from crm.services.datetime_utils import BR_TZ, UTC_TZ, parse_api_datetime
from crm.services.refs import priority_ref_label, status_ref_label
from crm.services.tasks import normalize_task_fields

DEFAULT_EVENT_DURATION = timedelta(hours=1)

PRIORITY_COLORS = {
    'alta': '#e74c3c',
    'high': '#e74c3c',
    'média': '#f39c12',
    'media': '#f39c12',
    'medium': '#f39c12',
    'baixa': '#3498db',
    'low': '#3498db',
}

SCHEDULED_COLOR = '#153e70'
DUE_COLOR = '#7f8c8d'
OVERDUE_COLOR = '#c0392b'


def parse_fc_range(start_raw, end_raw):
    """Interpreta parâmetros ISO enviados pelo FullCalendar."""
    start = parse_api_datetime(start_raw) if start_raw else None
    end = parse_api_datetime(end_raw) if end_raw else None
    return start, end


def _to_fc_datetime(dt):
    if not dt:
        return None
    return dt.astimezone(BR_TZ).isoformat()


def _priority_color(task):
    priority = task.get('priority') if isinstance(task.get('priority'), dict) else {}
    for key in ('slug', 'name'):
        value = str(priority.get(key) or '').strip().lower()
        if value:
            for token, color in PRIORITY_COLORS.items():
                if token in value:
                    return color
    for key in ('priority_slug', 'priority_name', 'priority_id'):
        value = str(task.get(key) or '').strip().lower()
        if not value:
            continue
        for token, color in PRIORITY_COLORS.items():
            if token in value:
                return color
    return SCHEDULED_COLOR


def _event_in_range(event_start, event_end, range_start, range_end):
    if not range_start or not range_end:
        return True
    if event_end and event_end <= range_start:
        return False
    if event_start >= range_end:
        return False
    return True


def _build_scheduled_event(task):
    task = normalize_task_fields(task)
    task_id = task.get('id')
    scheduled = parse_api_datetime(task.get('scheduled_at'))
    if not task_id or not scheduled:
        return None

    local = scheduled.astimezone(BR_TZ)
    all_day = local.hour == 0 and local.minute == 0 and local.second == 0
    event = {
        'id': f'scheduled-{task_id}',
        'title': task.get('title') or 'Tarefa',
        'start': local.date().isoformat() if all_day else _to_fc_datetime(scheduled),
        'allDay': all_day,
        'url': reverse('crm:task_detail', kwargs={'task_id': task_id}),
        'backgroundColor': _priority_color(task),
        'borderColor': _priority_color(task),
        'extendedProps': {
            'kind': 'scheduled',
            'status': status_ref_label(task),
            'priority': priority_ref_label(task),
            'due_at': task.get('due_at') or '',
        },
    }
    if not all_day:
        event['end'] = _to_fc_datetime(scheduled + DEFAULT_EVENT_DURATION)
    return event


def _build_due_event(task, *, now=None):
    task = normalize_task_fields(task)
    task_id = task.get('id')
    if task.get('scheduled_at'):
        return None
    due = parse_api_datetime(task.get('due_at'))
    if not task_id or not due:
        return None

    now = now or datetime.now(tz=UTC_TZ)
    overdue = due < now
    local = due.astimezone(BR_TZ)
    title = task.get('title') or 'Tarefa'
    return {
        'id': f'due-{task_id}',
        'title': f'Vence: {title}',
        'start': local.date().isoformat(),
        'allDay': True,
        'url': reverse('crm:task_detail', kwargs={'task_id': task_id}),
        'backgroundColor': OVERDUE_COLOR if overdue else DUE_COLOR,
        'borderColor': OVERDUE_COLOR if overdue else DUE_COLOR,
        'classNames': ['crm-cal-event-due'],
        'extendedProps': {
            'kind': 'due',
            'status': status_ref_label(task),
            'priority': priority_ref_label(task),
            'overdue': overdue,
        },
    }


def tasks_to_calendar_events(tasks, *, start=None, end=None, include_due=False):
    """Monta lista de eventos FullCalendar a partir de tarefas da API."""
    events = []
    now = datetime.now(tz=UTC_TZ)

    for task in tasks or []:
        if not isinstance(task, dict):
            continue

        scheduled_event = _build_scheduled_event(task)
        if scheduled_event:
            event_start = parse_api_datetime(task.get('scheduled_at'))
            event_end = event_start + DEFAULT_EVENT_DURATION if event_start else None
            if _event_in_range(event_start, event_end, start, end):
                events.append(scheduled_event)

        if include_due:
            due_event = _build_due_event(task, now=now)
            if due_event:
                due_start = parse_api_datetime(task.get('due_at'))
                due_end = due_start + timedelta(days=1) if due_start else None
                if _event_in_range(due_start, due_end, start, end):
                    events.append(due_event)

    return events


def build_calendar_fetch_params(start=None, end=None, *, include_due=False):
    """Parâmetros para GET /tasks/ — inclui filtros de data quando disponíveis."""
    params = {'limit': 500}
    if not include_due:
        params['scheduled_only'] = 'true'

    if start:
        params['scheduled_from'] = start.astimezone(UTC_TZ).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    if end:
        params['scheduled_to'] = end.astimezone(UTC_TZ).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    if include_due:
        if start:
            params['due_from'] = start.astimezone(UTC_TZ).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        if end:
            params['due_to'] = end.astimezone(UTC_TZ).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    return params
