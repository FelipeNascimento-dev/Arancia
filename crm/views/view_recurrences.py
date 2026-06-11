from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_recurrences import TaskRecurrenceForm
from crm.services.client import CrmApiClient
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.gates import ajax_require_gai, require_gai_or_render
from crm.services.lookups import (
    build_board_choices,
    build_priority_choices,
    build_project_choices,
    build_status_choices,
    fetch_crm_lookups,
)
from crm.services.pagination import (
    build_pagination_context,
    find_record_by_id,
    get_pagination_params,
    normalize_list_response,
)

PROJECTS_MENU = {
    'current_parent_menu': 'projetos',
    'current_menu': 'projetos_recurrences',
}


def _require_gai_or_render(request, template, extra_context=None):
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Recorrências',
        menu_context=PROJECTS_MENU,
        extra_context=extra_context,
    )


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _recurrence_form_kwargs(lookups):
    return {
        'board_choices': build_board_choices(lookups),
        'status_choices': build_status_choices(lookups),
        'priority_choices': build_priority_choices(lookups),
        'project_choices': build_project_choices(lookups),
    }


@crm_perm_required('view_task_recurrences')
def recurrence_list(request):
    blocked = _require_gai_or_render(request, 'crm/recurrences/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    items = []
    api_error = None
    try:
        raw = CrmApiClient(request.user).get('/task-recurrences/', params={'skip': skip, 'limit': limit})
        items = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    return render(request, 'crm/recurrences/list.html', {
        'site_title': 'CRM — Recorrências de tarefas',
        'items': items,
        'pagination': build_pagination_context(skip, limit, items),
        'api_error': api_error,
        'can_manage': request.user.has_perm('crm.add_task_recurrence'),
        **PROJECTS_MENU,
    })


@crm_perm_required('add_task_recurrence')
def recurrence_new(request):
    params = []
    if request.GET.get('board_id'):
        params.append(f"board_id={request.GET.get('board_id')}")
    if request.GET.get('project_id'):
        params.append(f"project_id={request.GET.get('project_id')}")
    params.append('recurring=1')
    return redirect(f"{reverse('crm:task_new')}?{'&'.join(params)}")


@crm_perm_required('view_task_recurrences')
def recurrence_detail(request, recurrence_id):
    blocked = _require_gai_or_render(request, 'crm/recurrences/detail.html')
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    try:
        record = api.get(f'/task-recurrences/{recurrence_id}')
        runs = normalize_list_response(api.get(f'/task-recurrences/{recurrence_id}/runs'))
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:recurrence_list')

    return render(request, 'crm/recurrences/detail.html', {
        'site_title': f'CRM — {record.get("title") or recurrence_id}',
        'record': record,
        'recurrence_id': recurrence_id,
        'runs': runs,
        **PROJECTS_MENU,
    })


@crm_perm_required('change_task_recurrence')
def recurrence_edit(request, recurrence_id):
    blocked = _require_gai_or_render(request, 'crm/recurrences/form.html', {
        'form_mode': 'edit',
        'recurrence_id': recurrence_id,
    })
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)
    form_kwargs = _recurrence_form_kwargs(lookups)

    try:
        record = find_record_by_id(request.user, '/task-recurrences/', recurrence_id)
        if not record:
            raise CrmApiError('Recorrência não encontrada.', status_code=404)
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:recurrence_list')

    initial = {
        'title': record.get('title') or '',
        'description': record.get('description') or '',
        'board_id': str(record['board_id']) if record.get('board_id') else '',
        'status_id': str(record['status_id']) if record.get('status_id') else '',
        'priority_id': str(record['priority_id']) if record.get('priority_id') else '',
        'project_id': str(record['project_id']) if record.get('project_id') else '',
        'frequency': record.get('frequency') or 'daily',
        'interval': record.get('interval') or 1,
        'start_date': str(record.get('start_date') or '')[:10] if record.get('start_date') else '',
        'end_date': str(record.get('end_date') or '')[:10] if record.get('end_date') else '',
        'is_active': record.get('is_active', True),
    }
    form = TaskRecurrenceForm(initial=initial, **form_kwargs)

    if request.method == 'POST':
        form = TaskRecurrenceForm(request.POST, **form_kwargs)
        if form.is_valid():
            try:
                api.patch(
                    f'/task-recurrences/{recurrence_id}',
                    json=form.cleaned_payload(for_update=True),
                )
                messages.success(request, 'Recorrência atualizada.')
                return redirect('crm:recurrence_detail', recurrence_id=recurrence_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/recurrences/form.html', {
        'site_title': f'CRM — Editar {record.get("title") or recurrence_id}',
        'form': form,
        'form_mode': 'edit',
        'recurrence_id': recurrence_id,
        'record': record,
        'lookups': lookups,
        **PROJECTS_MENU,
    })
    

@require_POST
@crm_perm_required('delete_task_recurrence')
def ajax_recurrence_delete(request, recurrence_id):
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    try:
        CrmApiClient(request.user).delete(f'/task-recurrences/{recurrence_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)
