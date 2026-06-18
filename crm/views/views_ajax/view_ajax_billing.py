import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_permission_required
from crm.forms import BillingForm
from crm.helpers.api_display import billing_form_json, billing_to_json, enrich_billing_with_lookups
from crm.views.views_faturamento.view_lista_faturamento import (
    _billing_lookup_maps,
    _lookup_options,
    get_billing_lookups,
)
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import billing_api_payload
from crm_api.services import billing as billing_service
from crm_api.services import contracts as contracts_service


def _parse_request_data(request):
    content_type = (request.content_type or "").split(";")[0].strip().lower()
    if content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return None
    return request.POST.dict()


def _billing_form_response(request, raw, *, nome_form):
    gai_id = raw.get("client_gai_id")
    lookups = get_billing_lookups(CrmApiClient(request))
    form = BillingForm(raw, lookups=lookups, nome_form=nome_form)
    if not form.is_valid():
        return None, JsonResponse(
            {"ok": False, "errors": form.errors, "detail": "Verifique os campos."},
            status=400,
        )
    return form, None


def _load_contract(client, contract_id):
    if contract_id in (None, ""):
        return None
    try:
        return contracts_service.get_contract(client, contract_id)
    except CrmApiError:
        return None


def _resolve_billing_record(client, created, *, fallback=None):
    billing_id = (created or {}).get("id") if isinstance(created, dict) else created
    if billing_id not in (None, ""):
        try:
            return billing_service.get_billing(client, billing_id)
        except CrmApiError:
            pass
    if isinstance(created, dict):
        return created
    return fallback or {}


def _billing_api_payload_for_form(client, cleaned_data):
    contract = _load_contract(client, cleaned_data.get("contract_id"))
    return billing_api_payload(cleaned_data, contract=contract)


@crm_permission_required("view_billing")
@require_GET
def ajax_billing_lookups(request):
    """Opções de cliente/contrato para modais — carregadas sob demanda."""
    client = CrmApiClient(request)
    lookups = get_billing_lookups(client)
    clients, contracts = _lookup_options(lookups)
    return JsonResponse({"ok": True, "clients": clients, "contracts": contracts})


@crm_permission_required("view_billing")
@require_GET
def ajax_get_billing(request, billing_id):
    client = CrmApiClient(request)
    try:
        data = billing_service.get_billing(client, billing_id)
        data = _enrich_billing_response(client, data)
        return JsonResponse({
            "ok": True,
            "billing": billing_to_json(data, already_enriched=True),
            "form": billing_form_json(data),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )


def _enrich_billing_response(client, record):
    lookups = get_billing_lookups(client)
    clients_by_gai, contracts_by_id = _billing_lookup_maps(lookups)
    return enrich_billing_with_lookups(
        record,
        clients_by_gai=clients_by_gai,
        contracts_by_id=contracts_by_id,
    )


@crm_permission_required("add_billing")
@require_POST
def ajax_create_billing(request):
    raw = _parse_request_data(request)
    if raw is None:
        return JsonResponse({"ok": False, "detail": "JSON inválido."}, status=400)

    form, error_response = _billing_form_response(request, raw, nome_form="Novo Faturamento")
    if error_response:
        return error_response

    client = CrmApiClient(request)
    try:
        created = billing_service.create_billing(
            client,
            _billing_api_payload_for_form(client, form.cleaned_data),
        )
        record = _resolve_billing_record(
            client,
            created,
            fallback={"id": None, **form.cleaned_data},
        )
        record = _enrich_billing_response(client, record)
        return JsonResponse({
            "ok": True,
            "message": "Faturamento criado com sucesso!",
            "billing": billing_to_json(record, already_enriched=True),
            "form": billing_form_json(record),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )


@crm_permission_required("change_billing")
@require_POST
def ajax_update_billing(request, billing_id):
    raw = _parse_request_data(request)
    if raw is None:
        return JsonResponse({"ok": False, "detail": "JSON inválido."}, status=400)

    form, error_response = _billing_form_response(request, raw, nome_form="Editar Faturamento")
    if error_response:
        return error_response

    client = CrmApiClient(request)
    try:
        updated = billing_service.update_billing(
            client,
            billing_id,
            _billing_api_payload_for_form(client, form.cleaned_data),
        )
        record = _resolve_billing_record(
            client,
            updated,
            fallback={"id": billing_id, **form.cleaned_data},
        )
        record = _enrich_billing_response(client, record)
        return JsonResponse({
            "ok": True,
            "message": "Faturamento atualizado com sucesso!",
            "billing": billing_to_json(record, already_enriched=True),
            "form": billing_form_json(record),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )
