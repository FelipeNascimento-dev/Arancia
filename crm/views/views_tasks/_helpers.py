from crm.helpers.api_display import enrich_task_lookups, nested_label
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import clients as clients_service
from crm_api.services import projects as projects_service
from crm_api.services import tasks as tasks_service
from crm_api.services.lookups import (
    get_column_templates,
    get_crm_lookups,
    get_designations,
    get_gais,
    get_groups,
    get_team_gais,
    get_users,
    unwrap_lookup_items,
)


def menu_context(current_menu, current_submenu=None, *, parent_menu="projetos"):
    ctx = {
        "current_parent_menu": parent_menu,
        "current_menu": current_menu,
    }
    if current_submenu:
        ctx["current_submenu"] = current_submenu
    return ctx


def _normalize_crm_lookups(data):
    if not isinstance(data, dict):
        return {}
    merged = dict(data)
    nested = data.get("lookups")
    if isinstance(nested, dict):
        merged.update(nested)
    for key, value in list(merged.items()):
        if key == "lookups":
            continue
        if isinstance(value, dict) and any(k in value for k in ("items", "results", "data")):
            merged[key] = unwrap_lookup_items(value)
    return merged


def _filter_active_gais(items):
    filtered = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        if item.get("is_active") is False:
            continue
        status = str(item.get("status") or "").lower()
        if status in ("inactive", "inativo", "disabled", "desativado"):
            continue
        filtered.append(item)
    return filtered if filtered else list(items or [])


def _normalize_gai_item(item):
    if not isinstance(item, dict):
        return item
    gai_id = item.get("id") or item.get("gai_id")
    nome = item.get("nome") or item.get("name")
    return {
        **item,
        "id": gai_id,
        "gai_id": gai_id,
        "nome": nome,
        "name": nome,
    }


def _load_active_gais(client: CrmApiClient):
    items = []
    try:
        items = unwrap_lookup_items(get_gais(client))
    except CrmApiError:
        pass
    items = [_normalize_gai_item(item) for item in _filter_active_gais(items)]
    if items:
        return items
    try:
        clients, _ = clients_service.list_clients(client, limit=500)
        return [_normalize_gai_item(item) for item in _filter_active_gais(clients)]
    except CrmApiError:
        return []


def _load_system_users(client: CrmApiClient):
    try:
        users = unwrap_lookup_items(get_users(client))
        if users:
            return users
    except CrmApiError:
        pass
    try:
        crm = _normalize_crm_lookups(get_crm_lookups(client) or {})
        users = crm.get("users")
        if isinstance(users, list):
            return users
        if isinstance(users, dict):
            return unwrap_lookup_items(users)
    except CrmApiError:
        pass
    return _django_system_users()


def _django_system_users():
    from django.contrib.auth.models import User

    return [
        {
            "id": user.id,
            "username": user.username,
            "name": user.get_full_name() or user.username,
        }
        for user in User.objects.filter(is_active=True).order_by("username")
    ]


def _load_designations(client: CrmApiClient):
    try:
        designations = unwrap_lookup_items(get_designations(client))
        if designations:
            return designations
    except CrmApiError:
        pass
    try:
        crm = _normalize_crm_lookups(get_crm_lookups(client) or {})
        designations = crm.get("designations")
        if isinstance(designations, list):
            return designations
        if isinstance(designations, dict):
            return unwrap_lookup_items(designations)
    except CrmApiError:
        pass
    return []


def load_task_lookups(client: CrmApiClient):
    lookups = {}
    try:
        lookups = enrich_task_lookups(_normalize_crm_lookups(get_crm_lookups(client) or {}))
    except CrmApiError:
        lookups = {}

    if not lookups.get("gais"):
        lookups["gais"] = _load_active_gais(client)
    if not lookups.get("users"):
        lookups["users"] = _load_system_users(client)
    if not lookups.get("designations"):
        lookups["designations"] = _load_designations(client)

    return enrich_task_lookups(lookups)


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
    customer = task.get("customer") or {}
    return {
        **task,
        "display_title": task.get("title") or task.get("titulo") or task.get("nome") or "-",
        "display_status": nested_label(status, "name", "nome") or task.get("status_name") or "-",
        "display_board": nested_label(board, "name", "nome") or task.get("board_name") or "-",
        "display_priority": nested_label(priority, "name", "nome") or task.get("priority_name") or "-",
        "display_project": nested_label(project, "name", "nome", "title") or task.get("project_name") or "-",
        "display_customer": nested_label(customer, "nome", "name", "razao_social") or "-",
        "display_due": task.get("due_at") or task.get("due_date") or task.get("data_vencimento") or "-",
        "display_scheduled_start": task.get("scheduled_start_at") or "-",
    }


def enrich_subtask_for_display(subtask):
    if not isinstance(subtask, dict):
        return subtask
    status = subtask.get("status") or {}
    return {
        **subtask,
        "display_title": subtask.get("title") or subtask.get("nome") or "-",
        "display_status": nested_label(status, "name", "nome") or subtask.get("status_name") or "-",
    }


def enrich_move_history_for_display(entry):
    if not isinstance(entry, dict):
        return entry
    from_status = entry.get("from_status") or {}
    to_status = entry.get("to_status") or {}
    return {
        **entry,
        "display_moved_at": entry.get("moved_at") or entry.get("created_at") or "-",
        "display_from_status": nested_label(from_status, "name", "nome") or entry.get("from_status_name") or "-",
        "display_to_status": nested_label(to_status, "name", "nome") or entry.get("to_status_name") or "-",
        "display_user": (
            entry.get("user_username")
            or entry.get("username")
            or entry.get("user_id")
            or "-"
        ),
    }


def enrich_assignee_for_display(assignee):
    if not isinstance(assignee, dict):
        return assignee
    return {
        **assignee,
        "display_name": (
            assignee.get("username")
            or assignee.get("name")
            or assignee.get("nome")
            or assignee.get("user_id")
            or "-"
        ),
    }


def enrich_watcher_for_display(watcher):
    if not isinstance(watcher, dict):
        return watcher
    return {
        **watcher,
        "display_name": (
            watcher.get("username")
            or watcher.get("name")
            or watcher.get("nome")
            or watcher.get("user_id")
            or "-"
        ),
    }


def enrich_comment_for_display(comment):
    if not isinstance(comment, dict):
        return comment
    return {
        **comment,
        "display_author": (
            comment.get("author_username")
            or comment.get("username")
            or comment.get("user_id")
            or "Usuário"
        ),
        "display_body": comment.get("content") or comment.get("body") or comment.get("text") or "",
    }


def enrich_attachment_for_display(attachment):
    if not isinstance(attachment, dict):
        return attachment
    return {
        **attachment,
        "display_name": attachment.get("filename") or attachment.get("name") or "Anexo",
        "display_url": attachment.get("url") or "#",
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
    try:
        lookups = load_board_lookups(client)
    except Exception:
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


_TASK_ASSIGNEE_FIELDS = frozenset({"assignee_user_id", "assignee_customer_gai_id"})


def task_create_data_from_form(cleaned_data):
    """Remove campos de atribuição antes de montar payload de criação."""
    return {
        k: v
        for k, v in cleaned_data.items()
        if k not in _TASK_ASSIGNEE_FIELDS
    }


def apply_task_assignees(client, task_id, cleaned_data):
    """Atribui usuário e/ou GAI após criar a task."""
    from crm_api.payloads import assignee_payload

    payloads = []
    user_id = cleaned_data.get("assignee_user_id")
    gai_id = cleaned_data.get("assignee_customer_gai_id")
    if user_id not in (None, ""):
        payloads.append({"user_id": user_id})
    if gai_id not in (None, ""):
        payloads.append({"customer_gai_id": gai_id})
    for payload in payloads:
        tasks_service.add_assignee(client, task_id, assignee_payload(payload))
