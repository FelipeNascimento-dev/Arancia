from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import BoardForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import board_payload
from crm_api.services import boards as boards_service
from crm.views.views_tasks._helpers import load_board_lookups, menu_context


def _board_initial(board):
    if not board:
        return {}
    return {
        "name": board.get("name") or board.get("nome"),
        "description": board.get("description") or board.get("descricao"),
        "column_template_id": board.get("column_template_id"),
        "is_active": board.get("is_active", True),
    }


@crm_permission_required("view_board")
def form_board(request, board_id=None):
    client = CrmApiClient(request)
    lookups = load_board_lookups(client)
    is_edit = board_id is not None
    board = None

    if is_edit:
        try:
            board = boards_service.get_board(client, board_id)
        except CrmApiError as exc:
            messages.error(request, crm_error_message_pt(exc))
            return redirect("crm:lista_boards")

    form = BoardForm(
        lookups=lookups,
        nome_form="Editar Board" if is_edit else "Novo Board",
        initial_data=_board_initial(board),
    )

    if request.method == "POST":
        action_ok = (
            ("edit_board" in request.POST and is_edit)
            or ("create_board" in request.POST and not is_edit)
        )
        if not action_ok:
            return redirect("crm:lista_boards")

        perm = "crm.change_board" if is_edit else "crm.add_board"
        if not request.user.has_perm(perm):
            messages.error(request, "Você não tem permissão para esta ação.")
            return redirect("crm:lista_boards")

        form = BoardForm(request.POST, lookups=lookups, nome_form=form.nome_formulario)
        if form.is_valid():
            try:
                payload = board_payload(form.cleaned_data)
                if is_edit:
                    boards_service.update_board(client, board_id, payload)
                    messages.success(request, "Board atualizado com sucesso!")
                    return redirect("crm:kanban_board", board_id=board_id)
                created = boards_service.create_board(client, payload)
                new_id = (created or {}).get("id")
                messages.success(request, "Board criado com sucesso!")
                if new_id:
                    return redirect("crm:kanban_board", board_id=new_id)
                return redirect("crm:lista_boards")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao salvar board. Verifique os campos.")

    return render(
        request,
        "crm/templates_boards/form_board.html",
        {
            "site_title": f"CRM — {'Editar' if is_edit else 'Novo'} Board",
            "form": form,
            "is_edit": is_edit,
            "board_id": board_id,
            "board": board,
            **menu_context("crm_boards"),
        },
    )
