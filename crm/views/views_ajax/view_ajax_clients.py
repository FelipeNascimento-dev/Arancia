import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_permission_required
from crm.forms import ClientForm
from crm.helpers.api_display import client_to_json
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import client_payload
from crm_api.services import clients as clients_service


@crm_permission_required("view_clients")
@require_GET
def ajax_get_client(request, gai_id):
    client = CrmApiClient(request)
    try:
        data = clients_service.get_client(client, gai_id)
        return JsonResponse({"ok": True, "client": client_to_json(data)})
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )


@crm_permission_required("change_client")
@require_POST
def ajax_update_client(request, gai_id):
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

    form = ClientForm(raw, nome_form="Editar Cliente")
    if not form.is_valid():
        return JsonResponse(
            {"ok": False, "errors": form.errors, "detail": "Verifique os campos."},
            status=400,
        )

    try:
        updated = clients_service.update_client(
            client,
            gai_id,
            client_payload(form.cleaned_data),
        )
        return JsonResponse({
            "ok": True,
            "client": client_to_json(updated or {"gai_id": gai_id, **form.cleaned_data}),
        })
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )


@crm_permission_required("delete_client")
@require_POST
def ajax_delete_client(request, gai_id):
    client = CrmApiClient(request)
    try:
        data = clients_service.delete_client(client, gai_id)
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        status = getattr(exc, "status_code", None) or 400
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=status,
        )
