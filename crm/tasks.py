import logging

from celery import shared_task

from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError
from crm_api.services import alerts as alerts_service
from crm_api.services import recurrences as recurrences_service

logger = logging.getLogger(__name__)


@shared_task
def generate_recurring_tasks():
    """Dispara o agendador interno da API CRM (idempotente no lado da API)."""
    client = CrmApiClient(scheduler=True)
    try:
        result = recurrences_service.generate_due_tasks(client)
        logger.info("CRM scheduler generate_due_tasks: %s", result)
        return "Scheduler CRM executado com sucesso."
    except CrmApiError as exc:
        logger.exception("CRM scheduler falhou: %s", exc)
        return f"Scheduler CRM falhou: {exc}"


@shared_task
def fire_contract_alerts():
    """Lista alertas pendentes e dispara fire para cada um."""
    client = CrmApiClient(service_user=True)
    fired = 0
    errors = 0
    try:
        items, _ = alerts_service.list_alerts(client, limit=500)
    except CrmApiError as exc:
        logger.exception("CRM fire_contract_alerts — listagem falhou: %s", exc)
        return f"Listagem de alertas falhou: {exc}"

    for alert in items:
        alert_id = alert.get("id")
        if alert_id is None:
            continue
        status = (alert.get("status") or "").lower()
        if status in ("fired", "sent", "cancelled", "inactive"):
            continue
        try:
            alerts_service.fire_alert(client, alert_id)
            fired += 1
        except CrmApiError:
            errors += 1
            logger.warning("CRM fire alert %s falhou", alert_id)

    return f"{fired} alertas disparados; {errors} erros."
