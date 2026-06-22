from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from crm.decorators import crm_permission_required
from crm.forms import ContractForm
from crm.helpers.api_display import contract_initial
from crm.views.views_contratos._helpers import contract_lookups
from crm_api.client import CrmApiClient
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.payloads import contract_api_payload
from crm_api.services import contracts as contracts_service


@crm_permission_required("view_contract")
def form_contrato(request, contract_id=None):
    if contract_id and not request.user.has_perm("crm.change_contract"):
        raise PermissionDenied
    if not contract_id and not request.user.has_perm("crm.add_contract"):
        raise PermissionDenied
    client = CrmApiClient(request)
    lookups = contract_lookups(client)
    is_edit = contract_id is not None
    initial = {}

    if is_edit:
        try:
            data = contracts_service.get_contract(client, contract_id)
            initial = contract_initial(data)
            lookups = contract_lookups(client, client_gai_id=initial.get("client_gai_id"))
        except CrmApiError as exc:
            messages.error(request, crm_error_message_pt(exc))
            return redirect("crm:lista_contratos")

    nome_form = "Editar Contrato" if is_edit else "Novo Contrato"
    form = ContractForm(initial=initial, lookups=lookups, nome_form=nome_form)

    if request.method == "POST":
        gai_id = request.POST.get("client_gai_id") or initial.get("client_gai_id")
        lookups = contract_lookups(client, client_gai_id=gai_id)
        form = ContractForm(request.POST, lookups=lookups, nome_form=nome_form)
        if form.is_valid():
            try:
                payload = contract_api_payload(
                    form.cleaned_data,
                    is_create=not is_edit,
                )
                if is_edit:
                    contracts_service.update_contract(client, contract_id, payload)
                    messages.success(request, "Contrato atualizado com sucesso!")
                    return redirect("crm:detalhe_contrato", contract_id=contract_id)
                created = contracts_service.create_contract(client, payload)
                new_id = (created or {}).get("id")
                messages.success(request, "Contrato criado com sucesso!")
                if new_id:
                    return redirect("crm:detalhe_contrato", contract_id=new_id)
                return redirect("crm:lista_contratos")
            except CrmApiError as exc:
                messages.error(request, crm_error_message_pt(exc))

    return render(
        request,
        "crm/templates_contratos/form_contrato.html",
        {
            "site_title": nome_form,
            "form": form,
            "is_edit": is_edit,
            "contract_id": contract_id,
            "botao_texto": "Salvar",
            "current_parent_menu": "crm",
            "current_menu": "crm_contratos",
            "current_submenu": "editar" if is_edit else "novo",
        },
    )
