import json

from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_permission_required
from crm.views.kanban_helpers import KANBAN_LOAD_MORE_LIMIT, kanban_tasks_page
from crm.views.views_tasks._helpers import enrich_task_for_kanban_card
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services import boards as boards_service


def _json_error(exc, default_status=400):
    status = getattr(exc, "status_code", None) or default_status
    return JsonResponse(
        {"ok": False, "detail": crm_error_message_pt(exc)},
        status=status,
    )


def _column_key_for_status(columns, status_id):
    status_to_column = {}
    for col in columns:
        col_status = col.get("status_task_id") or col.get("status_id")
        if col_status is not None:
            status_to_column[col_status] = col.get("id") or col_status
    return status_to_column.get(status_id, status_id)


@crm_permission_required("view_board")
@require_GET
def ajax_kanban_tasks(request, board_id):
    client = CrmApiClient(request)
    try:
        skip = max(0, int(request.GET.get("skip", 0)))
    except (TypeError, ValueError):
        skip = 0
    try:
        limit = min(100, max(1, int(request.GET.get("limit", KANBAN_LOAD_MORE_LIMIT))))
    except (TypeError, ValueError):
        limit = KANBAN_LOAD_MORE_LIMIT

    try:
        columns = boards_service.list_columns(client, board_id)
    except CrmApiError as exc:
        return _json_error(exc)

    try:
        tasks, total = kanban_tasks_page(client, board_id, skip=skip, limit=limit)
    except CrmApiError as exc:
        return _json_error(exc)

    items = []
    for task in tasks:
        enriched = enrich_task_for_kanban_card(task)
        task_id = enriched.get("id")
        status_id = enriched.get("status_id")
        if isinstance(enriched.get("status"), dict):
            status_id = status_id or enriched["status"].get("id")
        items.append({
            "id": task_id,
            "title": enriched.get("title") or enriched.get("titulo") or "Task",
            "column_key": _column_key_for_status(columns, status_id),
            "display_due": enriched.get("display_due") or "-",
            "priority_name": enriched.get("priority_name") or "",
            "detail_url": reverse("crm:detalhe_task", kwargs={"task_id": task_id}),
            "kanban_position": enriched.get("kanban_position") or 0,
        })

    loaded = skip + len(items)
    has_more = total is not None and loaded < total
    if total is None and len(items) >= limit:
        has_more = True

    return JsonResponse({
        "ok": True,
        "tasks": items,
        "has_more": has_more,
        "total": total,
        "loaded": loaded,
    })


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
