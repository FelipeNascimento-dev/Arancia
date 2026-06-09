import logging
from datetime import date

from celery import shared_task
from django.conf import settings

from crm.services.client import CrmApiClient
from crm.services.exceptions import CrmApiError
from crm.services.pagination import normalize_list_response

logger = logging.getLogger(__name__)


def _service_client():
    return CrmApiClient(service=True)


@shared_task(name='crm.tasks.crm_fire_due_alerts')
def crm_fire_due_alerts():
    """
    Dispara alertas pendentes com due_date <= hoje.
    API não expõe listagem de vencidos — filtra localmente após GET /alerts/.
    """
    if not settings.CRM_API_BASE_URL or not settings.CRM_INTERNAL_API_SECRET:
        logger.warning('CRM não configurado; crm_fire_due_alerts ignorado.')
        return 'CRM não configurado.'

    client = _service_client()
    today = date.today()
    fired = 0
    errors = 0

    try:
        raw = client.get('/alerts/', params={'limit': 500})
        alerts = normalize_list_response(raw)
    except CrmApiError as exc:
        logger.error('crm_fire_due_alerts: falha ao listar alertas: %s', exc)
        return f'Erro ao listar alertas: {exc}'

    for alert in alerts:
        alert_id = alert.get('id')
        due = alert.get('due_date')
        if not alert_id or not due:
            continue
        try:
            due_date = date.fromisoformat(str(due)[:10])
        except ValueError:
            continue
        if due_date > today:
            continue
        if alert.get('fired_at') or alert.get('is_fired'):
            continue
        try:
            client.post(f'/alerts/fire/{alert_id}', json={})
            fired += 1
        except CrmApiError as exc:
            errors += 1
            logger.warning('crm_fire_due_alerts: fire %s falhou: %s', alert_id, exc)

    return f'{fired} alertas disparados; {errors} erros.'


@shared_task(name='crm.tasks.crm_generate_recurring_tasks')
def crm_generate_recurring_tasks():
    """Gera tarefas recorrentes vencidas via scheduler interno da API."""
    if not settings.CRM_API_BASE_URL or not settings.CRM_INTERNAL_API_SECRET:
        logger.warning('CRM não configurado; crm_generate_recurring_tasks ignorado.')
        return 'CRM não configurado.'

    client = _service_client()
    try:
        result = client.post('/internal/scheduler/generate-due-tasks', json={})
        count = result.get('generated_count') if isinstance(result, dict) else result
        return f'Tarefas recorrentes geradas: {count}'
    except CrmApiError as exc:
        logger.error('crm_generate_recurring_tasks falhou: %s', exc)
        return f'Erro: {exc}'
