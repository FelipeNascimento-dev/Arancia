from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import ProjectForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import project_payload
from crm_api.services import projects as projects_service
from crm.views.views_tasks._helpers import load_project_lookups, menu_context


@crm_permission_required("view_project")
def detalhe_projeto(request, project_id):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    lookups = load_project_lookups(client)
    active_tab = request.GET.get("tab", "principal")
    projeto = None
    projetos = []

    try:
        projeto = projects_service.get_project(client, project_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:lista_projetos")

    edit_form = ProjectForm(
        initial={
            "name": projeto.get("name") or projeto.get("nome"),
            "description": projeto.get("description") or projeto.get("descricao"),
            "customer_gai_id": projeto.get("customer_gai_id"),
            "is_active": projeto.get("is_active", True),
        },
        lookups=lookups,
        nome_form="Editar Projeto",
    )

    if request.method == "POST" and "edit_project" in request.POST:
        if not request.user.has_perm("crm.change_project"):
            messages.error(request, "Você não tem permissão para alterar projetos.")
            return redirect("crm:detalhe_projeto", project_id=project_id)
        edit_form = ProjectForm(request.POST, lookups=lookups, nome_form="Editar Projeto")
        if edit_form.is_valid():
            try:
                projects_service.update_project(
                    client, project_id, project_payload(edit_form.cleaned_data),
                )
                messages.success(request, "Projeto atualizado com sucesso!")
                return redirect("crm:detalhe_projeto", project_id=project_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    try:
        projetos, _ = projects_service.list_projects(client, limit=100, q=q or None)
    except CrmApiError:
        projetos = []

    return render(
        request,
        "crm/templates_projetos/detalhe_projeto.html",
        {
            "site_title": f"CRM — {projeto.get('name') or projeto.get('nome') or project_id}",
            "projeto": projeto,
            "project_id": project_id,
            "projetos": projetos,
            "edit_form": edit_form,
            "active_tab": active_tab,
            "q": q,
            **menu_context("crm_projetos"),
        },
    )
