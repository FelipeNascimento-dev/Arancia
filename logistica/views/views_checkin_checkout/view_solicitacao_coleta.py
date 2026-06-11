import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient

from ...forms import SolicitacaoColetaCheckinForm

JSON_CT = "application/json"


def _location_id_usuario(user):
    gai = getattr(getattr(user, "designacao", None), "informacao_adicional", None)
    if gai and gai.sales_channel == "all":
        return 0
    return getattr(getattr(user, "designacao", None), "informacao_adicional_id", None)


def _carregar_clientes():
    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=1000"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        if isinstance(result, list):
            data = result
        elif isinstance(result, dict):
            data = result.get("items") or result.get("results") or []
        else:
            data = json.loads(result) if result else []

        if not isinstance(data, list):
            return []

        return [
            (str(item.get("client_code", "")), item.get("client_name", "Sem nome"))
            for item in data
            if item.get("client_code")
        ]

    except Exception:
        return []


def _finalizar_romaneio_collection_request(numero_romaneio, location_id, username):
    finish_payload = {
        "finished_by": username,
        "finished_at": datetime.utcnow().isoformat() + "Z",
        "movement_type": "COLLECTION_REQUEST",
        "external_order_number": numero_romaneio,
    }

    finish_url = (
        f"{STOCK_API_URL}/v2/romaneios/finish/{numero_romaneio}?location_id={location_id}"
    )

    client = RequestClient(
        url=finish_url,
        method="POST",
        headers={
            "Accept": JSON_CT,
            "Content-Type": JSON_CT,
        },
        request_data=finish_payload,
    )

    return client.send_api_request()


@csrf_protect
@login_required(login_url="logistica:login")
@permission_required("logistica.lastmile_b2c", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def solicitacao_coleta_checkin(request):
    titulo = "Solicitação de Coleta"
    client_choices = _carregar_clientes()

    form = SolicitacaoColetaCheckinForm(
        request.POST or None,
        nome_form=titulo,
        client_choices=client_choices,
    )

    if request.method == "POST" and "enviar_evento" in request.POST:
        if not form.is_valid():
            messages.warning(request, "Preencha o cliente e o número do romaneio.")
        else:
            numero_romaneio = form.cleaned_data["numero_romaneio"].strip()
            location_id = _location_id_usuario(request.user)

            if location_id is None:
                messages.error(request, "Usuário sem designação/GAI configurado.")
            else:
                try:
                    result = _finalizar_romaneio_collection_request(
                        numero_romaneio,
                        location_id,
                        request.user.username,
                    )

                    if isinstance(result, dict) and result.get("detail"):
                        messages.error(request, result.get("detail"))
                    else:
                        messages.success(
                            request,
                            f"Solicitação de coleta do romaneio {numero_romaneio} enviada com sucesso.",
                        )
                        form = SolicitacaoColetaCheckinForm(
                            nome_form=titulo,
                            client_choices=client_choices,
                        )

                except Exception:
                    messages.error(request, "Erro ao enviar solicitação de coleta.")

    elif request.method != "POST":
        if not client_choices:
            messages.warning(request, "Não foi possível carregar a lista de clientes.")

    return render(
        request,
        "logistica/templates_checkin_checkout/solicitacao_coleta.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Enviar solicitação",
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "solicitacao_coleta",
        },
    )
