from crm.helpers.api_display import enrich_board_column
from crm.forms import BoardColumnForm
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import board_column_payload
from crm_api.services import boards as boards_service
from crm_api.services.boards import _column_sort_key


def load_board_columns(client, board_id, lookups):
    columns = boards_service.list_columns(client, board_id)
    columns = sorted(columns, key=_column_sort_key)
    return [enrich_board_column(c, lookups) for c in columns]


def handle_column_post(request, client, board_id, lookups, column_form):
    """
    Processa POST de criar/editar coluna.

    Retorna dict com column_form, ui_state e redirect (bool).
    """
    from django.contrib import messages

    ui_state = {
        "manage_columns_modal": False,
        "create_column_modal": False,
        "edit_column_modal": False,
        "edit_column_post": None,
    }
    redirect = False

    if request.method != "POST":
        return {"column_form": column_form, "ui_state": ui_state, "redirect": redirect}

    if "add_column" in request.POST:
        ui_state["manage_columns_modal"] = True
        ui_state["create_column_modal"] = True
        if not request.user.has_perm("crm.manage_board_columns"):
            messages.error(request, "Você não tem permissão para gerenciar colunas.")
            return {"column_form": column_form, "ui_state": ui_state, "redirect": redirect}
        column_form = BoardColumnForm(request.POST, lookups=lookups)
        if column_form.is_valid():
            try:
                boards_service.create_column(
                    client, board_id, board_column_payload(column_form.cleaned_data),
                )
                messages.success(request, "Coluna adicionada!")
                return {
                    "column_form": BoardColumnForm(lookups=lookups),
                    "ui_state": ui_state,
                    "redirect": True,
                }
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        return {"column_form": column_form, "ui_state": ui_state, "redirect": redirect}

    if "edit_column" in request.POST:
        ui_state["manage_columns_modal"] = True
        ui_state["edit_column_modal"] = True
        column_id = request.POST.get("column_id")
        if column_id and request.user.has_perm("crm.manage_board_columns"):
            payload = {
                "name": request.POST.get("name"),
                "status_task_id": request.POST.get("status_task_id"),
                "position": request.POST.get("position"),
            }
            payload = {k: v for k, v in payload.items() if v not in (None, "")}
            try:
                boards_service.update_column(client, board_id, column_id, payload)
                messages.success(request, "Coluna atualizada.")
                return {
                    "column_form": BoardColumnForm(lookups=lookups),
                    "ui_state": ui_state,
                    "redirect": True,
                }
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        ui_state["edit_column_post"] = {
            "column_id": request.POST.get("column_id", ""),
            "name": request.POST.get("name", ""),
            "status_task_id": request.POST.get("status_task_id", ""),
            "position": request.POST.get("position", ""),
        }
        return {"column_form": column_form, "ui_state": ui_state, "redirect": redirect}

    return {"column_form": column_form, "ui_state": ui_state, "redirect": redirect}
