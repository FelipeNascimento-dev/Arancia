from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import project_payload
from crm_api.services import projects as projects_service
from projetos.forms import ProjectForm
from projetos.views._helpers import load_project_lookups, menu_context


@crm_permission_required("view_project")
def form_projeto(request, project_id):
    if not request.user.has_perm("crm.change_project"):
        raise PermissionDenied

    client = CrmApiClient(request)
    lookups = load_project_lookups(client)

    try:
        projeto = projects_service.get_project(client, project_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:lista_projetos")

    form = ProjectForm(
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
        form = ProjectForm(request.POST, lookups=lookups, nome_form="Editar Projeto")
        if form.is_valid():
            try:
                projects_service.update_project(
                    client, project_id, project_payload(form.cleaned_data),
                )
                messages.success(request, "Projeto atualizado com sucesso!")
                return redirect("projetos:detalhe_projeto", project_id=project_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao salvar. Verifique os campos.")

    return render(
        request,
        "projetos/templates_projetos/form_projeto.html",
        {
            "site_title": f"Projetos — Editar — {projeto.get('name') or project_id}",
            "form": form,
            "projeto": projeto,
            "project_id": project_id,
            **menu_context("projetos_detalhe", "editar"),
        },
    )
