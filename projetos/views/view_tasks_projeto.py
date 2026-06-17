from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.helpers.api_display import enrich_project
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.services import projects as projects_service
from crm.views.views_tasks._helpers import enrich_task_for_display, load_task_lookups, menu_context, task_display_value


@crm_permission_required("view_project")
def tasks_projeto(request, project_id):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    status_id = request.GET.get("status_id") or None
    requester_gai_id = request.GET.get("requester_gai_id") or None
    pagination = build_api_pagination(request, [], limit=request.GET.get("limit", 20))
    projeto = None
    items = []
    lookups = load_task_lookups(client)

    try:
        projeto = enrich_project(projects_service.get_project(client, project_id))
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:lista_projetos")

    try:
        items, total = projects_service.list_project_tasks(
            client,
            project_id,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
            status_id=status_id,
            requester_gai_id=requester_gai_id,
        )
        items = [enrich_task_for_display(item) for item in items]
        pagination = build_api_pagination(
            request, items, total_items=total, limit=pagination["limit"],
        )
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "projetos/templates_projetos/tasks_projeto.html",
        {
            "site_title": f"Projetos — Tasks — {projeto.get('name') or project_id}",
            "projeto": projeto,
            "project_id": project_id,
            "items": items,
            "pagination": pagination,
            "q": q,
            "status_id": status_id,
            "requester_gai_id": requester_gai_id,
            "lookups": lookups,
            "task_display_value": task_display_value,
            **menu_context("projetos_detalhe", "tasks"),
        },
    )
