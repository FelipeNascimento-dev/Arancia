import json

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from crm.decorators import crm_permission_required
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import assignee_payload, comment_payload, link_payload, subtask_payload
from crm_api.services import tasks as tasks_service
from crm.views.views_tasks._helpers import (
    board_access_for_task,
    can_comment_on_board,
    enrich_task_for_display,
)
from crm.views.views_tasks.task_tab_helpers import TASK_DETAIL_TABS, fetch_task_tab_context


def _json_error(exc, default_status=400):
    status = getattr(exc, "status_code", None) or default_status
    return JsonResponse(
        {"ok": False, "detail": crm_error_message_pt(exc)},
        status=status,
    )


def _require_task_comment_access(request, client, task_id):
    try:
        task = tasks_service.get_task(client, task_id)
    except CrmApiError as exc:
        return None, _json_error(exc, getattr(exc, "status_code", None) or 403)
    board_access = board_access_for_task(client, task)
    if not can_comment_on_board(request, board_access):
        return None, JsonResponse(
            {"ok": False, "detail": "Você não tem permissão para comentar neste board."},
            status=403,
        )
    return task, None


@crm_permission_required("view_task")
@require_GET
def ajax_task_tab(request, task_id):
    tab = request.GET.get("tab", "info")
    if tab not in TASK_DETAIL_TABS:
        return JsonResponse({"ok": False, "detail": "Aba inválida."}, status=400)

    client = CrmApiClient(request)
    try:
        task = tasks_service.get_task(client, task_id)
        if task:
            task = enrich_task_for_display(task)
    except CrmApiError as exc:
        return _json_error(exc, getattr(exc, "status_code", None) or 404)

    board_access = board_access_for_task(client, task)
    can_comment = can_comment_on_board(request, board_access)
    context = fetch_task_tab_context(
        client,
        request,
        task_id,
        tab,
        task=task,
        board_access=board_access,
        can_comment=can_comment,
    )
    html = render_to_string(
        f"crm/templates_tasks/partials/tab_{tab}.html",
        context,
        request=request,
    )
    return JsonResponse({"ok": True, "html": html, "tab": tab})


@crm_permission_required("move_task")
@require_POST
def ajax_move_task(request, task_id):
    client = CrmApiClient(request)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {
            "status_id": request.POST.get("status_id"),
            "kanban_position": request.POST.get("kanban_position"),
            "board_id": request.POST.get("board_id"),
        }
        payload = {k: v for k, v in payload.items() if v not in (None, "")}
    try:
        data = tasks_service.move_task(client, task_id, payload)
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("assign_task")
@require_POST
def ajax_assign_task(request, task_id):
    client = CrmApiClient(request)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {
            "user_id": request.POST.get("user_id"),
            "designation_id": request.POST.get("designation_id"),
        }
        payload = {k: v for k, v in payload.items() if v not in (None, "")}
    try:
        data = tasks_service.add_assignee(client, task_id, assignee_payload(payload))
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("assign_task")
@require_POST
def ajax_remove_assignee(request, task_id, assignee_id):
    client = CrmApiClient(request)
    try:
        tasks_service.remove_assignee(client, task_id, assignee_id)
        return JsonResponse({"ok": True})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("view_task")
@require_POST
def ajax_watch_task(request, task_id):
    client = CrmApiClient(request)
    try:
        data = tasks_service.watch_task(client, task_id)
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("manage_watchers")
@require_POST
def ajax_remove_watcher(request, task_id, watcher_id):
    client = CrmApiClient(request)
    try:
        tasks_service.remove_watcher(client, task_id, watcher_id)
        return JsonResponse({"ok": True})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("view_task")
@require_POST
def ajax_comment_task(request, task_id):
    client = CrmApiClient(request)
    _, denied = _require_task_comment_access(request, client, task_id)
    if denied:
        return denied
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {"body": request.POST.get("body", "")}
    try:
        data = tasks_service.add_comment(client, task_id, comment_payload(payload))
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("view_task")
@require_POST
def ajax_attachment_task(request, task_id):
    client = CrmApiClient(request)
    _, denied = _require_task_comment_access(request, client, task_id)
    if denied:
        return denied
    upload_file = request.FILES.get("file") or request.FILES.get("attachment")
    if not upload_file:
        return JsonResponse(
            {"ok": False, "detail": "Nenhum arquivo enviado."},
            status=400,
        )
    try:
        data = tasks_service.upload_attachment(
            client,
            task_id,
            files={
                "file": (upload_file.name, upload_file.read(), upload_file.content_type),
            },
        )
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("change_task")
@require_POST
def ajax_task_link(request, task_id):
    client = CrmApiClient(request)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {
            "target_task_id": request.POST.get("target_task_id"),
            "link_type": request.POST.get("link_type", "related"),
        }
    try:
        data = tasks_service.create_link(client, task_id, link_payload(payload))
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("change_task")
@require_POST
def ajax_remove_task_link(request, task_id, link_id):
    client = CrmApiClient(request)
    try:
        tasks_service.delete_link(client, task_id, link_id)
        return JsonResponse({"ok": True})
    except CrmApiError as exc:
        return _json_error(exc)


@crm_permission_required("add_task")
@require_POST
def ajax_subtask(request, task_id):
    client = CrmApiClient(request)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {"title": request.POST.get("title", "")}
    try:
        data = tasks_service.create_subtask(client, task_id, subtask_payload(payload))
        return JsonResponse({"ok": True, "data": data})
    except CrmApiError as exc:
        return _json_error(exc)
