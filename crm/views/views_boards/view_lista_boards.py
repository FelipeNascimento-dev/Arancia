from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import BoardForm
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.pagination import build_api_pagination
from crm_api.payloads import board_payload
from crm_api.services import boards as boards_service
from crm.views.views_tasks._helpers import load_board_lookups, menu_context


@crm_permission_required("view_board")
def lista_boards(request):
    client = CrmApiClient(request)
    q = request.GET.get("q", "").strip()
    pagination = build_api_pagination(request, [])
    items = []
    lookups = load_board_lookups(client)
    form = BoardForm(lookups=lookups, nome_form="Novo Board")

    if request.method == "POST" and (
        "create_board" in request.POST or "register" in request.POST
    ):
        if not request.user.has_perm("crm.add_board"):
            messages.error(request, "Você não tem permissão para criar boards.")
            return redirect("crm:lista_boards")
        form = BoardForm(request.POST, lookups=lookups, nome_form="Novo Board")
        if form.is_valid():
            try:
                boards_service.create_board(client, board_payload(form.cleaned_data, is_create=True))
                messages.success(request, "Board criado com sucesso!")
                return redirect("crm:lista_boards")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Erro ao criar board. Verifique os campos.")

    try:
        items, total = boards_service.list_boards(
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
        "crm/templates_boards/lista_boards.html",
        {
            "site_title": "CRM — Boards",
            "items": items,
            "pagination": pagination,
            "q": q,
            "form": form,
            **menu_context("crm_boards"),
        },
    )
