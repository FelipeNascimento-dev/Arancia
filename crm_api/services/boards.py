from crm_api.client import CrmApiClient, parse_list_response


def list_boards(client: CrmApiClient, *, skip=0, limit=50, **filters):
    params = {"skip": skip, "limit": limit}
    for key, value in filters.items():
        if value not in (None, ""):
            params[key] = value
    data = client.get("/boards/", params=params)
    return parse_list_response(data)


def get_board(client: CrmApiClient, board_id):
    return client.get(f"/boards/{board_id}")


def create_board(client: CrmApiClient, payload):
    return client.post("/boards/", json=payload)


def update_board(client: CrmApiClient, board_id, payload):
    return client.patch(f"/boards/{board_id}", json=payload)


def delete_board(client: CrmApiClient, board_id):
    return client.delete(f"/boards/{board_id}")


def list_columns(client: CrmApiClient, board_id):
    data = client.get(f"/boards/{board_id}/columns")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or data.get("columns") or []


def create_column(client: CrmApiClient, board_id, payload):
    return client.post(f"/boards/{board_id}/columns", json=payload)


def update_column(client: CrmApiClient, board_id, column_id, payload):
    return client.patch(f"/boards/{board_id}/columns/{column_id}", json=payload)


def _column_sort_key(column):
    for key in ("kanban_position", "sort_order", "position"):
        value = column.get(key)
        if value is not None:
            return value
    return 0


def column_reorder_payload(payload):
    """Normaliza payload para PATCH /boards/{id}/columns/reorder."""
    if isinstance(payload, list):
        column_ids = payload
    elif isinstance(payload, dict):
        raw_items = payload.get("items")
        if isinstance(raw_items, list):
            items = []
            for index, item in enumerate(raw_items):
                if not isinstance(item, dict):
                    continue
                column_id = item.get("id")
                if column_id in (None, ""):
                    continue
                position = item.get("kanban_position")
                if position is None:
                    position = index
                items.append({"id": column_id, "kanban_position": int(position)})
            return {"items": items}
        column_ids = payload.get("column_ids") or payload.get("ids") or []
    else:
        column_ids = []

    items = []
    for index, column_id in enumerate(column_ids):
        if column_id in (None, ""):
            continue
        items.append({"id": column_id, "kanban_position": index})
    return {"items": items}


def reorder_columns(client: CrmApiClient, board_id, payload):
    return client.patch(
        f"/boards/{board_id}/columns/reorder",
        json=column_reorder_payload(payload),
    )


def list_access(client: CrmApiClient, board_id):
    data = client.get(f"/boards/{board_id}/access")
    if isinstance(data, list):
        return data
    return data.get("items") or data.get("results") or data.get("access") or []


def get_my_access(client: CrmApiClient, board_id):
    return client.get(f"/boards/{board_id}/access/me")


def add_access(client: CrmApiClient, board_id, payload):
    return client.post(f"/boards/{board_id}/access", json=payload)


def update_access(client: CrmApiClient, board_id, access_id, payload):
    return client.patch(f"/boards/{board_id}/access/{access_id}", json=payload)


def remove_access(client: CrmApiClient, board_id, access_id):
    return client.delete(f"/boards/{board_id}/access/{access_id}")


def get_comercial_board(client: CrmApiClient, *, code=None):
    from django.conf import settings
    from crm_api.exceptions import CrmNotFoundError

    board_code = code or getattr(settings, "CRM_COMERCIAL_BOARD_CODE", "crm_comercial")
    boards, _ = list_boards(client, limit=200)
    for board in boards:
        if board.get("code") == board_code:
            return board
    raise CrmNotFoundError(f"Board comercial '{board_code}' não encontrado.")


def get_comercial_board_id(client: CrmApiClient, *, code=None):
    from crm_api.exceptions import CrmNotFoundError

    board = get_comercial_board(client, code=code)
    board_id = board.get("id")
    if board_id is None:
        raise CrmNotFoundError("Board CRM Comercial sem ID.")
    return board_id


def get_kanban_bundle(client: CrmApiClient, board_id, *, task_limit=100):
    """GET /boards/{id}/kanban — board, columns, tasks and access (UI)."""
    return client.get(
        f"/boards/{board_id}/kanban",
        params={"task_limit": task_limit},
    )


def resolve_board_id_from_page(board_page, code=None):
    """Resolve board UUID from board-page bundle by code."""
    from django.conf import settings

    board_code = code or getattr(settings, "CRM_COMERCIAL_BOARD_CODE", "crm_comercial")
    crm = (board_page or {}).get("crm") or {}
    for board in crm.get("boards") or []:
        if isinstance(board, dict) and board.get("code") == board_code:
            return board.get("id")
    return None
