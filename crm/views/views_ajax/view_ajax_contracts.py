import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_permission_required
from crm.forms import ContractForm
from crm.helpers.api_display import contract_to_json
from crm.views.views_contratos._helpers import contract_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import contract_payload
from crm_api.services import contracts as contracts_service


@crm_permission_required("view_contract")
@require_GET
def ajax_get_contract(request, contract_id):
    client = CrmApiClient(request)
    try:
        data = contracts_service.get_contract(client, contract_id)
        return JsonResponse({"ok": True, "contract": contract_to_json(data)})
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )


@crm_permission_required("change_contract")
@require_POST
def ajax_update_contract(request, contract_id):
    client = CrmApiClient(request)
    if request.content_type == "application/json":
        try:
            raw = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse(
                {"ok": False, "detail": "JSON inválido."},
                status=400,
            )
    else:
        raw = request.POST.dict()

    gai_id = raw.get("client_gai_id")
    lookups = contract_lookups(client, client_gai_id=gai_id)
    form = ContractForm(raw, lookups=lookups, nome_form="Editar Contrato")
    if not form.is_valid():
        return JsonResponse(
            {"ok": False, "errors": form.errors, "detail": "Verifique os campos."},
            status=400,
        )

    try:
        updated = contracts_service.update_contract(
            client,
            contract_id,
            contract_payload(form.cleaned_data),
        )
        return JsonResponse({
            "ok": True,
            "contract": contract_to_json(updated or {"id": contract_id, **form.cleaned_data}),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )


@crm_permission_required("upload_contract_file")
@require_POST
def ajax_delete_contract_file(request, contract_id, file_id):
    client = CrmApiClient(request)
    try:
        data = contracts_service.delete_contract_file(client, contract_id, file_id)
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )
