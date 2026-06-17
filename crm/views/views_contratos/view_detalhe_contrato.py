from django.contrib import messages
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import ContractFileForm, ContractForm
from crm.helpers.api_display import contract_initial, enrich_contract
from crm.views.views_contratos._helpers import contract_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import contract_payload
from crm_api.services import contracts as contracts_service


@crm_permission_required("view_contract")
def detalhe_contrato(request, contract_id):
    client = CrmApiClient(request)
    lookups = contract_lookups(client)
    file_form = ContractFileForm()
    contrato = None
    arquivos = []

    try:
        contrato = enrich_contract(contracts_service.get_contract(client, contract_id))
        arquivos = contracts_service.list_contract_files(client, contract_id)
    except CrmApiError as exc:
        messages.error(request, crm_error_message_pt(exc))
        return redirect("crm:lista_contratos")

    edit_form = ContractForm(
        initial=contract_initial(contrato),
        lookups=lookups,
        nome_form="Editar Contrato",
    )

    if request.method == "POST" and "edit_contract" in request.POST:
        if not request.user.has_perm("crm.change_contract"):
            messages.error(request, "Você não tem permissão para alterar contratos.")
            return redirect("crm:detalhe_contrato", contract_id=contract_id)
        edit_form = ContractForm(request.POST, lookups=lookups, nome_form="Editar Contrato")
        if edit_form.is_valid():
            try:
                contracts_service.update_contract(
                    client, contract_id, contract_payload(edit_form.cleaned_data),
                )
                messages.success(request, "Contrato atualizado com sucesso!")
                return redirect("crm:detalhe_contrato", contract_id=contract_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    elif request.method == "POST" and "upload_file" in request.POST:
        if not request.user.has_perm("crm.upload_contract_file"):
            messages.error(request, "Você não tem permissão para enviar arquivos.")
            return redirect("crm:detalhe_contrato", contract_id=contract_id)
        file_form = ContractFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            try:
                contracts_service.upload_contract_file(
                    client, contract_id, file_form.cleaned_data["arquivo"],
                )
                messages.success(request, "Arquivo enviado com sucesso!")
                return redirect("crm:detalhe_contrato", contract_id=contract_id)
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))
        else:
            messages.error(request, "Selecione um arquivo válido.")

    return render(
        request,
        "crm/templates_contratos/detalhe_contrato.html",
        {
            "site_title": f"CRM — Contrato {contrato.get('numero') or contract_id}",
            "contrato": contrato,
            "contract_id": contract_id,
            "arquivos": arquivos,
            "edit_form": edit_form,
            "file_form": file_form,
            "current_parent_menu": "crm",
            "current_menu": "crm_contratos",
            "current_submenu": "detalhe",
        },
    )
