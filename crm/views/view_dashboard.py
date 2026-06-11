from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_module_required
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.tasks import enrich_task
from crm.services.gates import ajax_require_gai
from crm.services.lookups import (
    fetch_crm_lookups,
    fetch_gais,
    fetch_groups,
    normalize_lookup_list,
    parse_customer_gai_id,
)


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

    if request.user.has_perm('crm.view_billing'):
        try:
            billing_summary = client.get('/billing/summary')
        except CrmApiError as exc:
            errors.append('resumo de faturamento')
            handle_crm_error(request, exc)

    if request.user.has_perm('crm.view_contracts'):
        try:
            alerts = client.get('/alerts/')
        except CrmApiError as exc:
            errors.append('alertas')
            handle_crm_error(request, exc)

    if request.user.has_perm('crm.view_tasks'):
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

    tasks_list = [enrich_task(t) for t in tasks_list if isinstance(t, dict)]

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


@require_GET
@crm_module_required
def ajax_crm_lookups(request):
    """GET /lookups/crm com filtro opcional customer_gai_id (service_types por GAI)."""
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked
    customer_gai_id = parse_customer_gai_id(request.GET.get('customer_gai_id'))
    try:
        lookups = fetch_crm_lookups(request.user, customer_gai_id=customer_gai_id)
        return JsonResponse({'ok': True, 'lookups': lookups})
    except CrmApiError as exc:
        return JsonResponse({'ok': False, 'error': str(exc.detail or exc)}, status=exc.status_code or 502)


@require_GET
@crm_module_required
def ajax_lookup_groups(request):
    """GET /lookups/groups — grupos para filtro de demandantes GAI."""
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked
    try:
        groups = normalize_lookup_list(fetch_groups(request.user))
        return JsonResponse({'ok': True, 'groups': groups})
    except CrmApiError as exc:
        return JsonResponse({'ok': False, 'error': str(exc.detail or exc)}, status=exc.status_code or 502)


@require_GET
@crm_module_required
def ajax_lookup_gais(request):
    """GET /lookups/gais — GAIs demandantes (typeahead / picker)."""
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked
    group_id = request.GET.get('group_id')
    search = request.GET.get('search') or request.GET.get('q')
    try:
        gais = normalize_lookup_list(
            fetch_gais(request.user, group_id=group_id, search=search)
        )
        return JsonResponse({'ok': True, 'gais': gais})
    except CrmApiError as exc:
        return JsonResponse({'ok': False, 'error': str(exc.detail or exc)}, status=exc.status_code or 502)
