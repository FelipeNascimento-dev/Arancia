from urllib.parse import urlencode

from setup.local_settings import MURAL_API_URL
from utils.request import RequestClient

DEFAULT_FEED_LIMIT = 100
MAX_FEED_PAGES = 20


def _parse_items_response(resp):
    if isinstance(resp, dict) and resp.get("detail"):
        raise ValueError(resp.get("detail") or "Erro ao carregar itens do mural.")

    if isinstance(resp, list):
        return resp, None

    if isinstance(resp, dict):
        items = (
            resp.get("items")
            or resp.get("results")
            or resp.get("data")
            or []
        )
        total = (
            resp.get("total")
            or resp.get("total_items")
            or resp.get("count")
        )
        return items, total

    return [], None


def fetch_mural_item_by_id(item_id):
    if not item_id:
        return None

    url = f"{MURAL_API_URL}/v1/items/{item_id}"
    client = RequestClient(
        url=url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    resp = client.send_api_request()

    if isinstance(resp, dict) and resp.get("detail"):
        return None

    if isinstance(resp, dict) and resp.get("id") is not None:
        return resp

    return None


def fetch_mural_items_for_user_raw(
    *,
    user_id,
    gai_id,
    reads_param="false",
    limit=DEFAULT_FEED_LIMIT,
):
    """Busca todas as páginas do feed consumidor na API do mural."""
    all_items = []
    offset = 0
    total_from_api = None

    for _ in range(MAX_FEED_PAGES):
        params = {
            "user_id": user_id,
            "gai_id": gai_id,
            "offset": offset,
            "limit": limit,
            "reads": reads_param,
        }

        url = f"{MURAL_API_URL}/v1/items/by-user/?{urlencode(params)}"
        client = RequestClient(
            url=url,
            method="GET",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        resp = client.send_api_request()
        page_items, total = _parse_items_response(resp)

        if total is not None:
            total_from_api = int(total)

        if not page_items:
            break

        all_items.extend(page_items)

        if total_from_api is not None and len(all_items) >= total_from_api:
            break

        if len(page_items) < limit:
            break

        offset += limit

    return all_items


def fetch_mural_items_by_creator(*, user_id, limit=30):
    params = {
        "created_by_id": user_id,
        "offset": 0,
        "limit": limit,
    }
    url = f"{MURAL_API_URL}/v1/items/by-created-by/?{urlencode(params)}"
    client = RequestClient(
        url=url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    resp = client.send_api_request()
    items, _total = _parse_items_response(resp)
    return items


def merge_author_items_missing_from_feed(items, *, user_id):
    """Autor com ger_mural vê no feed os próprios itens ativos ausentes do by-user."""
    existing_ids = {str(item.get("id")) for item in items}
    created_items = fetch_mural_items_by_creator(user_id=user_id)

    extras = []
    for raw_item in created_items:
        item_id = str(raw_item.get("id"))
        if item_id in existing_ids:
            continue
        if str(raw_item.get("created_by_id")) != str(user_id):
            continue
        if not raw_item.get("is_active", True):
            continue
        extras.append(raw_item)
        existing_ids.add(item_id)

    if not extras:
        return items

    return extras + items


def merge_pending_item_for_creator(items, *, pending_item_id, user_id):
    """Inclui item recém-criado no feed do autor quando a API ainda não o retorna."""
    if not pending_item_id:
        return items

    pending_key = str(pending_item_id)
    existing_ids = {str(item.get("id")) for item in items}

    if pending_key in existing_ids:
        return items

    raw_item = fetch_mural_item_by_id(pending_item_id)
    if not raw_item:
        return items

    if str(raw_item.get("created_by_id")) != str(user_id):
        return items

    if not raw_item.get("is_active", True):
        return items

    return [raw_item] + items
