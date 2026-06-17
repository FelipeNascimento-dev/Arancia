from django.http import JsonResponse

from crm.decorators import crm_permission_required
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services.auth import health_check


@crm_permission_required("view_clients")
def ajax_health(request):
    client = CrmApiClient(request)
    try:
        result = health_check(client)
        return JsonResponse({"ok": result.get("ok", False), "data": result})
    except CrmApiError as exc:
        return JsonResponse(
            {"ok": False, "detail": crm_error_message_pt(exc)},
            status=503,
        )
