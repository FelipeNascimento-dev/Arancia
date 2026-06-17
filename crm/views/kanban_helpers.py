from crm.helpers.api_display import enrich_board, enrich_board_column
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services import boards as boards_service
from crm_api.services import tasks as tasks_service


def _tasks_by_status(tasks, columns):
    status_to_column = {}
    for col in columns:
        status_id = col.get("status_task_id") or col.get("status_id")
        if status_id is not None:
            status_to_column[status_id] = col.get("id") or status_id

    grouped = {col.get("id") or col.get("status_task_id"): [] for col in columns}
    for col in columns:
        key = col.get("id") or col.get("status_task_id")
        grouped.setdefault(key, [])

    for task in tasks:
        status_id = task.get("status_id")
        if isinstance(task.get("status"), dict):
            status_id = status_id or task["status"].get("id")
        col_key = status_to_column.get(status_id)
        if col_key is None:
            col_key = status_id
        grouped.setdefault(col_key, []).append(task)

    for key in grouped:
        grouped[key].sort(
            key=lambda t: (t.get("kanban_position") or 0, t.get("id") or 0),
        )
    return grouped


def build_kanban_context(request, client: CrmApiClient, board_id):
    board = None
    columns = []
    tasks = []
    my_access = {}
    errors = []

    try:
        board = boards_service.get_board(client, board_id)
        if board:
            board = enrich_board(board)
    except CrmApiError as exc:
        errors.append(crm_error_message_pt(exc))
        return None, errors

    try:
        columns = boards_service.list_columns(client, board_id)
        columns = sorted(columns, key=lambda c: c.get("position") or c.get("sort_order") or 0)
        columns = [enrich_board_column(c) for c in columns]
    except CrmApiError as exc:
        errors.append(crm_error_message_pt(exc))

    try:
        tasks, _ = tasks_service.list_tasks(client, board_id=board_id, limit=500)
    except CrmApiError as exc:
        errors.append(crm_error_message_pt(exc))

    try:
        my_access = boards_service.get_my_access(client, board_id) or {}
    except CrmApiError:
        my_access = {}

    tasks_by_column = _tasks_by_status(tasks, columns)
    columns_with_tasks = []
    for col in columns:
        col_key = col.get("id") or col.get("status_task_id")
        columns_with_tasks.append({
            "column": col,
            "col_key": col_key,
            "tasks": tasks_by_column.get(col_key, []),
        })

    return {
        "board": board,
        "board_id": board_id,
        "columns_with_tasks": columns_with_tasks,
        "my_access": my_access,
        "can_create_tasks": my_access.get("can_create_tasks", False),
        "can_move_tasks": my_access.get("can_move_tasks", False)
        or request.user.has_perm("crm.move_task"),
        "can_comment": my_access.get("can_comment", False),
    }, errors
