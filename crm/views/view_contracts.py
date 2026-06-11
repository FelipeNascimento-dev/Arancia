from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_contracts import ContractFileForm, ContractForm
from crm.services.client import CrmApiClient
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.gates import ajax_require_gai, require_gai_or_render
from crm.services.lookups import (
    build_customer_choices,
    build_service_type_choices,
    fetch_crm_lookups,
)
from crm.services.refs import customer_ref_label
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)

CRM_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_contracts',
}


def _require_gai_or_render(request, template, extra_context=None):
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Contratos',
        menu_context=CRM_MENU,
        extra_context=extra_context,
    )


def _load_lookups(request, customer_gai_id=None):
    try:
        return fetch_crm_lookups(request.user, customer_gai_id=customer_gai_id), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _contract_customer_gai_id(request, *, form=None, contract_data=None):
    if form is not None and form.is_bound:
        gai = form.data.get('customer_gai_id')
        if gai:
            return gai
    if contract_data and contract_data.get('customer_gai_id'):
        return contract_data['customer_gai_id']
    return request.GET.get('customer_gai_id')


@crm_perm_required('view_contracts')
def contract_list(request):
    """GET /contracts/ — listagem paginada."""
    blocked = _require_gai_or_render(request, 'crm/contracts/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    client = CrmApiClient(request.user)
    contracts = []
    api_error = None
    lookups, _ = _load_lookups(request)

    try:
        raw = client.get('/contracts/', params={'skip': skip, 'limit': limit})
        contracts = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    pagination = build_pagination_context(skip, limit, contracts)
    return render(request, 'crm/contracts/list.html', {
        'site_title': 'CRM — Contratos',
        'contracts': contracts,
        'pagination': pagination,
        'api_error': api_error,
        'lookups': lookups,
        **CRM_MENU,
    })


@crm_perm_required('add_contract')
def contract_new(request):
    """GET/POST — criar contrato via POST /contracts/."""
    blocked = _require_gai_or_render(request, 'crm/contracts/form.html', {
        'form_mode': 'new',
    })
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    customer_choices = build_customer_choices(lookups)

    if request.method == 'POST':
        form = ContractForm(
            request.POST,
            customer_choices=customer_choices,
        )
        selected_gai = _contract_customer_gai_id(request, form=form)
        st_lookups, _ = _load_lookups(request, customer_gai_id=selected_gai)
        service_type_choices = build_service_type_choices(st_lookups, customer_gai_id=selected_gai)
        form = ContractForm(
            request.POST,
            customer_choices=customer_choices,
            service_type_choices=service_type_choices,
        )
        if form.is_valid():
            if not form.cleaned_data.get('customer_gai_id'):
                form.add_error('customer_gai_id', 'Selecione o cliente (GAI).')
            else:
                try:
                    result = CrmApiClient(request.user).post(
                        '/contracts/',
                        json=form.cleaned_payload(),
                    )
                    contract_id = result.get('id') if isinstance(result, dict) else None
                    messages.success(request, 'Contrato criado com sucesso.')
                    if contract_id:
                        return redirect('crm:contract_detail', contract_id=contract_id)
                    return redirect('crm:contract_list')
                except CrmApiError as exc:
                    handle_crm_error(request, exc)
    else:
        selected_gai = _contract_customer_gai_id(request)
        st_lookups, _ = _load_lookups(request, customer_gai_id=selected_gai)
        service_type_choices = build_service_type_choices(st_lookups, customer_gai_id=selected_gai)
        form = ContractForm(
            customer_choices=customer_choices,
            service_type_choices=service_type_choices,
        )

    return render(request, 'crm/contracts/form.html', {
        'site_title': 'CRM — Novo contrato',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        'ajax_lookups_url': reverse('crm:ajax_crm_lookups'),
        **CRM_MENU,
    })


@crm_perm_required('view_contracts')
def contract_detail(request, contract_id):
    """GET /contracts/{id} — detalhe com arquivos."""
    blocked = _require_gai_or_render(request, 'crm/contracts/detail.html')
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    contract_data = None
    try:
        contract_data = CrmApiClient(request.user).get(f'/contracts/{contract_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:contract_list')

    file_form = ContractFileForm()
    return render(request, 'crm/contracts/detail.html', {
        'site_title': f'CRM — {contract_data.get("title") or contract_id}',
        'contract': contract_data,
        'contract_id': contract_id,
        'file_form': file_form,
        'lookups': lookups,
        **CRM_MENU,
    })


@crm_perm_required('change_contract')
def contract_edit(request, contract_id):
    """GET/PATCH — editar contrato."""
    blocked = _require_gai_or_render(request, 'crm/contracts/form.html', {
        'form_mode': 'edit',
        'contract_id': contract_id,
    })
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)

    try:
        contract_data = api.get(f'/contracts/{contract_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:contract_list')

    gai_id = contract_data.get('customer_gai_id')
    st_lookups, _ = _load_lookups(request, customer_gai_id=gai_id)
    customer_choices = build_customer_choices(lookups)
    service_type_choices = build_service_type_choices(st_lookups, customer_gai_id=gai_id)
    gai_label = customer_ref_label(contract_data, lookups=lookups)
    if gai_id and not any(str(c[0]) == str(gai_id) for c in customer_choices):
        customer_choices = [(str(gai_id), gai_label)] + customer_choices

    initial = {
        'customer_gai_id': str(gai_id) if gai_id else '',
        'service_type_id': str(contract_data['service_type_id']) if contract_data.get('service_type_id') else '',
        'title': contract_data.get('title') or '',
        'description': contract_data.get('description') or '',
        'renewal_notice_days': contract_data.get('renewal_notice_days', 30),
        'status': contract_data.get('status') or '',
        'is_active': contract_data.get('is_active', True),
    }
    if contract_data.get('start_date'):
        initial['start_date'] = contract_data['start_date']
    if contract_data.get('end_date'):
        initial['end_date'] = contract_data['end_date']

    form = ContractForm(
        initial=initial,
        customer_choices=customer_choices,
        service_type_choices=service_type_choices,
        lock_customer=True,
        show_status_fields=True,
    )
    file_form = ContractFileForm()

    if request.method == 'POST':
        action = request.POST.get('action', 'save_contract')

        if action == 'upload_file':
            file_form = ContractFileForm(request.POST, request.FILES)
            if file_form.is_valid():
                uploaded = file_form.cleaned_data['file']
                try:
                    uploaded.seek(0)
                    file_bytes = uploaded.read()
                    api.post_multipart(
                        f'/contracts/{contract_id}/files',
                        files={
                            'file': (
                                uploaded.name,
                                file_bytes,
                                uploaded.content_type or 'application/octet-stream',
                            ),
                        },
                    )
                    messages.success(request, 'Arquivo enviado com sucesso.')
                    return redirect('crm:contract_edit', contract_id=contract_id)
                except CrmApiError as exc:
                    if exc.status_code and exc.status_code >= 500:
                        messages.error(
                            request,
                            'Falha no armazenamento de arquivos do CRM (servidor). '
                            'Verifique a configuração de storage/Firebase na API CRM.',
                        )
                    else:
                        handle_crm_error(request, exc)
        else:
            form = ContractForm(
                request.POST,
                customer_choices=customer_choices,
                service_type_choices=service_type_choices,
                lock_customer=True,
                show_status_fields=True,
            )
            if form.is_valid():
                try:
                    api.patch(
                        f'/contracts/{contract_id}',
                        json=form.cleaned_payload(for_update=True),
                    )
                    messages.success(request, 'Contrato atualizado com sucesso.')
                    return redirect('crm:contract_detail', contract_id=contract_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

    return render(request, 'crm/contracts/form.html', {
        'site_title': f'CRM — Editar {contract_data.get("title") or contract_id}',
        'form': form,
        'file_form': file_form,
        'form_mode': 'edit',
        'contract_id': contract_id,
        'contract': contract_data,
        'lookups': lookups,
        'ajax_lookups_url': reverse('crm:ajax_crm_lookups'),
        **CRM_MENU,
    })


@require_POST
@crm_perm_required('upload_contract_file')
def ajax_contract_file_upload(request, contract_id):
    """POST multipart /contracts/{id}/files — upload via AJAX."""
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    uploaded = request.FILES.get('file')
    if not uploaded:
        return JsonResponse({
            'ok': False,
            'error': 'Nenhum arquivo enviado.',
        }, status=400)

    try:
        uploaded.seek(0)
        file_bytes = uploaded.read()
        result = CrmApiClient(request.user).post_multipart(
            f'/contracts/{contract_id}/files',
            files={
                'file': (
                    uploaded.name,
                    file_bytes,
                    uploaded.content_type or 'application/octet-stream',
                ),
            },
        )
        return JsonResponse({'ok': True, 'file': result})
    except CrmApiError as exc:
        error = str(exc.detail or exc)
        if exc.status_code and exc.status_code >= 500:
            error = (
                'Falha no armazenamento de arquivos do CRM (servidor). '
                'Verifique a configuração de storage/Firebase na API CRM.'
            )
        return JsonResponse({
            'ok': False,
            'error': error,
        }, status=exc.status_code or 502)


@require_POST
@crm_perm_required('upload_contract_file')
def ajax_contract_file_delete(request, contract_id, file_id):
    """DELETE /contracts/{id}/files/{file_id} — exclusão via AJAX."""
    blocked = ajax_require_gai(request)
    if blocked:
        return blocked

    try:
        CrmApiClient(request.user).delete(
            f'/contracts/{contract_id}/files/{file_id}',
        )
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)
