import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_boards import BoardAccessForm
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.datetime_utils import format_datetime
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.lookups import (
    build_designation_choices,
    build_team_gai_choices,
    build_user_choices,
    fetch_member_lookups,
    fetch_team_gais,
)
from crm.services.pagination import normalize_list_response
from crm.services.tasks import list_tasks

PROJECTS_MENU = {
    'current_parent_menu': 'projetos',
    'current_menu': 'projetos_boards',
}


def _require_gai_or_render(request, template, extra_context=None):
    if get_user_gai_id(request.user) is not None:
        return None
    context = {
        'site_title': 'CRM — Boards',
        'missing_gai': True,
        **PROJECTS_MENU,
        **(extra_context or {}),
    }
    return render(request, template, context)


def _access_form_choices(request):
    try:
        members_lookup = fetch_member_lookups(request.user)
    except CrmApiError:
        members_lookup = None
    try:
        team_gais = fetch_team_gais(request.user)
    except CrmApiError:
        team_gais = []
    team_items = team_gais if isinstance(team_gais, list) else (team_gais or {}).get('items') or []
    return {
        'user_choices': build_user_choices(members_lookup),
        'designation_choices': build_designation_choices(members_lookup),
        'team_gai_choices': build_team_gai_choices(team_items),
    }


def _enrich_task_card(task):
    task = dict(task)
    if task.get('due_at'):
        task['due_at_formatted'] = format_datetime(task['due_at'])
    return task


@crm_perm_required('view_boards')
def board_kanban(request, board_id):
    blocked = _require_gai_or_render(request, 'crm/boards/kanban.html', {'board_id': board_id})
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    board_data = None
    columns = []
    tasks_by_status = {}
    access_me = {}
    api_error = None

    try:
        board_data = api.get(f'/boards/{board_id}')
        columns = normalize_list_response(api.get(f'/boards/{board_id}/columns'))
        access_me = api.get(f'/boards/{board_id}/access/me') or {}
        raw_tasks, _ = list_tasks(
            request.user,
            params={'board_id': str(board_id), 'limit': 500},
        )
        tasks = normalize_list_response(raw_tasks)
        for col in columns:
            status_id = str(col.get('status_id') or col.get('id') or '')
            tasks_by_status[status_id] = []
        for task in tasks:
            task = _enrich_task_card(task)
            status_id = str(task.get('status_id') or '')
            if status_id not in tasks_by_status:
                tasks_by_status[status_id] = []
            tasks_by_status[status_id].append(task)
        for status_id in tasks_by_status:
            tasks_by_status[status_id].sort(
                key=lambda t: t.get('kanban_position') if t.get('kanban_position') is not None else 9999
            )
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)
        if exc.status_code == 404:
            return redirect('crm:dashboard')

    can_move = access_me.get('can_move_tasks', request.user.has_perm('crm.move_task'))
    can_comment = access_me.get('can_comment', request.user.has_perm('crm.change_task'))

    return render(request, 'crm/boards/kanban.html', {
        'site_title': f'CRM — {board_data.get("name") or board_data.get("title") or board_id if board_data else board_id}',
        'board': board_data,
        'board_id': board_id,
        'columns': columns,
        'tasks_by_status': tasks_by_status,
        'access_me': access_me,
        'can_move_tasks': can_move,
        'can_comment': can_comment,
        'api_error': api_error,
        **PROJECTS_MENU,
        'current_submenu': str(board_id),
    })


@crm_perm_required('manage_board_access')
def board_access(request, board_id):
    blocked = _require_gai_or_render(request, 'crm/boards/access.html', {'board_id': board_id})
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    try:
        board_data = api.get(f'/boards/{board_id}')
        access_list = normalize_list_response(api.get(f'/boards/{board_id}/access'))
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:dashboard')

    choices = _access_form_choices(request)
    access_form = BoardAccessForm(**choices)

    if request.method == 'POST':
        access_form = BoardAccessForm(request.POST, **choices)
        if access_form.is_valid():
            try:
                api.post(
                    f'/boards/{board_id}/access',
                    json=access_form.cleaned_payload(),
                )
                messages.success(request, 'Acesso concedido.')
                return redirect('crm:board_access', board_id=board_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/boards/access.html', {
        'site_title': f'CRM — Acesso — {board_data.get("name") or board_id}',
        'board': board_data,
        'board_id': board_id,
        'access_list': access_list,
        'access_form': access_form,
        **PROJECTS_MENU,
    })


@require_POST
@crm_perm_required('manage_board_columns')
def ajax_board_reorder_columns(request, board_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)

    column_ids = payload.get('column_ids') or payload.get('columns')
    if not column_ids:
        return JsonResponse({'ok': False, 'error': 'column_ids é obrigatório.'}, status=400)

    try:
        result = CrmApiClient(request.user).patch(
            f'/boards/{board_id}/columns/reorder',
            json={'column_ids': column_ids},
        )
        return JsonResponse({'ok': True, 'columns': result})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


@require_POST
@crm_perm_required('manage_board_access')
def ajax_board_access_delete(request, board_id, access_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/boards/{board_id}/access/{access_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)
