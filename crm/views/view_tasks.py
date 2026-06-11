import json

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from crm.decorators import crm_access_required, crm_perm_required
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
from crm.services.datetime_utils import format_datetime, format_datetime_to_input
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.gates import ajax_require_gai, require_gai_or_render
from crm.services.lookups import (
    build_board_choices,
    build_customer_choices,
    build_designation_choices,
    build_gai_requester_choices,
    build_group_choices,
    build_priority_choices,
    build_project_choices,
    build_status_choices,
    build_user_choices,
    extract_requester_gai_ids,
    fetch_board_status_choices,
    fetch_crm_lookups,
    fetch_gais,
    fetch_groups,
    build_status_choices_for_board,
    resolve_member_lookups,
)
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)
from crm.services.calendar import (
    build_calendar_fetch_params,
    parse_fc_range,
    tasks_to_calendar_events,
)
from crm.services.recurrences import (
    recurrence_start_at_from_form,
    recurrence_start_is_due,
    run_scheduler_for_template,
    validate_board_can_create,
)
from crm.services.tasks import enrich_move_history, enrich_task, list_tasks, normalize_task_fields

PROJECTS_MENU = {
    'current_parent_menu': 'projetos',
    'current_menu': 'projetos_tasks',
}


def _require_gai_or_render(request, template, extra_context=None):
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Tarefas',
        menu_context=PROJECTS_MENU,
        extra_context=extra_context,
    )


def _load_requester_form_choices(user):
    """Grupos e GAIs iniciais para demandantes de tarefa de projeto."""
    try:
        groups_raw = fetch_groups(user)
        gais_raw = fetch_gais(user)
    except CrmApiError:
        return [], []
    return build_group_choices(groups_raw), build_gai_requester_choices(gais_raw)


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _load_member_lookups(request):
    return resolve_member_lookups(request.user), None


def _task_form_choices(lookups, user=None, *, board_id=None):
    priority_choices = build_priority_choices(lookups)
    project_choices = build_project_choices(lookups)

    if user is not None and not priority_choices:
        try:
            raw = CrmApiClient(user).get('/prioritys/', params={'limit': 200})
            priority_choices = build_priority_choices({'prioritys': normalize_list_response(raw)})
        except CrmApiError:
            pass

    if user is not None and not project_choices:
        try:
            raw = CrmApiClient(user).get('/projects/', params={'limit': 200})
            project_choices = build_project_choices({'projects': normalize_list_response(raw)})
        except CrmApiError:
            pass

    status_choices = build_status_choices_for_board(user, lookups, board_id) if user else build_status_choices(lookups, board_id=board_id)
    if board_id and user is not None and not status_choices:
        try:
            status_choices = fetch_board_status_choices(user, board_id)
        except CrmApiError:
            pass

    return {
        'board_choices': build_board_choices(lookups),
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'project_choices': project_choices,
        'customer_choices': build_customer_choices(lookups),
    }


def _redirect_after_task_create(request, result, *, is_recurring=False):
    if isinstance(result, dict):
        task_id = (
            result.get('task_id')
            or result.get('created_task_id')
            or result.get('initial_task_id')
            or (result.get('id') if not is_recurring else None)
        )
        if task_id:
            return redirect('crm:task_detail', task_id=task_id)
        if is_recurring and result.get('id'):
            return redirect('crm:recurrence_detail', recurrence_id=result['id'])
    return redirect('crm:task_list')


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
        tasks = [enrich_task(t) for t in normalize_list_response(raw)]
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
        tasks = [enrich_task(t) for t in normalize_list_response(raw)]
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

    return render(request, 'crm/tasks/calendar.html', {
        'site_title': 'CRM — Calendário de tarefas',
        **PROJECTS_MENU,
        'current_menu': 'projetos_calendar',
    })


@crm_perm_required('view_tasks')
def ajax_task_calendar_events(request):
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    start, end = parse_fc_range(request.GET.get('start'), request.GET.get('end'))
    include_due = request.GET.get('include_due') == '1'
    params = build_calendar_fetch_params(start, end, include_due=include_due)

    try:
        raw, _tasks_scope_fallback = list_tasks(request.user, params=params)
        tasks = normalize_list_response(raw)
    except CrmApiError as exc:
        return _json_crm_error(exc)

    events = tasks_to_calendar_events(
        tasks,
        start=start,
        end=end,
        include_due=include_due,
    )
    return JsonResponse(events, safe=False)


@crm_access_required
def task_new(request):
    user = request.user
    can_add_task = user.has_perm('crm.add_task')
    can_add_recurrence = user.has_perm('crm.add_task_recurrence')
    if not can_add_task and not can_add_recurrence:
        raise PermissionDenied

    blocked = _require_gai_or_render(request, 'crm/tasks/form.html', {'form_mode': 'new'})
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    initial_board = request.GET.get('board_id')
    initial_project = request.GET.get('project_id')
    board_for_choices = (
        request.POST.get('board_id') if request.method == 'POST' else initial_board
    )
    choices = _task_form_choices(lookups, request.user, board_id=board_for_choices)
    group_choices, requester_gai_choices = _load_requester_form_choices(request.user)
    initial = {}
    if initial_board:
        initial['board_id'] = initial_board
    if initial_project:
        initial['project_id'] = initial_project
    scheduled_at = (request.GET.get('scheduled_at') or '').strip()
    if scheduled_at:
        initial['scheduled_at'] = scheduled_at

    show_task_kind = can_add_task and can_add_recurrence
    recurrence_only = can_add_recurrence and not can_add_task
    if recurrence_only or request.GET.get('recurring') in ('1', 'true', 'yes'):
        initial['task_kind'] = 'recurring'

    show_requesters = True
    group_choices, requester_gai_choices = _load_requester_form_choices(request.user)
    form_options = {
        **choices,
        'show_task_kind': show_task_kind,
        'recurrence_only': recurrence_only,
        'show_requesters': show_requesters,
        'group_choices': group_choices,
        'requester_gai_choices': requester_gai_choices,
    }

    if request.method == 'POST':
        form = TaskForm(request.POST, **form_options)
        if form.is_valid():
            board_id = form.cleaned_data.get('board_id')
            board_error = validate_board_can_create(request.user, board_id)
            if board_error:
                form.add_error('board_id', board_error)
            else:
                api = CrmApiClient(request.user)
                try:
                    if form.is_recurring():
                        if not can_add_recurrence:
                            raise PermissionDenied
                        result = api.post(
                            '/task-recurrences/',
                            json=form.cleaned_recurrence_payload(),
                        )
                        template_id = result.get('id') if isinstance(result, dict) else None
                        start_at = recurrence_start_at_from_form(form.cleaned_data)
                        task_id = None
                        if template_id and recurrence_start_is_due(start_at):
                            task_id = run_scheduler_for_template(template_id)
                        if task_id:
                            messages.success(
                                request,
                                'Template criado. Primeira ocorrência já disponível no Kanban.',
                            )
                            return redirect('crm:task_detail', task_id=task_id)
                        if template_id:
                            msg = 'Tarefa recorrente criada.'
                            next_run = (result or {}).get('next_run_at')
                            if next_run and not recurrence_start_is_due(start_at):
                                msg += (
                                    f' A primeira ocorrência será gerada em '
                                    f'{format_datetime(next_run)}.'
                                )
                            messages.success(request, msg)
                            return redirect('crm:recurrence_detail', recurrence_id=template_id)
                        return _redirect_after_task_create(request, result, is_recurring=True)
                    if not can_add_task:
                        raise PermissionDenied
                    result = api.post('/tasks/', json=form.cleaned_payload())
                    messages.success(request, 'Tarefa criada com sucesso.')
                    return _redirect_after_task_create(request, result, is_recurring=False)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)
    else:
        form = TaskForm(initial=initial, **form_options)

    return render(request, 'crm/tasks/form.html', {
        'site_title': 'CRM — Nova tarefa',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        'can_add_task': can_add_task,
        'can_add_recurrence': can_add_recurrence,
        'show_task_kind': show_task_kind,
        'recurrence_only': recurrence_only,
        'show_requesters': show_requesters,
        'ajax_lookup_gais_url': reverse('crm:ajax_lookup_gais'),
        'ajax_board_statuses_url': reverse(
            'crm:ajax_board_status_choices',
            kwargs={'board_id': '00000000-0000-0000-0000-000000000000'},
        ),
        'all_status_choices': build_status_choices(lookups),
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

    task_data = enrich_task(task_data)
    subtasks = task_data.get('subtasks') or []
    subtasks = [enrich_task(s) for s in subtasks]

    board_id = task_data.get('board_id')
    access_me = _board_access_for_task(request.user, board_id) if board_id else {}
    can_comment = _can_comment_on_task(request.user, task_data, access_me)

    linked_tasks = task_data.get('linked_tasks') or []
    watchers = task_data.get('watchers') or []
    move_history = []
    try:
        move_history = enrich_move_history(
            normalize_list_response(api.get(f'/tasks/{task_id}/move-history'))
        )
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

    try:
        task_data = api.get(f'/tasks/{task_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:task_list')

    task_fields = normalize_task_fields(task_data)
    board_for_choices = (
        request.POST.get('board_id') if request.method == 'POST' else task_fields.get('board_id')
    )
    choices = _task_form_choices(lookups, request.user, board_id=board_for_choices)

    initial = {
        'title': task_fields.get('title') or '',
        'description': task_fields.get('description') or '',
        'board_id': str(task_fields['board_id']) if task_fields.get('board_id') else '',
        'status_id': str(task_fields['status_id']) if task_fields.get('status_id') else '',
        'priority_id': str(task_fields['priority_id']) if task_fields.get('priority_id') else '',
        'project_id': str(task_fields['project_id']) if task_fields.get('project_id') else '',
        'customer_gai_id': str(task_fields['customer_gai_id']) if task_fields.get('customer_gai_id') else '',
        'requester_gai_ids': extract_requester_gai_ids(task_fields),
        'due_at': format_datetime_to_input(task_fields.get('due_at')),
        'scheduled_at': format_datetime_to_input(task_fields.get('scheduled_at')),
        'is_active': task_fields.get('is_active', True),
    }

    show_requesters = bool(task_data.get('project_id'))
    group_choices, requester_gai_choices = _load_requester_form_choices(request.user)
    form_kwargs = {
        **choices,
        'lock_board': bool(task_data.get('board_id')),
        'show_requesters': show_requesters,
        'group_choices': group_choices if show_requesters else [],
        'requester_gai_choices': requester_gai_choices if show_requesters else [],
    }

    form = TaskForm(initial=initial, **form_kwargs)

    if request.method == 'POST':
        form = TaskForm(request.POST, **form_kwargs)
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
        'show_requesters': show_requesters,
        'ajax_lookup_gais_url': reverse('crm:ajax_lookup_gais'),
        'ajax_board_statuses_url': reverse(
            'crm:ajax_board_status_choices',
            kwargs={'board_id': '00000000-0000-0000-0000-000000000000'},
        ),
        'all_status_choices': build_status_choices(lookups),
        **PROJECTS_MENU,
    })


@require_POST
@crm_perm_required('move_task')
def ajax_task_move(request, task_id):
    blocked = ajax_require_gai(request)
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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('change_task')
def ajax_task_links(request, task_id):
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}/links/{link_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('assign_task')
def ajax_task_assignee_update(request, task_id, assignee_id):
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}/assignees/{assignee_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@require_POST
@crm_perm_required('view_tasks')
def ajax_task_watcher_add(request, task_id):
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    if not request.user.has_perm('crm.manage_watchers'):
        return JsonResponse({'ok': False, 'error': 'Sem permissão para gerenciar observadores.'}, status=403)

    try:
        CrmApiClient(request.user).delete(f'/tasks/{task_id}/watchers/{watcher_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return _json_crm_error(exc)


@crm_perm_required('view_tasks')
def ajax_task_move_history(request, task_id):
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

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
