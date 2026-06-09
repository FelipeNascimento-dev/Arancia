from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_perm_required
from crm.forms.forms_billing import BillingForm
from crm.services.client import CrmApiClient
from crm.services.context import get_user_gai_id
from crm.services.exceptions import CrmApiError, handle_crm_error
from crm.services.lookups import (
    build_contract_choices,
    build_customer_choices,
    customer_label,
    fetch_crm_lookups,
)
from crm.services.pagination import (
    build_pagination_context,
    find_record_by_id,
    get_pagination_params,
    normalize_list_response,
)

CRM_MENU = {
    'current_parent_menu': 'crm',
    'current_menu': 'crm_billing',
}


def _require_gai_or_render(request, template, extra_context=None):
    if get_user_gai_id(request.user) is not None:
        return None
    context = {
        'site_title': 'CRM — Faturamento',
        'missing_gai': True,
        **CRM_MENU,
        **(extra_context or {}),
    }
    return render(request, template, context)


def _load_lookups(request):
    try:
        return fetch_crm_lookups(request.user), None
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return None, exc


def _load_contract_choices(user):
    try:
        raw = CrmApiClient(user).get('/contracts/', params={'skip': 0, 'limit': 500})
        return build_contract_choices(normalize_list_response(raw))
    except CrmApiError:
        return []


@crm_perm_required('view_billing')
def billing_list(request):
    """GET /billing/ — listagem paginada."""
    blocked = _require_gai_or_render(request, 'crm/billing/list.html')
    if blocked:
        return blocked

    skip, limit = get_pagination_params(request)
    client = CrmApiClient(request.user)
    records = []
    summary = None
    api_error = None
    lookups, _ = _load_lookups(request)

    try:
        raw = client.get('/billing/', params={'skip': skip, 'limit': limit})
        records = normalize_list_response(raw)
        for item in records:
            item['customer_label'] = customer_label(lookups, item.get('customer_gai_id'))
    except CrmApiError as exc:
        api_error = exc
        handle_crm_error(request, exc)

    try:
        summary = client.get('/billing/summary')
    except CrmApiError as exc:
        handle_crm_error(request, exc)

    pagination = build_pagination_context(skip, limit, records)
    return render(request, 'crm/billing/list.html', {
        'site_title': 'CRM — Faturamento',
        'records': records,
        'summary': summary,
        'pagination': pagination,
        'api_error': api_error,
        'lookups': lookups,
        **CRM_MENU,
    })


@crm_perm_required('add_billing')
def billing_new(request):
    """GET/POST — criar registro via POST /billing/."""
    blocked = _require_gai_or_render(request, 'crm/billing/form.html', {
        'form_mode': 'new',
    })
    if blocked:
        return blocked

    lookups, _ = _load_lookups(request)
    customer_choices = build_customer_choices(lookups)
    contract_choices = _load_contract_choices(request.user)

    if request.method == 'POST':
        form = BillingForm(
            request.POST,
            customer_choices=customer_choices,
            contract_choices=contract_choices,
        )
        if form.is_valid():
            if not form.cleaned_data.get('customer_gai_id'):
                form.add_error('customer_gai_id', 'Selecione o cliente (GAI).')
            else:
                try:
                    result = CrmApiClient(request.user).post(
                        '/billing/',
                        json=form.cleaned_payload(),
                    )
                    messages.success(request, 'Registro de faturamento criado.')
                    return redirect('crm:billing_list')
                except CrmApiError as exc:
                    handle_crm_error(request, exc)
    else:
        form = BillingForm(
            customer_choices=customer_choices,
            contract_choices=contract_choices,
        )

    return render(request, 'crm/billing/form.html', {
        'site_title': 'CRM — Novo faturamento',
        'form': form,
        'form_mode': 'new',
        'lookups': lookups,
        **CRM_MENU,
    })


@crm_perm_required('change_billing')
def billing_edit(request, record_id):
    """GET/PATCH — editar registro de faturamento."""
    blocked = _require_gai_or_render(request, 'crm/billing/form.html', {
        'form_mode': 'edit',
        'record_id': record_id,
    })
    if blocked:
        return blocked

    api = CrmApiClient(request.user)
    lookups, _ = _load_lookups(request)

    record_data = None
    try:
        record_data = find_record_by_id(request.user, '/billing/', record_id)
    except CrmApiError as exc:
        handle_crm_error(request, exc)
        return redirect('crm:billing_list')
    if record_data is None:
        messages.error(request, 'Registro de faturamento não encontrado.')
        return redirect('crm:billing_list')

    initial = {
        'planned_amount': record_data.get('planned_amount') or '0',
        'actual_amount': record_data.get('actual_amount') or '0',
        'notes': record_data.get('notes') or '',
    }
    if record_data.get('period_start'):
        initial['period_start'] = record_data['period_start']
    if record_data.get('period_end'):
        initial['period_end'] = record_data['period_end']

    form = BillingForm(initial=initial, lock_customer=True)

    if request.method == 'POST':
        form = BillingForm(request.POST, lock_customer=True)
        if form.is_valid():
            try:
                api.patch(
                    f'/billing/{record_id}',
                    json=form.cleaned_payload(for_update=True),
                )
                messages.success(request, 'Faturamento atualizado com sucesso.')
                return redirect('crm:billing_list')
            except CrmApiError as exc:
                handle_crm_error(request, exc)

    return render(request, 'crm/billing/form.html', {
        'site_title': 'CRM — Editar faturamento',
        'form': form,
        'form_mode': 'edit',
        'record_id': record_id,
        'record': record_data,
        'lookups': lookups,
        'customer_name': customer_label(lookups, record_data.get('customer_gai_id')),
        **CRM_MENU,
    })
