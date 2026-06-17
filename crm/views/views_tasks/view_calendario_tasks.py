from django.contrib import messages
from django.shortcuts import render

from crm.decorators import crm_permission_required
from crm.views.views_tasks._helpers import fetch_calendar_tasks, menu_context


@crm_permission_required("view_task")
def calendario_tasks(request):
    items, pagination, filters, lookups, error_message = fetch_calendar_tasks(request)
    if error_message:
        messages.error(request, error_message)

    return render(
        request,
        "crm/templates_tasks/calendario_tasks.html",
        {
            "site_title": "CRM — Calendário de Tasks",
            "items": items,
            "pagination": pagination,
            "filters": filters,
            "lookups": lookups,
            "list_mode": "calendar",
            **menu_context("projetos_tasks", "calendar"),
        },
    )
