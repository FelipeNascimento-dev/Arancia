from django.conf import settings

from crm.helpers.api_display import enrich_task_lookups, nested_label
from crm.helpers.lookup_entities import (
    django_designations,
    django_system_gais,
    django_system_users,
    merge_gai_candidate_lists,
    normalize_lookup_designations,
    normalize_lookup_users,
)
from crm.helpers.date_format import format_datetime_br
from crm.helpers.lookup_cache import get_cached_lookup_for_client
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import clients as clients_service
from crm_api.services import projects as projects_service
from crm_api.services import tasks as tasks_service
from crm_api.services.lookups import (
    get_board_page,
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


def _use_aggregated_endpoints():
    return getattr(settings, "CRM_USE_AGGREGATED_ENDPOINTS", True)


def _get_board_page_bundle(client: CrmApiClient):
    return get_cached_lookup_for_client(
        client,
        "board_page",
        lambda: get_board_page(client, gais_limit=50),
        redis_key="lookups:board-page",
    )


def _normalize_column_templates(raw):
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, dict):
        return []
    items = raw.get("items") or raw.get("results")
    if isinstance(items, list):
        return items
    templates = raw.get("templates")
    if isinstance(templates, dict):
        flattened = []
        for group in templates.values():
            if isinstance(group, list):
                flattened.extend(group)
        return flattened
    if isinstance(templates, list):
        return templates
    return []


def _normalize_lookup_list(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("items") or raw.get("results") or []
    return []


def _derive_task_lookups_from_board_page(board_page, client: CrmApiClient):
    page = board_page or {}
    crm_lookups = _normalize_crm_lookups(page.get("crm") or {})
    lookups = enrich_task_lookups(crm_lookups) if crm_lookups else {}

    gais = merge_gai_candidate_lists(
        _filter_active_gais(page.get("gais") or []),
        crm_lookups.get("customers"),
    )
    if gais:
        lookups["gais"] = gais
    elif not lookups.get("gais"):
        lookups["gais"] = _load_active_gais(client, crm_lookups=crm_lookups)

    users = normalize_lookup_users(lookups.get("users") or [])
    if users:
        lookups["users"] = users
    else:
        lookups["users"] = _load_system_users(client, crm_lookups=crm_lookups)

    designations = normalize_lookup_designations(lookups.get("designations") or [])
    if designations:
        lookups["designations"] = designations
    else:
        lookups["designations"] = _load_designations(client, crm_lookups=crm_lookups)

    return enrich_task_lookups(lookups)


def _derive_board_lookups_from_board_page(board_page, client: CrmApiClient):
    lookups = dict(_derive_task_lookups_from_board_page(board_page, client))
    page = board_page or {}

    groups = _normalize_lookup_list(page.get("groups"))
    if groups:
        lookups["groups"] = groups
    else:
        lookups.setdefault("groups", [])

    templates = _normalize_column_templates(page.get("column_templates"))
    if templates:
        lookups["column_templates"] = templates
    else:
        lookups.setdefault("column_templates", [])

    crm = _normalize_crm_lookups(page.get("crm") or {})
    if crm.get("boards"):
        lookups["boards"] = crm.get("boards")
    else:
        lookups["boards"] = _load_boards_list(client)

    return enrich_task_lookups(lookups)


def resolve_comercial_board_id(client: CrmApiClient, *, board_page=None):
    """Resolve board comercial UUID — board-page quando agregado, senão fan-out legado."""
    from crm_api.exceptions import CrmNotFoundError
    from crm_api.services import boards as boards_service
    from crm_api.services.boards import resolve_board_id_from_page

    if _use_aggregated_endpoints():
        page = board_page if board_page is not None else _get_board_page_bundle(client)
        board_id = resolve_board_id_from_page(page)
        if board_id:
            return board_id

    return boards_service.get_comercial_board_id(client)


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


def _load_active_gais(client: CrmApiClient, *, crm_lookups=None):
    def _fetch():
        items = []
        try:
            items = unwrap_lookup_items(get_gais(client))
        except CrmApiError:
            pass

        crm = crm_lookups
        if crm is None:
            try:
                crm = _get_crm_lookups_normalized(client)
            except Exception:
                crm = {}

        gais = merge_gai_candidate_lists(
            _filter_active_gais(items),
            (crm or {}).get("customers"),
        )
        if gais:
            return gais

        try:
            clients, _ = clients_service.list_clients(client, limit=500)
            gais = merge_gai_candidate_lists(_filter_active_gais(clients))
            if gais:
                return gais
        except CrmApiError:
            pass

        return django_system_gais()

    return get_cached_lookup_for_client(
        client,
        "gais",
        _fetch,
        redis_key="lookups:gais",
    )


def _get_crm_lookups_normalized(client: CrmApiClient):
    def _fetch():
        try:
            return _normalize_crm_lookups(get_crm_lookups(client) or {})
        except CrmApiError:
            return {}

    return get_cached_lookup_for_client(
        client,
        "crm_lookups_raw",
        _fetch,
        redis_key="lookups:crm",
    )


def _load_system_users(client: CrmApiClient, *, crm_lookups=None):
    candidates = []
    try:
        candidates = unwrap_lookup_items(get_users(client))
    except CrmApiError:
        pass

    if not candidates:
        crm = crm_lookups if crm_lookups is not None else _get_crm_lookups_normalized(client)
        users = crm.get("users")
        if isinstance(users, list):
            candidates = users
        elif isinstance(users, dict):
            candidates = unwrap_lookup_items(users)

    users = normalize_lookup_users(candidates)
    return users if users else django_system_users()


def _load_designations(client: CrmApiClient, *, crm_lookups=None):
    candidates = []
    try:
        candidates = unwrap_lookup_items(get_designations(client))
    except CrmApiError:
        pass

    if not candidates:
        crm = crm_lookups if crm_lookups is not None else _get_crm_lookups_normalized(client)
        designations = crm.get("designations")
        if isinstance(designations, list):
            candidates = designations
        elif isinstance(designations, dict):
            candidates = unwrap_lookup_items(designations)

    designations = normalize_lookup_designations(candidates)
    return designations if designations else django_designations()


def _load_task_lookups(client: CrmApiClient):
    if _use_aggregated_endpoints():
        lookups = _derive_task_lookups_from_board_page(
            _get_board_page_bundle(client), client,
        )
    else:
        crm_lookups = _get_crm_lookups_normalized(client)
        lookups = enrich_task_lookups(crm_lookups) if crm_lookups else {}

        if not lookups.get("gais"):
            lookups["gais"] = _load_active_gais(client, crm_lookups=crm_lookups)
        if not lookups.get("users"):
            lookups["users"] = _load_system_users(client, crm_lookups=crm_lookups)
        if not lookups.get("designations"):
            lookups["designations"] = _load_designations(client, crm_lookups=crm_lookups)

        lookups = enrich_task_lookups(lookups)

    if not lookups.get("projects"):
        try:
            projects, _ = projects_service.list_projects(client, limit=200)
            lookups["projects"] = projects
        except CrmApiError:
            lookups.setdefault("projects", [])

    return enrich_task_lookups(lookups)


def load_task_lookups(client: CrmApiClient):
    return get_cached_lookup_for_client(
        client,
        "task_lookups",
        lambda: _load_task_lookups(client),
    )


def _load_project_lookups(client: CrmApiClient):
    lookups = dict(load_task_lookups(client))
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
    return enrich_task_lookups(lookups)


def load_project_lookups(client: CrmApiClient):
    return get_cached_lookup_for_client(
        client,
        "project_lookups",
        lambda: _load_project_lookups(client),
    )


def _load_board_lookups(client: CrmApiClient):
    if _use_aggregated_endpoints():
        lookups = _derive_board_lookups_from_board_page(_get_board_page_bundle(client), client)
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
        return enrich_task_lookups(lookups)

    lookups = dict(load_project_lookups(client))
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
    lookups["boards"] = _load_boards_list(client)
    return enrich_task_lookups(lookups)


def load_board_lookups(client: CrmApiClient):
    return get_cached_lookup_for_client(
        client,
        "board_lookups",
        lambda: _load_board_lookups(client),
    )


def _load_boards_list(client: CrmApiClient):
    def _fetch():
        try:
            from crm_api.services import boards as boards_service

            boards, _ = boards_service.list_boards(client, limit=200)
            return boards
        except CrmApiError:
            return []

    return get_cached_lookup_for_client(client, "boards_list", _fetch)


def _load_task_list_lookups(client: CrmApiClient):
    """Lookups para listagens de tasks — sem groups/column-templates."""
    lookups = dict(load_project_lookups(client))
    lookups["boards"] = _load_boards_list(client)
    return enrich_task_lookups(lookups)


def load_task_list_lookups(client: CrmApiClient):
    return get_cached_lookup_for_client(
        client,
        "task_list_lookups",
        lambda: _load_task_list_lookups(client),
    )


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


def enrich_task_for_kanban_card(task):
    """Campos mínimos para card Kanban — evita enrichment completo em listagens."""
    if not isinstance(task, dict):
        return task
    priority = task.get("priority") or {}
    due_raw = task.get("due_at") or task.get("due_date") or task.get("data_vencimento")
    return {
        **task,
        "display_due": format_datetime_br(due_raw, default="-"),
        "priority_name": nested_label(priority, "name", "nome") or task.get("priority_name") or "",
    }


def enrich_task_for_display(task):
    if not isinstance(task, dict):
        return task
    board = task.get("board") or {}
    status = task.get("status") or {}
    priority = task.get("priority") or {}
    project = task.get("project") or {}
    customer = task.get("customer") or {}
    due_raw = task.get("due_at") or task.get("due_date") or task.get("data_vencimento")
    return {
        **task,
        "display_title": task.get("title") or task.get("titulo") or task.get("nome") or "-",
        "display_status": nested_label(status, "name", "nome") or task.get("status_name") or "-",
        "display_board": nested_label(board, "name", "nome") or task.get("board_name") or "-",
        "display_priority": nested_label(priority, "name", "nome") or task.get("priority_name") or "-",
        "display_project": nested_label(project, "name", "nome", "title") or task.get("project_name") or "-",
        "display_customer": nested_label(customer, "nome", "name", "razao_social") or "-",
        "display_due": format_datetime_br(due_raw, default="-"),
        "display_scheduled_start": format_datetime_br(task.get("scheduled_start_at"), default="-"),
        "display_scheduled_end": format_datetime_br(task.get("scheduled_end_at"), default="-"),
        "display_created_at": format_datetime_br(
            task.get("created_at") or task.get("created_on"),
            default="",
        ),
        "display_created_by": (
            task.get("created_by_username")
            or task.get("creator_username")
            or task.get("author_username")
            or nested_label(task.get("created_by") or {}, "username", "name", "nome")
            or ""
        ),
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


def _enrich_person_entity(entity, *, user_map=None, designation_map=None, label_key="display_name"):
    from crm.helpers.user_display import resolve_person_display

    if not isinstance(entity, dict):
        return entity
    person = resolve_person_display(
        entity,
        user_map=user_map,
        designation_map=designation_map,
    )
    display_name = person["display_name"]
    if display_name == "-" and entity.get("customer_gai_id") not in (None, ""):
        display_name = (
            entity.get("customer_gai_name")
            or entity.get("gai_name")
            or f"GAI {entity.get('customer_gai_id')}"
        )
    return {
        **entity,
        label_key: display_name,
        "avatar_url": person["avatar_url"],
        "display_initials": person["initials"],
    }


def enrich_move_history_for_display(entry, *, user_map=None, designation_map=None):
    if not isinstance(entry, dict):
        return entry
    from_status = entry.get("from_status") or {}
    to_status = entry.get("to_status") or {}
    person = _enrich_person_entity(
        entry,
        user_map=user_map,
        designation_map=designation_map,
        label_key="display_user",
    )
    return {
        **entry,
        "display_moved_at": format_datetime_br(
            entry.get("moved_at") or entry.get("created_at"),
            default="-",
        ),
        "display_from_status": nested_label(from_status, "name", "nome") or entry.get("from_status_name") or "-",
        "display_to_status": nested_label(to_status, "name", "nome") or entry.get("to_status_name") or "-",
        "display_user": person["display_user"],
    }


def enrich_assignee_for_display(assignee, *, user_map=None, designation_map=None):
    return _enrich_person_entity(
        assignee,
        user_map=user_map,
        designation_map=designation_map,
        label_key="display_name",
    )


def enrich_watchers_for_display(watchers):
    from crm.helpers.user_display import build_person_resolver

    resolver = build_person_resolver(watchers)
    return [
        enrich_watcher_for_display(
            watcher,
            user_map=resolver["users"],
            designation_map=resolver["designations"],
        )
        for watcher in (watchers or [])
    ]


def enrich_watcher_for_display(watcher, *, user_map=None, designation_map=None):
    return _enrich_person_entity(
        watcher,
        user_map=user_map,
        designation_map=designation_map,
        label_key="display_name",
    )


def enrich_assignees_for_display(assignees):
    from crm.helpers.user_display import build_person_resolver

    resolver = build_person_resolver(assignees)
    return [
        enrich_assignee_for_display(
            assignee,
            user_map=resolver["users"],
            designation_map=resolver["designations"],
        )
        for assignee in (assignees or [])
    ]


def enrich_comments_for_display(comments):
    from crm.helpers.user_display import build_person_resolver

    resolver = build_person_resolver(comments)
    return [
        enrich_comment_for_display(
            comment,
            user_map=resolver["users"],
            designation_map=resolver["designations"],
        )
        for comment in (comments or [])
    ]


def enrich_comment_for_display(comment, *, user_map=None, designation_map=None):
    if not isinstance(comment, dict):
        return comment
    enriched = _enrich_person_entity(
        comment,
        user_map=user_map,
        designation_map=designation_map,
        label_key="display_author",
    )
    if enriched.get("display_author") == "-":
        enriched["display_author"] = "Usuário"
    enriched["display_body"] = (
        comment.get("content") or comment.get("body") or comment.get("text") or ""
    )
    return enriched


def enrich_move_history_for_display_list(entries):
    from crm.helpers.user_display import build_person_resolver

    resolver = build_person_resolver(entries)
    return [
        enrich_move_history_for_display(
            entry,
            user_map=resolver["users"],
            designation_map=resolver["designations"],
        )
        for entry in (entries or [])
    ]


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
        lookups = load_task_list_lookups(client)
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
    if board_access.get("can_comment") is False:
        return False
    return True


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
