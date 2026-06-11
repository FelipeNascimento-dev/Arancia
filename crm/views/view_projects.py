from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_projects import ProjectForm, ProjectMemberForm
from crm.services.client import CrmApiClient
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.gates import require_gai_or_render
from crm.services.lookups import (
    build_customer_choices,
    build_designation_choices,
    build_team_gai_choices,
    build_user_choices,
    fetch_crm_lookups,
    resolve_member_lookups,
    fetch_team_gais,
)
from crm.services.refs import customer_ref_label
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)
from crm.services.tasks import enrich_task, list_tasks

PROJECTS_MENU = {
    'current_parent_menu': 'projetos',
    'current_menu': 'projetos_projects',
}


def _require_gai_or_render(request, template, extra_context=None):
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Projetos',
        menu_context=PROJECTS_MENU,
        extra_context=extra_context,
    )


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _member_form_choices(request):
    members_lookup = resolve_member_lookups(request.user)
    try:
        team_gais = fetch_team_gais(request.user)
    except CrmApiError:
        team_gais = []
    return {
        'user_choices': build_user_choices(members_lookup),
        'designation_choices': build_designation_choices(members_lookup),
        'team_gai_choices': build_team_gai_choices(
            team_gais if isinstance(team_gais, list) else (team_gais or {}).get('items') or team_gais
        ),
    }



@crm_perm_required('view_tasks')
def project_tasks(request, project_id):
    blocked = _require_gai_or_render(
        request,
        'crm/projects/tasks.html',
        {'project_id': project_id, 'current_menu': 'projetos_projects'},
    )
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    try:
        project_data = api.get(f'/projects/{project_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:project_list')

    skip, limit = get_pagination_params(request)
    params = {'skip': skip, 'limit': limit, 'project_id': str(project_id)}
    tasks = []
    api_error = None
    tasks_scope_fallback = False
    try:
        raw, tasks_scope_fallback = list_tasks(request.user, params=params)
        tasks = [enrich_task(t) for t in normalize_list_response(raw)]
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    default_board_id = project_data.get('default_board_id') or project_data.get('board_id')

    return render(request, 'crm/projects/tasks.html', {
        'site_title': f'CRM — Tarefas — {project_data.get("name") or project_id}',
        'project': project_data,
        'project_id': project_id,
        'tasks': tasks,
        'pagination': build_pagination_context(skip, limit, tasks),
        'api_error': api_error,
        'tasks_scope_fallback': tasks_scope_fallback,
        'default_board_id': default_board_id,
        **PROJECTS_MENU,
    })


@crm_perm_required('view_projects')
def project_list(request):
    blocked = _require_gai_or_render(request, 'crm/projects/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    projects = []
    api_error = None
    lookups, _ = _load_lookups(request)

    try:
        raw = CrmApiClient(request.user).get('/projects/', params={'skip': skip, 'limit': limit})
        projects = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    pagination = build_pagination_context(skip, limit, projects)
    return render(request, 'crm/projects/list.html', {
        'site_title': 'CRM — Projetos',
        'projects': projects,
        'pagination': pagination,
        'api_error': api_error,
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@crm_perm_required('add_project')
def project_new(request):
    blocked = _require_gai_or_render(request, 'crm/projects/form.html', {'form_mode': 'new'})
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    customer_choices = build_customer_choices(lookups)

    if request.method == 'POST':
        form = ProjectForm(request.POST, customer_choices=customer_choices)
        if form.is_valid():
            try:
                result = CrmApiClient(request.user).post(
                    '/projects/',
                    json=form.cleaned_payload(),
                )
                project_id = result.get('id') if isinstance(result, dict) else None
                messages.success(request, 'Projeto criado com sucesso.')
                if project_id:
                    return redirect('crm:project_detail', project_id=project_id)
                return redirect('crm:project_list')
            except CrmApiError as exc:
                handle_crm_error(request, exc)
    else:
        form = ProjectForm(customer_choices=customer_choices)

    return render(request, 'crm/projects/form.html', {
        'site_title': 'CRM — Novo projeto',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@crm_perm_required('view_projects')
def project_detail(request, project_id):
    blocked = _require_gai_or_render(request, 'crm/projects/detail.html')
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    try:
        project_data = CrmApiClient(request.user).get(f'/projects/{project_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:project_list')

    return render(request, 'crm/projects/detail.html', {
        'site_title': f'CRM — {project_data.get("name") or project_id}',
        'project': project_data,
        'project_id': project_id,
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@crm_perm_required('change_project')
def project_edit(request, project_id):
    blocked = _require_gai_or_render(request, 'crm/projects/form.html', {
        'form_mode': 'edit',
        'project_id': project_id,
    })
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)
    customer_choices = build_customer_choices(lookups)

    try:
        project_data = api.get(f'/projects/{project_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:project_list')

    gai_id = project_data.get('customer_gai_id')
    gai_label = customer_ref_label(project_data, lookups=lookups)
    if gai_id and not any(str(c[0]) == str(gai_id) for c in customer_choices):
        customer_choices = [(str(gai_id), gai_label)] + customer_choices

    initial = {
        'name': project_data.get('name') or '',
        'code': project_data.get('code') or '',
        'description': project_data.get('description') or '',
        'customer_gai_id': str(gai_id) if gai_id else '',
        'is_active': project_data.get('is_active', True),
    }
    form = ProjectForm(initial=initial, customer_choices=customer_choices, lock_customer=bool(gai_id))

    if request.method == 'POST':
        form = ProjectForm(
            request.POST,
            customer_choices=customer_choices,
            lock_customer=bool(gai_id),
        )
        if form.is_valid():
            try:
                api.patch(f'/projects/{project_id}', json=form.cleaned_payload(for_update=True))
                messages.success(request, 'Projeto atualizado com sucesso.')
                return redirect('crm:project_detail', project_id=project_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/projects/form.html', {
        'site_title': f'CRM — Editar {project_data.get("name") or project_id}',
        'form': form,
        'form_mode': 'edit',
        'project_id': project_id,
        'project': project_data,
        'lookups': lookups,
        **PROJECTS_MENU,
    })


@crm_perm_required('manage_project_members')
def project_members(request, project_id):
    blocked = _require_gai_or_render(request, 'crm/projects/members.html', {'project_id': project_id})
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    try:
        project_data = api.get(f'/projects/{project_id}')
        members = api.get(f'/projects/{project_id}/members')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:project_list')

    members_list = normalize_list_response(members) if members is not None else []
    member_choices = _member_form_choices(request)
    member_form = ProjectMemberForm(**member_choices)

    if request.method == 'POST':
        member_form = ProjectMemberForm(request.POST, **member_choices)
        if member_form.is_valid():
            try:
                api.post(
                    f'/projects/{project_id}/members',
                    json=member_form.cleaned_payload(),
                )
                messages.success(request, 'Membro adicionado ao projeto.')
                return redirect('crm:project_members', project_id=project_id)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/projects/members.html', {
        'site_title': f'CRM — Membros — {project_data.get("name") or project_id}',
        'project': project_data,
        'project_id': project_id,
        'members': members_list,
        'member_form': member_form,
        **PROJECTS_MENU,
    })


@require_POST
@crm_perm_required('manage_project_members')
def ajax_project_member_update(request, project_id, member_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    import json
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = request.POST.dict()

    try:
        result = CrmApiClient(request.user).patch(
            f'/projects/{project_id}/members/{member_id}',
            json=payload,
        )
        return JsonResponse({'ok': True, 'member': result})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


@require_POST
@crm_perm_required('manage_project_members')
def ajax_project_member_delete(request, project_id, member_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/projects/{project_id}/members/{member_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


@require_POST
@crm_perm_required('delete_project')
def ajax_project_delete(request, project_id):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/projects/{project_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)
