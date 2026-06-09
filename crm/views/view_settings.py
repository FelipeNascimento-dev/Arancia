from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_settings import PriorityForm, ServiceTypeForm, StatusTaskForm
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.pagination import (
    build_pagination_context,
    find_record_by_id,
    get_pagination_params,
    normalize_list_response,
)

CRM_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_settings',
}


def _require_gai_or_render(request, template, extra_context=None):
    if get_user_gai_id(request.user) is not None:
        return None
    context = {
        'site_title': 'CRM — Configurações',
        'missing_gai': True,
        **CRM_MENU,
        **(extra_context or {}),
    }
    return render(request, template, context)


def _settings_list(request, *, api_path, template, title, perm_manage):
    blocked = _require_gai_or_render(request, template)
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    items = []
    api_error = None
    try:
        raw = CrmApiClient(request.user).get(api_path, params={'skip': skip, 'limit': limit})
        items = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    return render(request, template, {
        'site_title': title,
        'items': items,
        'pagination': build_pagination_context(skip, limit, items),
        'api_error': api_error,
        'can_manage': request.user.has_perm(f'crm.{perm_manage}'),
        **CRM_MENU,
    })


def _settings_form(
    request,
    *,
    api_path,
    template,
    form_class,
    title_new,
    title_edit,
    list_url_name,
    record_id=None,
):
    blocked = _require_gai_or_render(request, template, {'form_mode': 'edit' if record_id else 'new'})
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    initial = {}
    record_data = None

    if record_id:
        try:
            record_data = find_record_by_id(request.user, api_path, record_id)
            if not record_data:
                raise CrmApiError('Registro não encontrado.', status_code=404)
            initial = {k: record_data.get(k) for k in form_class.base_fields}
        except CrmApiError as exc:
            handle_crm_error(request, exc)
            return redirect(list_url_name)

    form = form_class(initial=initial)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            try:
                if record_id:
                    api.patch(f'{api_path.rstrip("/")}/{record_id}', json=form.cleaned_payload())
                    messages.success(request, 'Registro atualizado.')
                else:
                    api.post(api_path, json=form.cleaned_payload())
                    messages.success(request, 'Registro criado.')
                return redirect(list_url_name)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, template, {
        'site_title': title_edit if record_id else title_new,
        'form': form,
        'form_mode': 'edit' if record_id else 'new',
        'record_id': record_id,
        'record': record_data,
        **CRM_MENU,
    })


@crm_perm_required('view_settings')
def settings_index(request):
    blocked = _require_gai_or_render(request, 'crm/settings/index.html')
    if blocked:
        return blocked
    return render(request, 'crm/settings/index.html', {
        'site_title': 'CRM — Configurações',
        **CRM_MENU,
    })


@crm_perm_required('view_settings')
def settings_service_types(request):
    return _settings_list(
        request,
        api_path='/service-types/',
        template='crm/settings/service_types.html',
        title='CRM — Tipos de serviço',
        perm_manage='manage_service_types',
    )


@crm_perm_required('manage_service_types')
def settings_service_type_new(request):
    return _settings_form(
        request,
        api_path='/service-types/',
        template='crm/settings/service_type_form.html',
        form_class=ServiceTypeForm,
        title_new='CRM — Novo tipo de serviço',
        title_edit='CRM — Editar tipo de serviço',
        list_url_name='crm:settings_service_types',
    )


@crm_perm_required('manage_service_types')
def settings_service_type_edit(request, record_id):
    return _settings_form(
        request,
        api_path='/service-types/',
        template='crm/settings/service_type_form.html',
        form_class=ServiceTypeForm,
        title_new='CRM — Novo tipo de serviço',
        title_edit='CRM — Editar tipo de serviço',
        list_url_name='crm:settings_service_types',
        record_id=record_id,
    )


@crm_perm_required('view_settings')
def settings_priorities(request):
    return _settings_list(
        request,
        api_path='/prioritys/',
        template='crm/settings/priorities.html',
        title='CRM — Prioridades',
        perm_manage='manage_priorities',
    )


@crm_perm_required('manage_priorities')
def settings_priority_new(request):
    return _settings_form(
        request,
        api_path='/prioritys/',
        template='crm/settings/priority_form.html',
        form_class=PriorityForm,
        title_new='CRM — Nova prioridade',
        title_edit='CRM — Editar prioridade',
        list_url_name='crm:settings_priorities',
    )


@crm_perm_required('manage_priorities')
def settings_priority_edit(request, record_id):
    return _settings_form(
        request,
        api_path='/prioritys/',
        template='crm/settings/priority_form.html',
        form_class=PriorityForm,
        title_new='CRM — Nova prioridade',
        title_edit='CRM — Editar prioridade',
        list_url_name='crm:settings_priorities',
        record_id=record_id,
    )


@crm_perm_required('view_settings')
def settings_status_tasks(request):
    return _settings_list(
        request,
        api_path='/status-tasks/',
        template='crm/settings/status_tasks.html',
        title='CRM — Status de tarefas',
        perm_manage='manage_status_tasks',
    )


@crm_perm_required('manage_status_tasks')
def settings_status_task_new(request):
    return _settings_form(
        request,
        api_path='/status-tasks/',
        template='crm/settings/status_task_form.html',
        form_class=StatusTaskForm,
        title_new='CRM — Novo status',
        title_edit='CRM — Editar status',
        list_url_name='crm:settings_status_tasks',
    )


@crm_perm_required('manage_status_tasks')
def settings_status_task_edit(request, record_id):
    return _settings_form(
        request,
        api_path='/status-tasks/',
        template='crm/settings/status_task_form.html',
        form_class=StatusTaskForm,
        title_new='CRM — Novo status',
        title_edit='CRM — Editar status',
        list_url_name='crm:settings_status_tasks',
        record_id=record_id,
    )


@require_POST
def ajax_settings_delete(request, resource, record_id):
    perm_map = {
        'service-types': 'manage_service_types',
        'prioritys': 'manage_priorities',
        'status-tasks': 'manage_status_tasks',
    }
    perm = perm_map.get(resource)
    if not perm or not request.user.has_perm(f'crm.{perm}'):
        return JsonResponse({'ok': False, 'error': 'Sem permissão.'}, status=403)

    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        CrmApiClient(request.user).delete(f'/{resource}/{record_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)
