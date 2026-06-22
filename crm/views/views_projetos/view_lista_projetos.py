from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import ProjectForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.payloads import project_payload
from crm_api.services import projects as projects_service
from crm.views.views_tasks._helpers import load_project_lookups, menu_context


@crm_permission_required("view_project")
def lista_projetos(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    pagination = build_api_pagination(request, [])
    items = []
    lookups = load_project_lookups(client)
    form = ProjectForm(lookups=lookups, nome_form="Novo Projeto")

    if request.method == "POST" and (
        "create_project" in request.POST or "register" in request.POST
    ):
        if not request.user.has_perm("crm.add_project"):
            messages.error(request, "Você não tem permissão para criar projetos.")
            return redirect("crm:lista_projetos")
        form = ProjectForm(request.POST, lookups=lookups, nome_form="Novo Projeto")
        if form.is_valid():
            try:
                projects_service.create_project(
                    client, project_payload(form.cleaned_data, is_create=True),
                )
                messages.success(request, "Projeto criado com sucesso!")
                return redirect("crm:lista_projetos")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar projeto. Verifique os campos.")

    try:
        items, total = projects_service.list_projects(
            client,
            skip=pagination["offset"],
            limit=pagination["limit"],
            q=q or None,
        )
        pagination = build_api_pagination(request, items, total_items=total)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_projetos/lista_projetos.html",
        {
            "site_title": "CRM — Projetos",
            "items": items,
            "pagination": pagination,
            "q": q,
            "form": form,
            "lookups": lookups,
            **menu_context("crm_projetos"),
        },
    )
