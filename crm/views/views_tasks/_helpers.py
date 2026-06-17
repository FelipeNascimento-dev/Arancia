from crm.helpers.api_display import enrich_task_lookups, nested_label
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import projects as projects_service
from crm_api.services import tasks as tasks_service
from crm_api.services.lookups import get_column_templates, get_crm_lookups, get_groups, get_team_gais


def menu_context(current_menu, current_submenu=None, *, parent_menu="projetos"):
    ctx = {
        "current_parent_menu": parent_menu,
        "current_menu": current_menu,
    }
    if current_submenu:
        ctx["current_submenu"] = current_submenu
    return ctx


def load_task_lookups(client: CrmApiClient):
    try:
        return enrich_task_lookups(get_crm_lookups(client) or {})
    except CrmApiError:
        return {}


def load_project_lookups(client: CrmApiClient):
    lookups = load_task_lookups(client)
    try:
        team_gais = get_team_gais(client)
        if isinstance(team_gais, dict):
            lookups["team_gais"] = team_gais.get("items") or team_gais.get("results") or []
        elif isinstance(team_gais, list):
            lookups["team_gais"] = team_gais
    except CrmApiError:
        lookups.setdefault("team_gais", [])
    try:
        projects, _ = projects_service.list_projects(client, limit=200)
        lookups["projects"] = projects
    except CrmApiError:
        lookups.setdefault("projects", [])
    return lookups


def load_board_lookups(client: CrmApiClient):
    lookups = load_project_lookups(client)
    try:
        groups = get_groups(client)
        if isinstance(groups, dict):
            lookups["groups"] = groups.get("items") or groups.get("results") or []
        elif isinstance(groups, list):
            lookups["groups"] = groups
    except CrmApiError:
        lookups.setdefault("groups", [])
    try:
        templates = get_column_templates(client)
        if isinstance(templates, dict):
            lookups["column_templates"] = (
                templates.get("items") or templates.get("results") or []
            )
        elif isinstance(templates, list):
            lookups["column_templates"] = templates
    except CrmApiError:
        lookups.setdefault("column_templates", [])
    try:
        from crm_api.services import boards as boards_service

        boards, _ = boards_service.list_boards(client, limit=200)
        lookups["boards"] = boards
    except CrmApiError:
        lookups.setdefault("boards", [])
    return enrich_task_lookups(lookups)


def task_list_filters(request):
    overdue = request.GET.get("overdue_only")
    scheduled = request.GET.get("scheduled_only")
    return {
        "q": request.GET.get("q", "").strip() or None,
        "status_id": request.GET.get("status_id") or None,
        "board_id": request.GET.get("board_id") or None,
        "project_id": request.GET.get("project_id") or None,
        "priority_id": request.GET.get("priority_id") or None,
        "overdue_only": overdue if overdue else None,
        "scheduled_only": scheduled if scheduled else None,
        "start_at_from": request.GET.get("start_at_from") or request.GET.get("date_from") or None,
        "start_at_to": request.GET.get("start_at_to") or request.GET.get("date_to") or None,
        "requester_gai_id": request.GET.get("requester_gai_id") or None,
    }


def enrich_task_for_display(task):
    if not isinstance(task, dict):
        return task
    board = task.get("board") or {}
    status = task.get("status") or {}
    priority = task.get("priority") or {}
    project = task.get("project") or {}
    return {
        **task,
        "display_title": task.get("title") or task.get("titulo") or task.get("nome") or "-",
        "display_status": nested_label(status, "name", "nome") or task.get("status_name") or "-",
        "display_board": nested_label(board, "name", "nome") or task.get("board_name") or "-",
        "display_priority": nested_label(priority, "name", "nome") or task.get("priority_name") or "-",
        "display_project": nested_label(project, "name", "nome", "title") or task.get("project_name") or "-",
        "display_due": task.get("due_at") or task.get("due_date") or task.get("data_vencimento") or "-",
    }


def _list_limit(request, default=20):
    try:
        return int(request.GET.get("limit", default))
    except (TypeError, ValueError):
        return default


def fetch_task_list(request, *, my_tasks=False, role=None, extra_filters=None):
    client = CrmApiClient(request)
    limit = _list_limit(request)
    pagination = build_api_pagination(request, [], limit=limit)
    filters = task_list_filters(request)
    if extra_filters:
        filters.update(extra_filters)
    if role:
        filters["role"] = role
    items = []
    error_message = None
    lookups = {}

    list_fn = tasks_service.list_my_tasks if my_tasks else tasks_service.list_tasks
    try:
        raw_items, total = list_fn(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            **{k: v for k, v in filters.items() if v is not None},
        )
        items = [enrich_task_for_display(item) for item in raw_items]
        pagination = build_api_pagination(
            request, items, total_items=total, limit=pagination["limit"],
        )
        lookups = load_board_lookups(client)
    except CrmApiError as exc:
        error_message = crm_error_message_pt(exc)

    return client, items, pagination, filters, lookups, error_message


def fetch_calendar_tasks(request):
    extra = {"scheduled_only": "true", "role": "assignee"}
    _, items, pagination, filters, lookups, error_message = fetch_task_list(
        request,
        my_tasks=True,
        extra_filters=extra,
    )
    return items, pagination, filters, lookups, error_message


def task_display_value(task, *keys, default="-"):
    for key in keys:
        value = task.get(key)
        if value not in (None, ""):
            if isinstance(value, dict):
                return value.get("name") or value.get("nome") or value.get("label") or default
            return value
    return default


def board_id_from_task(task):
    if not isinstance(task, dict):
        return None
    return task.get("board_id") or (task.get("board") or {}).get("id")


def board_access_for_task(client: CrmApiClient, task):
    board_id = board_id_from_task(task)
    if not board_id:
        return {}
    try:
        return client.get(f"/boards/{board_id}/access/me") or {}
    except CrmApiError:
        return {}


def can_comment_on_board(request, board_access):
    if not request.user.has_perm("crm.view_task"):
        return False
    return board_access.get("can_comment", True)
