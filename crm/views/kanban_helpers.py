from crm.helpers.api_display import enrich_board, enrich_board_column
from crm.views.views_tasks._helpers import enrich_task_for_kanban_card
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.parallel import run_parallel_crm_fetches
from crm_api.services import boards as boards_service
from crm_api.services.boards import _column_sort_key
from crm_api.services import tasks as tasks_service

KANBAN_TASK_LIMIT = 100
KANBAN_LOAD_MORE_LIMIT = 50


def _tasks_by_status(tasks, columns, *, enrich_fn=enrich_task_for_kanban_card):
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
        grouped.setdefault(col_key, []).append(enrich_fn(task))

    for key in grouped:
        grouped[key].sort(
            key=lambda t: (t.get("kanban_position") or 0, t.get("id") or 0),
        )
    return grouped


def build_kanban_context(request, client: CrmApiClient, board_id):
    board = None
    columns = []
    tasks = []
    tasks_total = None
    my_access = {}
    errors = []

    try:
        board = boards_service.get_board(client, board_id)
        if board:
            board = enrich_board(board)
    except CrmApiError as exc:
        errors.append(crm_error_message_pt(exc))
        return None, errors

    def _fetch_columns(c):
        cols = boards_service.list_columns(c, board_id)
        cols = sorted(cols, key=_column_sort_key)
        return [enrich_board_column(col) for col in cols]

    def _fetch_tasks(c):
        return tasks_service.list_tasks(
            c,
            board_id=board_id,
            limit=KANBAN_TASK_LIMIT,
        )

    def _fetch_access(c):
        return boards_service.get_my_access(c, board_id) or {}

    parallel_results, parallel_errors = run_parallel_crm_fetches(
        request,
        [
            ("columns", _fetch_columns),
            ("tasks", _fetch_tasks),
            ("access", _fetch_access),
        ],
        max_workers=3,
    )

    if "columns" in parallel_results:
        columns = parallel_results["columns"]
    elif "columns" in parallel_errors:
        exc = parallel_errors["columns"]
        if isinstance(exc, CrmApiError):
            errors.append(crm_error_message_pt(exc))
        else:
            errors.append("Não foi possível carregar as colunas do board.")

    if "tasks" in parallel_results:
        tasks, tasks_total = parallel_results["tasks"]
    elif "tasks" in parallel_errors:
        exc = parallel_errors["tasks"]
        if isinstance(exc, CrmApiError):
            errors.append(crm_error_message_pt(exc))

    if "access" in parallel_results:
        my_access = parallel_results["access"]

    tasks_by_column = _tasks_by_status(tasks, columns)
    columns_with_tasks = []
    for col in columns:
        col_key = col.get("id") or col.get("status_task_id")
        columns_with_tasks.append({
            "column": col,
            "col_key": col_key,
            "tasks": tasks_by_column.get(col_key, []),
        })

    loaded_count = len(tasks)
    has_more_tasks = tasks_total is not None and tasks_total > loaded_count
    if tasks_total is None and loaded_count >= KANBAN_TASK_LIMIT:
        has_more_tasks = True

    return {
        "board": board,
        "board_id": board_id,
        "columns_with_tasks": columns_with_tasks,
        "my_access": my_access,
        "can_create_tasks": my_access.get("can_create_tasks", False),
        "can_move_tasks": my_access.get("can_move_tasks", False)
        or request.user.has_perm("crm.move_task"),
        "can_comment": my_access.get("can_comment", False),
        "kanban_tasks_loaded": loaded_count,
        "kanban_tasks_total": tasks_total,
        "kanban_has_more_tasks": has_more_tasks,
    }, errors


def kanban_tasks_page(client, board_id, *, skip=0, limit=KANBAN_LOAD_MORE_LIMIT):
    """Busca página adicional de tasks para o Kanban (AJAX load more)."""
    tasks, total = tasks_service.list_tasks(
        client,
        board_id=board_id,
        skip=skip,
        limit=limit,
    )
    return tasks, total
