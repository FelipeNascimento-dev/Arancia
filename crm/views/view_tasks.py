import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_tasks import (
    SubtaskForm,
    TaskAssigneeForm,
    TaskAttachmentForm,
    TaskCommentForm,
    TaskForm,
    TaskLinkForm,
    TaskWatcherForm,
)
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.datetime_utils import format_datetime, format_datetime_to_input
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.lookups import (
    build_board_choices,
    build_customer_choices,
    build_designation_choices,
    build_priority_choices,
    build_project_choices,
    build_status_choices,
    build_user_choices,
    fetch_crm_lookups,
    fetch_member_lookups,
)
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)
from crm.services.tasks import list_tasks

PROJECTS_MENU = {
    'current_parent_menu': 'projetos',
    'current_menu': 'projetos_tasks',
}


def _require_gai_or_render(request, template, extra_context=None):
    if get_user_gai_id(request.user) is not None:
        return None
    context = {
        'site_title': 'CRM — Tarefas',
        'missing_gai': True,
        **PROJECTS_MENU,
        **(extra_context or {}),
    }
    return render(request, template, context)


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _load_member_lookups(request):
    try:
        return fetch_member_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _task_form_choices(lookups):
    return {
        'board_choices': build_board_choices(lookups),
        'status_choices': build_status_choices(lookups),
        'priority_choices': build_priority_choices(lookups),
        'project_choices': build_project_choices(lookups),
        'customer_choices': build_customer_choices(lookups),
    }


def _enrich_task(task):
    if not isinstance(task, dict):
        return task
    task = dict(task)
    if task.get('due_at'):
        task['due_at_formatted'] = format_datetime(task['due_at'])
    if task.get('scheduled_at'):
        task['scheduled_at_formatted'] = format_datetime(task['scheduled_at'])
    return task


def _ajax_require_gai(request):
    """Retorna JsonResponse de erro se usuário sem GAI; None se OK."""
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)
    return None


def _json_crm_error(exc):
    return JsonResponse({
        'ok': False,
        'error': str(exc.detail or exc),
    }, status=exc.status_code or 502)


def _board_access_for_task(user, board_id):
    if not board_id:
        return {}
    try:
        return CrmApiClient(user).get(f'/boards/{board_id}/access/me') or {}
    except CrmApiError:
        return {}


def _can_comment_on_task(user, task_data, access_me=None):
    if not user.has_perm('crm.change_task'):
        return False
    board_id = task_data.get('board_id') if isinstance(task_data, dict) else None
    if board_id:
        access = access_me if access_me is not None else _board_access_for_task(user, board_id)
        return bool(access.get('can_comment', user.has_perm('crm.change_task')))
    return True


def _require_can_comment_json(user, task_id):
    try:
        task_data = CrmApiClient(user).get(f'/tasks/{task_id}')
    except CrmApiError as exc:
        return None, JsonResponse({'ok': False, 'error': str(exc.detail or exc)}, status=exc.status_code or 502)
    if not _can_comment_on_task(user, task_data):
        return None, JsonResponse({'ok': False, 'error': 'Sem permissão para comentar nesta tarefa.'}, status=403)
    return task_data, None


@crm_perm_required('view_tasks')
def task_list(request):
    blocked = _require_gai_or_render(request, 'crm/tasks/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    params = {'skip': skip, 'limit': limit}
    board_id = request.GET.get('board_id')
    project_id = request.GET.get('project_id')
    if board_id:
        params['board_id'] = board_id
    if project_id:
        params['project_id'] = project_id

    tasks = []
    api_error = None
    tasks_scope_fallback = False
    try:
        raw, tasks_scope_fallback = list_tasks(request.user, params=params)
        tasks = [_enrich_task(t) for t in normalize_list_response(raw)]
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    lookups, _ = _load_lookups(request)
    pagination = build_pagination_context(skip, limit, tasks)
    return render(request, 'crm/tasks/list.html', {
        'site_title': 'CRM — Tarefas',
        'tasks': tasks,
        'pagination': pagination,
        'api_error': api_error,
        'tasks_scope_fallback': tasks_scope_fallback,
        'lookups': lookups,
        'filter_board_id': board_id,
        'filter_project_id': project_id,
        **PROJECTS_MENU,
    })


@crm_perm_required('view_tasks')
def task_my(request):
    blocked = _require_gai_or_render(request, 'crm/tasks/my.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    params = {'skip': skip, 'limit': limit}
    if request.GET.get('overdue_only') == 'true':
        params['overdue_only'] = 'true'

    tasks = []
    api_error = None
    try:
        raw = CrmApiClient(request.user).get('/tasks/my/', params=params)
        tasks = [_enrich_task(t) for t in normalize_list_response(raw)]
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    pagination = build_pagination_context(skip, limit, tasks)
    return render(request, 'crm/tasks/my.html', {
        'site_title': 'CRM — Minhas tarefas',
        'tasks': tasks,
        'pagination': pagination,
        'api_error': api_error,
        'overdue_only': request.GET.get('overdue_only') == 'true',
        **PROJECTS_MENU,
        'current_menu': 'projetos_my_tasks',
    })


@crm_perm_required('view_tasks')
def task_calendar(request):
    blocked = _require_gai_or_render(request, 'crm/tasks/calendar.html')
    if blocked:
        return blocked

    tasks = []
    api_error = None
    tasks_scope_fallback = False
    try:
        raw, tasks_scope_fallback = list_tasks(
            request.user,
            params={'scheduled_only': 'true', 'limit': 200},
        )
        tasks = [_enrich_task(t) for t in normalize_list_response(raw)]
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    return render(request, 'crm/tasks/calendar.html', {
        'site_title': 'CRM — Calendário de tarefas',
        'tasks': tasks,
        'api_error': api_error,
        'tasks_scope_fallback': tasks_scope_fallback,
        **PROJECTS_MENU,
        'current_menu': 'projetos_calendar',
    })


@crm_perm_required('add_task')
def task_new(request):
    blocked = _require_gai_or_render(request, 'crm/tasks/form.html', {'form_mode': 'new'})
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    choices = _task_form_choices(lookups)
    initial_board = request.GET.get('board_id')
    initial_project = request.GET.get('project_id')
    initial = {}
    if initial_board:
        initial['board_id'] = initial_board
    if initial_project:
        initial['project_id'] = initial_project

    if request.method == 'POST':
        form = TaskForm(request.POST, **choices)
        if form.is_valid():
            try:
                result = CrmApiClient(request.user).post('/tasks/', json=form.cleaned_payload())
                task_id = result.get('id') if isinstance(result, dict) else None
                messages.success(request, 'Tarefa criada com sucesso.')
                if task_id:
                    return redirect('crm:task_detail', task_id=task_id)
                return redirect('crm:task_list')
            except CrmApiError as exc:
                handle_crm_error(request, exc)
    else:
        form = TaskForm(initial=initial, **choices)

    return render(request, 'crm/tasks/form.html', {
        'site_title': 'CRM — Nova tarefa',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@crm_perm_required('view_tasks')
def task_detail(request, task_id):
    blocked = _require_gai_or_render(request, 'crm/tasks/detail.html')
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)
    members_lookup, _ = _load_member_lookups(request)

    try:
        task_data = api.get(f'/tasks/{task_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:task_list')

    task_data = _enrich_task(task_data)
    subtasks = task_data.get('subtasks') or []
    subtasks = [_enrich_task(s) for s in subtasks]

    board_id = task_data.get('board_id')
    access_me = _board_access_for_task(request.user, board_id) if board_id else {}
    can_comment = _can_comment_on_task(request.user, task_data, access_me)

    linked_tasks = task_data.get('linked_tasks') or []
    watchers = task_data.get('watchers') or []
    move_history = []
    try:
        move_history = normalize_list_response(api.get(f'/tasks/{task_id}/move-history'))
    except CrmApiError:
        move_history = []

    comment_form = TaskCommentForm(prefix='comment')
    assignee_form = TaskAssigneeForm(
        prefix='assignee',
        user_choices=build_user_choices(members_lookup),
        designation_choices=build_designation_choices(members_lookup),
    )
    attachment_form = TaskAttachmentForm(prefix='attachment')
    subtask_form = SubtaskForm(prefix='subtask')
    link_form = TaskLinkForm(prefix='link')
    watcher_form = TaskWatcherForm(
        prefix='watcher',
        user_choices=build_user_choices(members_lookup),
        designation_choices=build_designation_choices(members_lookup),
    )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_comment' and can_comment:
            comment_form = TaskCommentForm(request.POST, prefix='comment')
            if comment_form.is_valid():
                try:
                    api.post(
                        f'/tasks/{task_id}/comments',
                        json={'content': comment_form.cleaned_data['content']},
                    )
                    messages.success(request, 'Comentário adicionado.')
                    return redirect('crm:task_detail', task_id=task_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

        elif action == 'add_link' and request.user.has_perm('crm.change_task'):
            link_form = TaskLinkForm(request.POST, prefix='link')
            if link_form.is_valid():
                try:
                    api.post(f'/tasks/{task_id}/links', json=link_form.cleaned_payload())
                    messages.success(request, 'Vínculo criado.')
                    return redirect('crm:task_detail', task_id=task_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

        elif action == 'add_watcher' and request.user.has_perm('crm.manage_watchers'):
            watcher_form = TaskWatcherForm(
                request.POST,
                prefix='watcher',
                user_choices=build_user_choices(members_lookup),
                designation_choices=build_designation_choices(members_lookup),
            )
            if watcher_form.is_valid():
                try:
                    api.post(f'/tasks/{task_id}/watchers', json=watcher_form.cleaned_payload())
                    messages.success(request, 'Observador adicionado.')
                    return redirect('crm:task_detail', task_id=task_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

        elif action == 'add_assignee' and request.user.has_perm('crm.assign_task'):
            assignee_form = TaskAssigneeForm(
                request.POST,
                prefix='assignee',
                user_choices=build_user_choices(members_lookup),
                designation_choices=build_designation_choices(members_lookup),
            )
            if assignee_form.is_valid():
                try:
                    api.post(f'/tasks/{task_id}/assignees', json=assignee_form.cleaned_payload())
                    messages.success(request, 'Responsável atribuído.')
                    return redirect('crm:task_detail', task_id=task_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

        elif action == 'add_subtask' and request.user.has_perm('crm.add_task'):
            subtask_form = SubtaskForm(request.POST, prefix='subtask')
            if subtask_form.is_valid():
                try:
                    api.post(
                        f'/tasks/{task_id}/subtasks',
                        json={'title': subtask_form.cleaned_data['title']},
                    )
                    messages.success(request, 'Subtarefa criada.')
                    return redirect('crm:task_detail', task_id=task_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

        elif action == 'watch':
            try:
                api.post(f'/tasks/{task_id}/watch', json={})
                messages.success(request, 'Você está observando esta tarefa.')
                return redirect('crm:task_detail', task_id=task_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/tasks/detail.html', {
        'site_title': f'CRM — {task_data.get("title") or task_id}',
        'task': task_data,
        'task_id': task_id,
        'subtasks': subtasks,
        'linked_tasks': linked_tasks,
        'watchers': watchers,
        'move_history': move_history,
        'can_comment': can_comment,
        'access_me': access_me,
        'comment_form': comment_form,
        'assignee_form': assignee_form,
        'attachment_form': attachment_form,
        'subtask_form': subtask_form,
        'link_form': link_form,
        'watcher_form': watcher_form,
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@crm_perm_required('change_task')
def task_edit(request, task_id):
    blocked = _require_gai_or_render(request, 'crm/tasks/form.html', {
        'form_mode': 'edit',
        'task_id': task_id,
    })
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)
    choices = _task_form_choices(lookups)

    try:
        task_data = api.get(f'/tasks/{task_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:task_list')

    initial = {
        'title': task_data.get('title') or '',
        'description': task_data.get('description') or '',
        'board_id': str(task_data['board_id']) if task_data.get('board_id') else '',
        'status_id': str(task_data['status_id']) if task_data.get('status_id') else '',
        'priority_id': str(task_data['priority_id']) if task_data.get('priority_id') else '',
        'project_id': str(task_data['project_id']) if task_data.get('project_id') else '',
        'customer_gai_id': str(task_data['customer_gai_id']) if task_data.get('customer_gai_id') else '',
        'due_at': format_datetime_to_input(task_data.get('due_at')),
        'scheduled_at': format_datetime_to_input(task_data.get('scheduled_at')),
        'is_active': task_data.get('is_active', True),
    }

    form = TaskForm(initial=initial, lock_board=bool(task_data.get('board_id')), **choices)

    if request.method == 'POST':
        form = TaskForm(request.POST, lock_board=bool(task_data.get('board_id')), **choices)
        if form.is_valid():
            try:
                api.patch(f'/tasks/{task_id}', json=form.cleaned_payload(for_update=True))
                messages.success(request, 'Tarefa atualizada com sucesso.')
                return redirect('crm:task_detail', task_id=task_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/tasks/form.html', {
        'site_title': f'CRM — Editar {task_data.get("title") or task_id}',
        'form': form,
        'form_mode': 'edit',
        'task_id': task_id,
        'task': task_data,
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@require_POST
@crm_perm_required('move_task')
def ajax_task_move(request, task_id):
    blocked = _ajax_require_gai(request)
    if blocked:
        return blocked

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = {
            'status_id': request.POST.get('status_id'),
            'kanban_position': request.POST.get('kanban_position'),
        }

    if not payload.get('status_id'):
        return JsonResponse({'ok': False, 'error': 'status_id é obrigatório.'}, status=400)

    try:
        result = CrmApiClient(request.user).patch(
            f'/tasks/{task_id}/move',
            json={
                'status_id': payload['status_id'],
                'kanban_position': int(payload.get('kanban_position', 0)),
            },
        )
        return JsonResponse({'ok': True, 'task': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('assign_task')
def ajax_task_assign(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).post(
            f'/tasks/{task_id}/assignees',
            json=payload,
        )
        return JsonResponse({'ok': True, 'assignee': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('change_task')
def ajax_task_comment(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    _, blocked = _require_can_comment_json(request.user, task_id)
    if blocked:
        return blocked

    content = request.POST.get('content')
    if not content:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
            content = payload.get('content') or payload.get('body')
        except json.JSONDecodeError:
            content = None
    if not content:
        return JsonResponse({'ok': False, 'error': 'Comentário vazio.'}, status=400)

    try:
        result = CrmApiClient(request.user).post(
            f'/tasks/{task_id}/comments',
            json={'content': content},
        )
        return JsonResponse({'ok': True, 'comment': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('change_task')
def ajax_task_attachment(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    _, blocked = _require_can_comment_json(request.user, task_id)
    if blocked:
        return blocked

    uploaded = request.FILES.get('file')
    if not uploaded:
        return JsonResponse({'ok': False, 'error': 'Nenhum arquivo enviado.'}, status=400)

    try:
        uploaded.seek(0)
        result = CrmApiClient(request.user).post_multipart(
            f'/tasks/{task_id}/attachments',
            files={
                'file': (
                    uploaded.name,
                    uploaded.read(),
                    uploaded.content_type or 'application/octet-stream',
                ),
            },
        )
        return JsonResponse({'ok': True, 'attachment': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('view_tasks')
def ajax_task_watch(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    if not request.user.has_perm('crm.manage_watchers'):
        try:
            CrmApiClient(request.user).post(f'/tasks/{task_id}/watch', json={})
            return JsonResponse({'ok': True})
        except CrmApiError as exc:
            return _json_crm_error(exc)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()
    try:
        result = CrmApiClient(request.user).post(
            f'/tasks/{task_id}/watch',
            json=payload or {},
        )
        return JsonResponse({'ok': True, 'watch': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('delete_task')
def ajax_task_delete(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('change_task')
def ajax_task_links(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).post(f'/tasks/{task_id}/links', json=payload)
        return JsonResponse({'ok': True, 'link': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('change_task')
def ajax_task_link_delete(request, task_id, link_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}/links/{link_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('assign_task')
def ajax_task_assignee_update(request, task_id, assignee_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).patch(
            f'/tasks/{task_id}/assignees/{assignee_id}',
            json=payload,
        )
        return JsonResponse({'ok': True, 'assignee': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('assign_task')
def ajax_task_assignee_delete(request, task_id, assignee_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}/assignees/{assignee_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('view_tasks')
def ajax_task_watcher_add(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    if not request.user.has_perm('crm.manage_watchers'):
        return JsonResponse({'ok': False, 'error': 'Sem permissão para gerenciar observadores.'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).post(f'/tasks/{task_id}/watchers', json=payload)
        return JsonResponse({'ok': True, 'watcher': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('view_tasks')
def ajax_task_watcher_delete(request, task_id, watcher_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    if not request.user.has_perm('crm.manage_watchers'):
        return JsonResponse({'ok': False, 'error': 'Sem permissão para gerenciar observadores.'}, status=403)

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}/watchers/{watcher_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@crm_perm_required('view_tasks')
def ajax_task_move_history(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        history = normalize_list_response(
            CrmApiClient(request.user).get(f'/tasks/{task_id}/move-history')
        )
        return JsonResponse({'ok': True, 'history': history})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('add_task')
def ajax_task_subtask(request, task_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).post(
            f'/tasks/{task_id}/subtasks',
            json={'title': payload.get('title', '')},
        )
        return JsonResponse({'ok': True, 'subtask': result})
    except CrmApiError as exc:
        return _json_crm_error(exc)
