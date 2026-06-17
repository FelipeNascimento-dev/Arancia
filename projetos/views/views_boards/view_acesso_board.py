from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import BoardAccessForm
from crm.helpers.api_display import enrich_board
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import board_access_payload
from crm_api.services import boards as boards_service
from projetos.views._helpers import load_board_lookups, menu_context


@crm_permission_required("view_board")
def acesso_board(request, board_id):
    client = CrmApiClient(request)
    lookups = load_board_lookups(client)
    board = None
    grants = []
    access_form = BoardAccessForm(lookups=lookups)

    try:
        board = enrich_board(boards_service.get_board(client, board_id))
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:lista_boards")

    if request.method == "POST" and "add_access" in request.POST:
        if not request.user.has_perm("crm.manage_board_access"):
            messages.error(request, "Você não tem permissão para gerenciar acessos.")
            return redirect("projetos:acesso_board", board_id=board_id)
        access_form = BoardAccessForm(request.POST, lookups=lookups)
        if access_form.is_valid():
            try:
                boards_service.add_access(
                    client, board_id, board_access_payload(access_form.cleaned_data),
                )
                messages.success(request, "Acesso concedido com sucesso!")
                return redirect("projetos:acesso_board", board_id=board_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "remove_access" in request.POST:
        access_id = request.POST.get("access_id")
        if access_id and request.user.has_perm("crm.manage_board_access"):
            try:
                boards_service.remove_access(client, board_id, access_id)
                messages.success(request, "Acesso removido.")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:acesso_board", board_id=board_id)

    elif request.method == "POST" and "edit_access" in request.POST:
        access_id = request.POST.get("access_id")
        if access_id and request.user.has_perm("crm.manage_board_access"):
            payload = {}
            access_level = request.POST.get("access_level")
            if access_level:
                payload["access_level"] = access_level
            try:
                boards_service.update_access(client, board_id, access_id, payload)
                messages.success(request, "Acesso atualizado.")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        return redirect("projetos:acesso_board", board_id=board_id)

    try:
        grants = boards_service.list_access(client, board_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "projetos/templates_boards/acesso_board.html",
        {
            "site_title": f"Projetos — Acesso — {board.get('name') or board_id}",
            "board": board,
            "board_id": board_id,
            "grants": grants,
            "access_form": access_form,
            **menu_context("projetos_boards"),
        },
    )
