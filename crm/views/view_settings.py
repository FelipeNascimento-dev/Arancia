import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_settings import PriorityForm, ServiceTypeForm, StatusTaskForm
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.exceptions import CrmApiError, CrmBusinessError, handle_crm_error
from crm.services.gates import require_gai_or_render
from crm.services.lookups import (
    build_customer_choices,
    build_status_choices,
    customer_label,
    fetch_crm_lookups,
    fetch_service_types,
    parse_customer_gai_id,
)
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
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Configurações',
        menu_context=CRM_MENU,
        extra_context=extra_context,
    )


def _selected_customer_gai_id(request):
    return parse_customer_gai_id(request.GET.get('customer_gai_id'))


def _service_type_api_params(customer_gai_id):
    gai_id = parse_customer_gai_id(customer_gai_id)
    if gai_id is None:
        return None
    return {'customer_gai_id': gai_id}


def _service_types_list_url(customer_gai_id=None):
    url = reverse('crm:settings_service_types')
    gai_id = parse_customer_gai_id(customer_gai_id)
    if gai_id is None:
        return url
    return f'{url}?customer_gai_id={gai_id}'


def _load_customer_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _load_service_type_lookups(request, customer_gai_id=None):
    gai_id = parse_customer_gai_id(customer_gai_id)
    try:
        return fetch_crm_lookups(request.user, customer_gai_id=gai_id), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _service_type_list_context(request, *, customer_gai_id, lookups):
    customer_choices = build_customer_choices(lookups) if lookups else []
    return {
        'customer_gai_id': gai_id if (gai_id := parse_customer_gai_id(customer_gai_id)) else None,
        'customer_gai_id_str': str(gai_id) if gai_id else '',
        'customer_choices': customer_choices,
        'selected_customer_label': customer_label(lookups, gai_id) if gai_id and lookups else '',
    }


def _service_type_form_kwargs(lookups, customer_gai_id=None):
    return {
        'status_choices': build_status_choices(lookups),
        'client_choices': build_customer_choices(lookups),
        'default_client_id': str(customer_gai_id) if customer_gai_id else '',
    }


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
    list_redirect,
    record_id=None,
    form_kwargs=None,
    form_initial=None,
    find_params=None,
    extra_context=None,
):
    blocked = _require_gai_or_render(request, template, {'form_mode': 'edit' if record_id else 'new'})
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    initial = dict(form_initial or {})
    record_data = None

    if record_id:
        try:
            record_data = find_record_by_id(
                request.user,
                api_path,
                record_id,
                params=find_params,
            )
            if not record_data:
                raise CrmApiError('Registro não encontrado.', status_code=404)
            for key in form_class.base_fields:
                if key not in initial and record_data.get(key) is not None:
                    initial[key] = record_data.get(key)
        except CrmApiError as exc:
            handle_crm_error(request, exc)
            return redirect(list_redirect)

    form = form_class(initial=initial, **(form_kwargs or {}))

    if request.method == 'POST':
        form = form_class(request.POST, **(form_kwargs or {}))
        if form.is_valid():
            try:
                if record_id:
                    api.patch(f'{api_path.rstrip("/")}/{record_id}', json=form.cleaned_payload())
                    messages.success(request, 'Registro atualizado.')
                else:
                    api.post(api_path, json=form.cleaned_payload())
                    messages.success(request, 'Registro criado.')
                return redirect(list_redirect)
            except CrmBusinessError as exc:
                handle_crm_error(request, exc)
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, template, {
        'site_title': title_edit if record_id else title_new,
        'form': form,
        'form_mode': 'edit' if record_id else 'new',
        'record_id': record_id,
        'record': record_data,
        **(extra_context or {}),
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
    blocked = _require_gai_or_render(request, 'crm/settings/service_types.html')
    if blocked:
        return blocked

    customer_gai_id = _selected_customer_gai_id(request)
    lookups, _ = _load_customer_lookups(request)
    list_context = _service_type_list_context(
        request,
        customer_gai_id=customer_gai_id,
        lookups=lookups,
    )

    skip, limit = get_pagination_params(request)
    items = []
    api_error = None

    if customer_gai_id is None:
        return render(request, 'crm/settings/service_types.html', {
            'site_title': 'CRM — Tipos de serviço',
            'items': items,
            'pagination': build_pagination_context(skip, limit, items),
            'api_error': api_error,
            'can_manage': request.user.has_perm('crm.manage_service_types'),
            'requires_customer_gai': True,
            **list_context,
            **CRM_MENU,
        })

    try:
        raw = fetch_service_types(
            request.user,
            customer_gai_id=customer_gai_id,
            skip=skip,
            limit=limit,
        )
        items = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    return render(request, 'crm/settings/service_types.html', {
        'site_title': 'CRM — Tipos de serviço',
        'items': items,
        'pagination': build_pagination_context(skip, limit, items),
        'api_error': api_error,
        'can_manage': request.user.has_perm('crm.manage_service_types'),
        'requires_customer_gai': False,
        'filter_query': f'customer_gai_id={customer_gai_id}' if customer_gai_id else '',
        **list_context,
        **CRM_MENU,
    })


@crm_perm_required('manage_service_types')
def settings_service_type_new(request):
    customer_gai_id = _selected_customer_gai_id(request)
    lookups, _ = _load_customer_lookups(request)
    form_kwargs = _service_type_form_kwargs(lookups, customer_gai_id)
    initial = {}
    if customer_gai_id:
        initial['client_id'] = str(customer_gai_id)

    return _settings_form(
        request,
        api_path='/service-types/',
        template='crm/settings/service_type_form.html',
        form_class=ServiceTypeForm,
        title_new='CRM — Novo tipo de serviço',
        title_edit='CRM — Editar tipo de serviço',
        list_redirect=_service_types_list_url(customer_gai_id),
        form_kwargs=form_kwargs,
        form_initial=initial,
        extra_context={
            **_service_type_list_context(request, customer_gai_id=customer_gai_id, lookups=lookups),
            'service_types_list_url': _service_types_list_url(customer_gai_id),
        },
    )


@crm_perm_required('manage_service_types')
def settings_service_type_edit(request, record_id):
    customer_gai_id = _selected_customer_gai_id(request)
    lookups, _ = _load_customer_lookups(request)

    return _settings_form(
        request,
        api_path='/service-types/',
        template='crm/settings/service_type_form.html',
        form_class=ServiceTypeForm,
        title_new='CRM — Novo tipo de serviço',
        title_edit='CRM — Editar tipo de serviço',
        list_redirect=_service_types_list_url(customer_gai_id),
        record_id=record_id,
        form_kwargs=_service_type_form_kwargs(lookups, customer_gai_id),
        find_params=_service_type_api_params(customer_gai_id),
        extra_context={
            **_service_type_list_context(request, customer_gai_id=customer_gai_id, lookups=lookups),
            'service_types_list_url': _service_types_list_url(customer_gai_id),
        },
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
        list_redirect=reverse('crm:settings_priorities'),
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
        list_redirect=reverse('crm:settings_priorities'),
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
        list_redirect=reverse('crm:settings_status_tasks'),
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
        list_redirect=reverse('crm:settings_status_tasks'),
        record_id=record_id,
    )


@require_POST
@crm_perm_required('manage_status_tasks')
def ajax_status_tasks_reorder(request):
    if get_user_gai_id(request.user) is None:
        return JsonResponse({'ok': False, 'error': 'Usuário sem GAI configurado.'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)

    status_ids = payload.get('status_ids') or payload.get('ids')
    if not status_ids:
        return JsonResponse({'ok': False, 'error': 'status_ids é obrigatório.'}, status=400)

    try:
        result = CrmApiClient(request.user).patch(
            '/status-tasks/reorder',
            json={'status_ids': status_ids},
        )
        return JsonResponse({'ok': True, 'items': result})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)


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
