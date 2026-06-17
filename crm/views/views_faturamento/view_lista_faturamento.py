from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import BillingFilterForm, BillingForm
from crm.helpers.api_display import billing_initial, enrich_billing
from crm.views.views_contratos._helpers import contract_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.payloads import billing_payload
from crm_api.services import billing as billing_service
from crm_api.services import contracts as contracts_service

BILLING_SUMMARY_LABELS = {
    "total_records": "Total de registros",
    "total_value": "Valor total",
    "pending_count": "Pendentes",
    "pending_value": "Valor pendente",
    "paid_count": "Pagos",
    "paid_value": "Valor pago",
    "overdue_count": "Vencidos",
    "overdue_value": "Valor vencido",
}


def _billing_lookups(client):
    lookups = contract_lookups(client)
    try:
        contracts, _ = contracts_service.list_contracts(client, limit=200)
        lookups["contracts"] = contracts
    except CrmApiError:
        lookups.setdefault("contracts", [])
    return lookups


@crm_permission_required("view_billing")
def lista_faturamento(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    pagination = build_api_pagination(request, [])
    items = []
    summary = {}
    summary_cards = []

    try:
        summary = billing_service.billing_summary(client) or {}
        if isinstance(summary, dict):
            for key, value in summary.items():
                if key in ("items", "detail"):
                    continue
                summary_cards.append({
                    "label": BILLING_SUMMARY_LABELS.get(key, key.replace("_", " ").title()),
                    "value": value,
                })
    except CrmApiError:
        summary = {}

    try:
        raw_items, total = billing_service.list_billing(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
            status=status or None,
        )
        items = [enrich_billing(item) for item in raw_items]
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    filter_form = BillingFilterForm(
        initial={"q": q, "status": status},
        nome_form="Consulta de Faturamento",
    )

    return render(
        request,
        "crm/templates_faturamento/lista_faturamento.html",
        {
            "site_title": "CRM — Faturamento",
            "items": items,
            "pagination": pagination,
            "q": q,
            "status": status,
            "summary": summary,
            "summary_cards": summary_cards,
            "filter_form": filter_form,
            "current_parent_menu": "crm",
            "current_menu": "crm_faturamento",
        },
    )


@crm_permission_required("view_billing")
def form_faturamento(request, billing_id=None):
    if billing_id and not request.user.has_perm("crm.change_billing"):
        raise PermissionDenied
    if not billing_id and not request.user.has_perm("crm.add_billing"):
        raise PermissionDenied
    client = CrmApiClient(request)
    lookups = _billing_lookups(client)
    is_edit = billing_id is not None
    initial = {}

    if is_edit:
        try:
            data = billing_service.get_billing(client, billing_id)
            initial = billing_initial(data)
        except CrmApiError as exc:
            messages.error(request, crm_error_message_pt(exc))
            return redirect("crm:lista_faturamento")

    nome_form = "Editar Faturamento" if is_edit else "Novo Faturamento"
    form = BillingForm(initial=initial, lookups=lookups, nome_form=nome_form)

    if request.method == "POST":
        form = BillingForm(request.POST, lookups=lookups, nome_form=nome_form)
        if form.is_valid():
            try:
                payload = billing_payload(form.cleaned_data)
                if is_edit:
                    billing_service.update_billing(client, billing_id, payload)
                    messages.success(request, "Faturamento atualizado com sucesso!")
                else:
                    billing_service.create_billing(client, payload)
                    messages.success(request, "Faturamento criado com sucesso!")
                return redirect("crm:lista_faturamento")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_faturamento/form_faturamento.html",
        {
            "site_title": nome_form,
            "form": form,
            "is_edit": is_edit,
            "billing_id": billing_id,
            "botao_texto": "Salvar",
            "current_parent_menu": "crm",
            "current_menu": "crm_faturamento",
        },
    )
