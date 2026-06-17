import math


def build_api_pagination(request, items, *, page=None, limit=None, total_items=None):
    """Paginação estilo mural para respostas da API CRM."""
    page = max(1, int(page or request.GET.get("page", 1)))
    limit = max(1, min(100, int(limit or request.GET.get("limit", 10))))
    offset = (page - 1) * limit

    total_known = total_items is not None
    if total_known:
        total_pages = max(1, math.ceil(total_items / limit))
        has_previous = page > 1
        has_next = page < total_pages
    else:
        total_items = offset + len(items)
        total_pages = page + 1 if len(items) == limit else page
        has_previous = page > 1
        has_next = len(items) == limit

    previous_page = page - 1 if has_previous else None
    next_page = page + 1 if has_next else None

    def build_page_url(page_number):
        query_params = request.GET.copy()
        query_params["page"] = page_number
        query_params["limit"] = limit
        return f"{request.path}?{query_params.urlencode()}"

    return {
        "page": page,
        "limit": limit,
        "offset": offset,
        "total_items": total_items,
        "total_pages": total_pages,
        "total_known": total_known,
        "has_previous": has_previous,
        "has_next": has_next,
        "previous_page": previous_page,
        "next_page": next_page,
        "previous_url": build_page_url(previous_page) if previous_page else "",
        "next_url": build_page_url(next_page) if next_page else "",
    }
