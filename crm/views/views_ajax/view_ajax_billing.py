import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_permission_required
from crm.forms import BillingForm
from crm.helpers.api_display import billing_form_json, billing_to_json
from crm.views.views_faturamento.view_lista_faturamento import _billing_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import billing_payload
from crm_api.services import billing as billing_service


def _parse_request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return None
    return request.POST.dict()


def _billing_form_response(request, raw, *, nome_form):
    gai_id = raw.get("client_gai_id")
    lookups = _billing_lookups(CrmApiClient(request))
    form = BillingForm(raw, lookups=lookups, nome_form=nome_form)
    if not form.is_valid():
        return None, JsonResponse(
            {"ok": False, "errors": form.errors, "detail": "Verifique os campos."},
            status=400,
        )
    return form, None


@crm_permission_required("view_billing")
@require_GET
def ajax_get_billing(request, billing_id):
    client = CrmApiClient(request)
    try:
        data = billing_service.get_billing(client, billing_id)
        return JsonResponse({
            "ok": True,
            "billing": billing_to_json(data),
            "form": billing_form_json(data),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
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
        created = billing_service.create_billing(client, billing_payload(form.cleaned_data))
        record = created or {"id": None, **form.cleaned_data}
        return JsonResponse({
            "ok": True,
            "billing": billing_to_json(record),
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
            billing_payload(form.cleaned_data),
        )
        record = updated or {"id": billing_id, **form.cleaned_data}
        return JsonResponse({
            "ok": True,
            "billing": billing_to_json(record),
            "form": billing_form_json(record),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )
