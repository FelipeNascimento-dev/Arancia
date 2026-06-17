from django.contrib import messages
from django.shortcuts import render

from crm.decorators import crm_permission_required
from crm.views.views_tasks._helpers import fetch_task_list, menu_context


@crm_permission_required("view_task")
def lista_tasks(request):
    _, items, pagination, filters, lookups, error_message = fetch_task_list(request)
    if error_message:
        messages.error(request, error_message)

    return render(
        request,
        "crm/templates_tasks/lista_tasks.html",
        {
            "site_title": "CRM — Tasks",
            "items": items,
            "pagination": pagination,
            "filters": filters,
            "lookups": lookups,
            "list_mode": "all",
            **menu_context("projetos_tasks", "lista"),
        },
    )
