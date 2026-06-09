from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_module_required
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.datetime_utils import format_datetime
from crm.services.exceptions import CrmApiError, handle_crm_error


@crm_module_required
def dashboard(request):
    """Dashboard CRM composto: billing/summary, alerts, tasks/my overdue."""
    gai_id = get_user_gai_id(request.user)
    if gai_id is None:
        messages.warning(
            request,
            'Seu usuário não possui GAI (designação) configurado. '
            'Solicite ao gestor antes de usar o CRM.',
        )
        return render(request, 'crm/dashboard.html', {
            'site_title': 'CRM — Dashboard',
            'current_parent_menu': 'crm',
            'current_menu': 'crm_dashboard',
            'missing_gai': True,
        })

    client = CrmApiClient(request.user)
    billing_summary = None
    alerts = None
    overdue_tasks = None
    errors = []

    try:
        billing_summary = client.get('/billing/summary')
    except CrmApiError as exc:
        errors.append('resumo de faturamento')
        handle_crm_error(request, exc)

    try:
        alerts = client.get('/alerts/')
    except CrmApiError as exc:
        errors.append('alertas')
        handle_crm_error(request, exc)

    try:
        overdue_tasks = client.get('/tasks/my/', params={'overdue_only': 'true'})
    except CrmApiError as exc:
        errors.append('tarefas em atraso')
        handle_crm_error(request, exc)

    if isinstance(alerts, dict):
        alerts_list = alerts.get('items') or alerts.get('results') or []
    elif isinstance(alerts, list):
        alerts_list = alerts
    else:
        alerts_list = []

    if isinstance(overdue_tasks, dict):
        tasks_list = overdue_tasks.get('items') or overdue_tasks.get('results') or []
    elif isinstance(overdue_tasks, list):
        tasks_list = overdue_tasks
    else:
        tasks_list = []

    for task in tasks_list:
        if isinstance(task, dict) and task.get('due_at'):
            task['due_at_formatted'] = format_datetime(task['due_at'])

    return render(request, 'crm/dashboard.html', {
        'site_title': 'CRM — Dashboard',
        'current_parent_menu': 'crm',
        'current_menu': 'crm_dashboard',
        'billing_summary': billing_summary,
        'alerts': alerts_list,
        'overdue_tasks': tasks_list,
        'partial_errors': errors,
    })


@require_GET
@crm_module_required
def ajax_health(request):
    """Proxy de health: GET {CRM_API_BASE_URL}/"""
    try:
        response = CrmApiClient(request.user).health_check()
        return JsonResponse({
            'ok': response.status_code < 400,
            'status_code': response.status_code,
        })
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc),
        }, status=502)


@require_POST
@staff_member_required
@crm_module_required
def validate_context(request):
    """Diagnóstico staff: POST /auth/validate-context."""
    try:
        client = CrmApiClient(request.user)
        result = client.post('/auth/validate-context', json={})
        return JsonResponse({'ok': True, 'result': result})
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return JsonResponse({'ok': False, 'error': str(exc)}, status=exc.status_code or 502)
