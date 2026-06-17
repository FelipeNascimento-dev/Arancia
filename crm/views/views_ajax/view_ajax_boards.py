import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from crm.decorators import crm_permission_required
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services import boards as boards_service


def _json_error(exc, default_status=400):
    status = getattr(exc, "status_code", None) or default_status
    return JsonResponse(
        {"ok": False, "detail": crm_error_message_pt(exc)},
        status=status,
    )


@crm_permission_required("manage_board_columns")
@require_POST
def ajax_reorder_columns(request, board_id):
    client = CrmApiClient(request)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        column_ids = request.POST.getlist("column_ids[]") or request.POST.getlist("column_ids")
        payload = {"column_ids": column_ids}
    try:
        data = boards_service.reorder_columns(client, board_id, payload)
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)
