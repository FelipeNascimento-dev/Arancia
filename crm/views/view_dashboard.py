from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse

from crm.decorators import crm_any_access_required
from crm.context_processors import crm_menu_context
from crm.helpers.dashboard import build_chart_data, build_summary_cards
from crm.helpers.date_format import format_datetime_br
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.services import alerts as alerts_service
from crm_api.services import billing as billing_service


def _menu_context(current_menu, current_submenu=None):
    return {
        "current_parent_menu": "crm",
        "current_menu": current_menu,
        "current_submenu": current_submenu,
    }


def _nested_label(entity, *flat_keys):
    if not entity or not isinstance(entity, dict):
        return ""
    for key in flat_keys:
        value = entity.get(key)
        if value not in (None, ""):
            return value
    return ""


def _enrich_alert(alert):
    if not isinstance(alert, dict):
        return alert
    customer = alert.get("customer") or {}
    contract = alert.get("contract") or {}
    return {
        **alert,
        "display_title": alert.get("title") or alert.get("titulo") or "Alerta",
        "display_customer": _nested_label(customer, "nome", "name") or alert.get("customer_name") or alert.get("client_name") or "",
        "display_contract": _nested_label(contract, "numero", "number", "titulo", "title") or alert.get("contract_number") or "",
    }


def _enrich_task(task):
    if not isinstance(task, dict):
        return task
    board = task.get("board") or {}
    status = task.get("status") or {}
    return {
        **task,
        "display_title": task.get("title") or task.get("titulo") or "Task",
        "display_due": format_datetime_br(
            task.get("due_date") or task.get("due_at") or task.get("data_vencimento"),
            default="-",
        ),
        "display_board": _nested_label(board, "name", "nome") or task.get("board_name") or "",
        "display_status": _nested_label(status, "name", "nome") or task.get("status_name") or "",
        "task_id": task.get("id"),
    }


def _build_shortcuts(user, crm_context):
    shortcuts = []
    comercial_code = getattr(settings, "CRM_COMERCIAL_BOARD_CODE", "crm_comercial")
    spec = [
        ("crm.view_clients", "Clientes", "crm:lista_clientes", "fa-building"),
        ("crm.view_contract", "Contratos", "crm:lista_contratos", "fa-file-contract"),
        ("crm.view_billing", "Faturamento", "crm:lista_faturamento", "fa-file-invoice-dollar"),
        ("crm.view_contract", "Alertas", "crm:lista_alertas", "fa-bell"),
        ("crm.view_task", "Minhas Tasks", "crm:minhas_tasks", "fa-list-check"),
        ("crm.view_task", "Todas as Tasks", "crm:lista_tasks", "fa-tasks"),
        ("crm.view_board", "Projeto CRM Comercial", "crm:kanban_comercial", "fa-handshake"),
        ("crm.view_project", "Projetos", "projetos:lista_projetos", "fa-diagram-project"),
        ("crm.view_board", "Boards", "projetos:lista_boards", "fa-table-columns"),
        ("crm.view_settings", "Configurações", "crm:config_index", "fa-gear"),
    ]
    for perm, label, url_name, icon in spec:
        if user.has_perm(perm):
            shortcuts.append({
                "label": label,
                "href": reverse(url_name),
                "icon": icon,
            })

    for board in (crm_context or {}).get("accessible_boards") or []:
        board_id = board.get("id")
        if board_id is None:
            continue
        board_code = board.get("code") or board.get("codigo")
        try:
            if board_code == comercial_code:
                href = reverse("crm:kanban_comercial")
            else:
                href = reverse("projetos:kanban_board", kwargs={"board_id": board_id})
        except NoReverseMatch:
            continue
        shortcuts.append({
            "label": f"Board: {board.get('name') or board.get('nome') or board_id}",
            "href": href,
            "icon": "fa-table-columns",
        })

    for project in (crm_context or {}).get("accessible_projects") or []:
        project_id = project.get("id")
        if project_id is None:
            continue
        try:
            href = reverse("projetos:detalhe_projeto", kwargs={"project_id": project_id})
        except NoReverseMatch:
            continue
        shortcuts.append({
            "label": f"Projeto: {project.get('name') or project.get('nome') or project_id}",
            "href": href,
            "icon": "fa-diagram-project",
        })

    return shortcuts


def _parse_task_list(tasks_data, limit=None):
    if isinstance(tasks_data, dict):
        raw_tasks = tasks_data.get("items") or tasks_data.get("results") or []
    elif isinstance(tasks_data, list):
        raw_tasks = tasks_data
    else:
        raw_tasks = []
    if limit is not None:
        raw_tasks = raw_tasks[:limit]
    return raw_tasks


@crm_any_access_required
def crm_dashboard(request):
    client = CrmApiClient(request)
    billing_data = {}
    summary_cards = []
    overdue_tasks = []
    my_tasks = []
    recent_alerts = []
    api_ok = True

    crm_context = crm_menu_context(request).get("crm_context", {})

    try:
        billing_data = billing_service.billing_summary(client) or {}
        summary_cards = build_summary_cards(billing_data)
    except CrmApiError as exc:
        api_ok = False
        messages.warning(request, crm_error_message_pt(exc))

    try:
        alerts_items, _ = alerts_service.list_alerts(client, limit=20)
        recent_alerts = [_enrich_alert(a) for a in alerts_items[:20]]
    except CrmApiError:
        pass

    try:
        tasks_data = client.get("/tasks/my/", params={"overdue_only": "true", "limit": 10})
        overdue_tasks = [_enrich_task(t) for t in _parse_task_list(tasks_data, limit=10)]
    except CrmApiError:
        pass

    try:
        tasks_data = client.get("/tasks/my/", params={"limit": 50})
        my_tasks = [_enrich_task(t) for t in _parse_task_list(tasks_data, limit=50)]
    except CrmApiError:
        pass

    chart_data = build_chart_data(billing_data, my_tasks, recent_alerts)
    shortcuts = _build_shortcuts(request.user, crm_context)

    return render(
        request,
        "crm/templates_dashboard/dashboard.html",
        {
            "site_title": "CRM — Dashboard",
            "summary_cards": summary_cards,
            "overdue_tasks": overdue_tasks,
            "recent_alerts": recent_alerts[:10],
            "shortcuts": shortcuts,
            "chart_data": chart_data,
            "api_ok": api_ok,
            "accessible_boards": crm_context.get("accessible_boards") or [],
            "accessible_projects": crm_context.get("accessible_projects") or [],
            **_menu_context("crm_dashboard"),
        },
    )
