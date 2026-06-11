from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from crm.decorators import crm_perm_required
from crm.forms.forms_clients import ClientAddressForm, ClientContactForm, ClientForm
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.gates import require_gai_or_render
from crm.services.lookups import build_gai_choices, build_new_client_gai_choices, fetch_crm_lookups
from crm.services.pagination import (
    build_pagination_context,
    get_pagination_params,
    normalize_list_response,
)

CRM_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_clients',
}


def _require_gai_or_render(request, template, extra_context=None):
    return require_gai_or_render(
        request,
        template,
        site_title='CRM — Clientes',
        menu_context=CRM_MENU,
        extra_context=extra_context,
    )


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


@crm_perm_required('view_clients')
def client_list(request):
    """GET /clients/ — listagem paginada."""
    blocked = _require_gai_or_render(request, 'crm/clients/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    client = CrmApiClient(request.user)
    clients = []
    api_error = None

    try:
        raw = client.get('/clients/', params={'skip': skip, 'limit': limit})
        clients = normalize_list_response(raw)
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    pagination = build_pagination_context(skip, limit, clients)
    client_profiles = {
        str(c.get('gai_id')): c.get('profile')
        for c in clients
        if c.get('gai_id') is not None and c.get('profile') not in (None, '', {})
    }
    return render(request, 'crm/clients/list.html', {
        'site_title': 'CRM — Clientes',
        'clients': clients,
        'pagination': pagination,
        'api_error': api_error,
        'client_profiles': client_profiles,
        **CRM_MENU,
    })


@crm_perm_required('add_client')
def client_new(request):
    """GET/POST — criar cliente via POST /clients/."""
    blocked = _require_gai_or_render(request, 'crm/clients/form.html', {
        'form_mode': 'new',
    })
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    gai_choices = build_new_client_gai_choices(request.user, lookups)

    if request.method == 'POST':
        form = ClientForm(request.POST, gai_choices=gai_choices, hide_profile=True, show_crm_type=True)
        if form.is_valid():
            if not form.cleaned_data.get('gai_id'):
                form.add_error('gai_id', 'Selecione o GAI para vincular o cliente.')
            else:
                try:
                    gai_id = int(form.cleaned_data['gai_id'])
                    # POST /clients/ retorna 500 na API homolog — cadastro via PATCH /clients/{gai_id}.
                    result = CrmApiClient(request.user).patch(
                        f'/clients/{gai_id}',
                        json=form.cleaned_payload(for_create=True),
                    )
                    messages.success(request, 'Cliente criado com sucesso.')
                    return redirect('crm:client_detail', gai_id=gai_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)
    else:
        form = ClientForm(gai_choices=gai_choices, hide_profile=True, show_crm_type=True)

    return render(request, 'crm/clients/form.html', {
        'site_title': 'CRM — Novo cliente',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        'no_eligible_gais': not gai_choices,
        **CRM_MENU,
    })


@crm_perm_required('view_clients')
def client_detail(request, gai_id):
    """GET /clients/{gai_id} — detalhe com contatos, endereços e contratos."""
    blocked = _require_gai_or_render(request, 'crm/clients/detail.html')
    if blocked:
        return blocked

    client_data = None
    try:
        client_data = CrmApiClient(request.user).get(f'/clients/{gai_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:client_list')

    return render(request, 'crm/clients/detail.html', {
        'site_title': f'CRM — {client_data.get("nome") or client_data.get("razao_social") or gai_id}',
        'client': client_data,
        'gai_id': gai_id,
        **CRM_MENU,
    })


@crm_perm_required('change_client')
def client_edit(request, gai_id):
    """GET/PATCH — editar cliente; POST contato/endereço (sem PATCH/DELETE deles)."""
    blocked = _require_gai_or_render(request, 'crm/clients/form.html', {
        'form_mode': 'edit',
        'gai_id': gai_id,
    })
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)
    gai_choices = build_gai_choices(lookups)

    try:
        client_data = api.get(f'/clients/{gai_id}')
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:client_list')

    gai_label = client_data.get('razao_social') or client_data.get('nome') or str(gai_id)
    if not any(str(c[0]) == str(gai_id) for c in gai_choices):
        gai_choices = [(str(gai_id), gai_label)] + gai_choices

    initial = {
        'gai_id': str(gai_id),
        'razao_social': client_data.get('razao_social') or '',
        'nome': client_data.get('nome') or '',
        'cnpj': client_data.get('cnpj') or '',
        'email': client_data.get('email') or '',
        'telefone1': client_data.get('telefone1') or '',
        'profile': client_data.get('profile') or '',
    }

    form = ClientForm(initial=initial, gai_choices=gai_choices, lock_gai=True)
    contact_form = ClientContactForm(prefix='contact')
    address_form = ClientAddressForm(prefix='address')

    if request.method == 'POST':
        action = request.POST.get('action', 'save_client')

        if action == 'add_contact':
            contact_form = ClientContactForm(request.POST, prefix='contact')
            if contact_form.is_valid():
                try:
                    api.post(
                        f'/clients/{gai_id}/contacts',
                        json=contact_form.cleaned_payload(),
                    )
                    messages.success(request, 'Contato adicionado.')
                    return redirect('crm:client_edit', gai_id=gai_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)
        elif action == 'add_address':
            address_form = ClientAddressForm(request.POST, prefix='address')
            if address_form.is_valid():
                try:
                    api.post(
                        f'/clients/{gai_id}/addresses',
                        json=address_form.cleaned_payload(),
                    )
                    messages.success(request, 'Endereço adicionado.')
                    return redirect('crm:client_edit', gai_id=gai_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)
        else:
            form = ClientForm(
                request.POST,
                gai_choices=gai_choices,
                lock_gai=True,
            )
            if form.is_valid():
                try:
                    api.patch(f'/clients/{gai_id}', json=form.cleaned_payload())
                    messages.success(request, 'Cliente atualizado com sucesso.')
                    return redirect('crm:client_detail', gai_id=gai_id)
                except CrmApiError as exc:
                    handle_crm_error(request, exc)

    return render(request, 'crm/clients/form.html', {
        'site_title': f'CRM — Editar {gai_label}',
        'form': form,
        'contact_form': contact_form,
        'address_form': address_form,
        'form_mode': 'edit',
        'gai_id': gai_id,
        'client': client_data,
        'lookups': lookups,
        **CRM_MENU,
    })


@require_POST
@crm_perm_required('delete_client')
def ajax_client_delete(request, gai_id):
    """DELETE /clients/{gai_id} — exclusão via AJAX."""
    if get_user_gai_id(request.user) is None:
        return JsonResponse({
            'ok': False,
            'error': 'Usuário sem GAI configurado.',
        }, status=400)

    try:
        CrmApiClient(request.user).delete(f'/clients/{gai_id}')
        return JsonResponse({'ok': True})
    except CrmApiError as exc:
        return JsonResponse({
            'ok': False,
            'error': str(exc.detail or exc),
        }, status=exc.status_code or 502)
