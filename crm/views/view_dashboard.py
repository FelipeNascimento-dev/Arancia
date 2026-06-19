from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.urls import NoReverseMatch, reverse

from crm.context_processors import resolve_crm_context_data
from crm.decorators import crm_any_access_required
from crm.helpers.dashboard import build_chart_data, build_summary_cards
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.parallel import run_parallel_crm_fetches
from crm_api.services import billing as billing_service
from crm_api.services.dashboard import get_dashboard_summary


def _menu_context(current_menu, current_submenu=None):
    return {
        "current_parent_menu": "crm",
        "current_menu": current_menu,
        "current_submenu": current_submenu,
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


def _dashboard_needs_summary(user):
    return (
        user.has_perm("crm.view_billing")
        or user.has_perm("crm.view_contract")
        or user.has_perm("crm.view_task")
    )


def _load_dashboard_widgets_legacy(request, user):
    billing_data = {}
    api_ok = True

    jobs = []
    if user.has_perm("crm.view_billing"):
        jobs.append(
            ("billing", lambda c: billing_service.billing_summary(c) or {}),
        )

    results, errors = run_parallel_crm_fetches(request, jobs, max_workers=1)

    if "billing" in results:
        billing_data = results["billing"]
    elif "billing" in errors and isinstance(errors["billing"], CrmApiError):
        api_ok = False
        messages.warning(request, crm_error_message_pt(errors["billing"]))

    return billing_data, [], [], api_ok


def _load_dashboard_widgets_aggregated(request, user):
    billing_data = {}
    alerts = []
    my_tasks = []
    api_ok = True

    try:
        summary = get_dashboard_summary(CrmApiClient(request)) or {}
    except CrmApiError as exc:
        api_ok = False
        messages.warning(request, crm_error_message_pt(exc))
        return billing_data, alerts, my_tasks, api_ok

    if user.has_perm("crm.view_billing"):
        billing_data = summary.get("billing") or {}
    if user.has_perm("crm.view_contract"):
        alerts = summary.get("alerts") or []
    if user.has_perm("crm.view_task"):
        my_tasks = summary.get("my_tasks") or []

    return billing_data, alerts, my_tasks, api_ok


@crm_any_access_required
def crm_dashboard(request):
    crm_context = getattr(request, "_crm_context_data", None) or resolve_crm_context_data(request)
    user = request.user

    billing_data = {}
    alerts = []
    my_tasks = []
    api_ok = True

    if _dashboard_needs_summary(user):
        if getattr(settings, "CRM_USE_AGGREGATED_ENDPOINTS", True):
            billing_data, alerts, my_tasks, api_ok = _load_dashboard_widgets_aggregated(
                request, user,
            )
        else:
            billing_data, alerts, my_tasks, api_ok = _load_dashboard_widgets_legacy(
                request, user,
            )

    summary_cards = build_summary_cards(billing_data) if billing_data else []
    chart_data = build_chart_data(billing_data, alerts=alerts, my_tasks=my_tasks)
    shortcuts = _build_shortcuts(request.user, crm_context)

    return render(
        request,
        "crm/templates_dashboard/dashboard.html",
        {
            "site_title": "CRM — Dashboard",
            "summary_cards": summary_cards,
            "shortcuts": shortcuts,
            "chart_data": chart_data,
            "api_ok": api_ok,
            **_menu_context("crm_dashboard"),
        },
    )
