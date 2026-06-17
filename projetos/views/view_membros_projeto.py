from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.helpers.api_display import enrich_project
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import project_member_payload
from crm_api.services import projects as projects_service
from projetos.forms import ProjectMemberForm
from projetos.views._helpers import load_project_lookups, menu_context


def _member_payload_from_form(cleaned_data):
    member_type = cleaned_data.get("member_type")
    payload = {"role": cleaned_data.get("role")}
    if member_type == "user":
        payload["user_id"] = cleaned_data.get("user_id")
    elif member_type == "designation":
        payload["designation_id"] = cleaned_data.get("designation_id")
    elif member_type == "team_gai":
        payload["team_gai_id"] = cleaned_data.get("team_gai_id")
    return {k: v for k, v in payload.items() if v not in (None, "")}


@crm_permission_required("view_project")
def membros_projeto(request, project_id):
    client = CrmApiClient(request)
    lookups = load_project_lookups(client)
    projeto = None
    membros = []
    member_form = ProjectMemberForm(lookups=lookups)

    try:
        projeto = enrich_project(projects_service.get_project(client, project_id))
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:lista_projetos")

    if request.method == "POST" and (
        "add_member" in request.POST or "register" in request.POST
    ):
        if not request.user.has_perm("crm.manage_project_members"):
            messages.error(request, "Você não tem permissão para gerenciar membros.")
            return redirect("projetos:membros_projeto", project_id=project_id)
        member_form = ProjectMemberForm(request.POST, lookups=lookups)
        if member_form.is_valid():
            try:
                projects_service.add_member(
                    client, project_id, _member_payload_from_form(member_form.cleaned_data),
                )
                messages.success(request, "Membro adicionado com sucesso!")
                return redirect("projetos:membros_projeto", project_id=project_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "remove_member" in request.POST:
        member_id = request.POST.get("member_id")
        if member_id and request.user.has_perm("crm.manage_project_members"):
            try:
                projects_service.remove_member(client, project_id, member_id)
                messages.success(request, "Membro removido.")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:membros_projeto", project_id=project_id)

    try:
        membros = projects_service.list_members(client, project_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "projetos/templates_projetos/membros_projeto.html",
        {
            "site_title": f"Projetos — Membros — {projeto.get('name') or project_id}",
            "projeto": projeto,
            "project_id": project_id,
            "membros": membros,
            "member_form": member_form,
            **menu_context("projetos_detalhe", "membros"),
        },
    )
