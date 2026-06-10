import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_boards import (
    BoardAccessForm,
    BoardColumnForm,
    BoardForm,
)
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.datetime_utils import format_datetime
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.lookups import (
    build_column_template_choices,
    build_designation_choices,
    build_project_choices,
    build_status_choices,
    build_team_gai_choices,
    build_user_choices,
    fetch_column_templates,
    fetch_crm_lookups,
    fetch_member_lookups,
    fetch_team_gais,
)
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)
from crm.services.tasks import list_tasks

CRM_BOARDS_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_boards',
}

PROJECTS_MENU = {
    'current_parent_menu': 'projetos',
    'current_menu': 'projetos_boards',
}


def _filter_boards_by_type(boards, board_type):
    if not board_type:
        return boards
    return [board for board in boards if board.get('board_type') == board_type]


def _board_menu_context(request, board_data=None, *, board_id=None):
    """Destaca menu CRM ou Projetos conforme ?menu= ou board_type."""
    menu = (request.GET.get('menu') or '').strip().lower()
    if menu == 'crm':
        ctx = dict(CRM_BOARDS_MENU)
    elif menu == 'projetos':
        ctx = dict(PROJECTS_MENU)
    elif board_data and board_data.get('board_type') == 'crm':
        ctx = dict(CRM_BOARDS_MENU)
    else:
        ctx = dict(PROJECTS_MENU)
    if board_id is not None:
        ctx['current_submenu'] = str(board_id)
    return ctx


def _require_gai_or_render(request, template, extra_context=None, *, menu_context=None):
    if get_user_gai_id(request.user) is not None:
        return None
    context = {
        'site_title': 'CRM — Boards',
        'missing_gai': True,
        **(menu_context or PROJECTS_MENU),
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


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _column_form_kwargs(request):
    lookups, _ = _load_lookups(request)
    try:
        templates = fetch_column_templates(request.user)
    except CrmApiError:
        templates = []
    return {
        'status_choices': build_status_choices(lookups),
        'template_choices': build_column_template_choices(templates),
    }


@crm_perm_required('view_boards')
def board_list(request):
    menu_ctx = _board_menu_context(request)
    board_type_filter = (request.GET.get('board_type') or '').strip() or None
    blocked = _require_gai_or_render(
        request,
        'crm/boards/list.html',
        menu_context=menu_ctx,
    )
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    boards = []
    api_error = None
    try:
        raw = CrmApiClient(request.user).get('/boards/', params={'skip': skip, 'limit': limit})
        boards = _filter_boards_by_type(normalize_list_response(raw), board_type_filter)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    return render(request, 'crm/boards/list.html', {
        'site_title': 'CRM — Boards',
        'boards': boards,
        'board_type_filter': board_type_filter,
        'menu_scope': request.GET.get('menu'),
        'pagination': build_pagination_context(skip, limit, boards),
        'api_error': api_error,
        **menu_ctx,
    })


@crm_perm_required('add_board')
def board_new(request):
    menu_ctx = _board_menu_context(request)
    blocked = _require_gai_or_render(
        request,
        'crm/boards/form.html',
        {'form_mode': 'new'},
        menu_context=menu_ctx,
    )
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    project_choices = build_project_choices(lookups)

    if request.method == 'POST':
        form = BoardForm(request.POST, project_choices=project_choices)
        if form.is_valid():
            try:
                result = CrmApiClient(request.user).post('/boards/', json=form.cleaned_payload())
                board_id = result.get('id') if isinstance(result, dict) else None
                messages.success(request, 'Board criado com sucesso.')
                if board_id:
                    return redirect('crm:board_kanban', board_id=board_id)
                return redirect('crm:board_list')
            except CrmApiError as exc:
                handle_crm_error(request, exc)
    else:
        form = BoardForm(project_choices=project_choices)

    return render(request, 'crm/boards/form.html', {
        'site_title': 'CRM — Novo board',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        **menu_ctx,
    })


@crm_perm_required('change_board')
def board_edit(request, board_id):
    menu_ctx = _board_menu_context(request, board_id=board_id)
    blocked = _require_gai_or_render(
        request,
        'crm/boards/form.html',
        {
            'form_mode': 'edit',
            'board_id': board_id,
        },
        menu_context=menu_ctx,
    )
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)
    project_choices = build_project_choices(lookups)

    try:
        board_data = api.get(f'/boards/{board_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:board_list')
    menu_ctx = _board_menu_context(request, board_data, board_id=board_id)

    initial = {
        'name': board_data.get('name') or board_data.get('title') or '',
        'description': board_data.get('description') or '',
        'project_id': str(board_data['project_id']) if board_data.get('project_id') else '',
    }
    form = BoardForm(initial=initial, project_choices=project_choices)

    if request.method == 'POST':
        form = BoardForm(request.POST, project_choices=project_choices)
        if form.is_valid():
            try:
                api.patch(f'/boards/{board_id}', json=form.cleaned_payload(for_update=True))
                messages.success(request, 'Board atualizado.')
                return redirect('crm:board_kanban', board_id=board_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/boards/form.html', {
        'site_title': f'CRM — Editar {board_data.get("name") or board_id}',
        'form': form,
        'form_mode': 'edit',
        'board_id': board_id,
        'board': board_data,
        'lookups': lookups,
        **menu_ctx,
    })


@crm_perm_required('manage_board_columns')
def board_settings(request, board_id):
    menu_ctx = _board_menu_context(request, board_id=board_id)
    blocked = _require_gai_or_render(
        request,
        'crm/boards/settings.html',
        {'board_id': board_id},
        menu_context=menu_ctx,
    )
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    try:
        board_data = api.get(f'/boards/{board_id}')
        columns = normalize_list_response(api.get(f'/boards/{board_id}/columns'))
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:board_list')
    menu_ctx = _board_menu_context(request, board_data, board_id=board_id)

    col_kwargs = _column_form_kwargs(request)
    column_form = BoardColumnForm(**col_kwargs)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_column':
            column_form = BoardColumnForm(request.POST, **col_kwargs)
            if column_form.is_valid():
                try:
                    api.post(
                        f'/boards/{board_id}/columns',
                        json=column_form.cleaned_payload(),
                    )
                    messages.success(request, 'Coluna criada.')
                    return redirect('crm:board_settings', board_id=board_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

    return render(request, 'crm/boards/settings.html', {
        'site_title': f'CRM — Colunas — {board_data.get("name") or board_id}',
        'board': board_data,
        'board_id': board_id,
        'columns': columns,
        'column_form': column_form,
        **menu_ctx,
    })


@require_POST
@crm_perm_required('delete_board')
def ajax_board_delete(request, board_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/boards/{board_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


@require_POST
@crm_perm_required('manage_board_columns')
def ajax_board_column_update(request, board_id, column_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).patch(
            f'/boards/{board_id}/columns/{column_id}',
            json=payload,
        )
        return JsonResponse({'ok': True, 'column': result})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


@require_POST
@crm_perm_required('manage_board_access')
def ajax_board_access_update(request, board_id, access_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).patch(
            f'/boards/{board_id}/access/{access_id}',
            json=payload,
        )
        return JsonResponse({'ok': True, 'access': result})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


@crm_perm_required('view_boards')
def board_kanban(request, board_id):
    menu_ctx = _board_menu_context(request, board_id=board_id)
    blocked = _require_gai_or_render(
        request,
        'crm/boards/kanban.html',
        {'board_id': board_id},
        menu_context=menu_ctx,
    )
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    board_data = None
    columns = []
    tasks_by_status = {}
    access_me = {}
    api_error = None

    tasks_error = None
    try:
        board_data = api.get(f'/boards/{board_id}')
        columns = normalize_list_response(api.get(f'/boards/{board_id}/columns'))
        access_me = api.get(f'/boards/{board_id}/access/me') or {}
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)
        if exc.status_code == 404:
            return redirect('crm:dashboard')

    if board_data is not None and api_error is None:
        try:
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
            tasks_error = exc
            handle_crm_error(request, exc)

    can_move = access_me.get('can_move_tasks', request.user.has_perm('crm.move_task'))
    can_comment = access_me.get('can_comment', request.user.has_perm('crm.change_task'))
    menu_ctx = _board_menu_context(request, board_data, board_id=board_id)

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
        'tasks_error': tasks_error,
        **menu_ctx,
    })


@crm_perm_required('manage_board_access')
def board_access(request, board_id):
    menu_ctx = _board_menu_context(request, board_id=board_id)
    blocked = _require_gai_or_render(
        request,
        'crm/boards/access.html',
        {'board_id': board_id},
        menu_context=menu_ctx,
    )
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    try:
        board_data = api.get(f'/boards/{board_id}')
        access_list = normalize_list_response(api.get(f'/boards/{board_id}/access'))
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:dashboard')
    menu_ctx = _board_menu_context(request, board_data, board_id=board_id)

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
        **menu_ctx,
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
