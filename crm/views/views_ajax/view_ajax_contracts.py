from django.http import JsonResponse
from django.views.decorators.http import require_POST

from crm.decorators import crm_permission_required
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services import contracts as contracts_service


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
