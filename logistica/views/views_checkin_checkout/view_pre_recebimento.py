import json
from datetime import datetime
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient

from ...forms import PreRecebimentoCheckinForm

JSON_CT = "application/json"
SESSION_MODAL = "pre_rec_modal_sucesso"


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


def _nome_cliente_por_code(client_choices, client_code):
    client_code = str(client_code or "").strip()
    for code, name in client_choices:
        if code == client_code:
            return name
    return client_code


def _finalizar_romaneio_pre_receive(numero_romaneio, location_id, username):
    finish_payload = {
        "finished_by": username,
        "finished_at": datetime.utcnow().isoformat() + "Z",
        "movement_type": "PRE_RECEIVE",
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

    print(finish_payload)

    return client.send_api_request()


@csrf_protect
@login_required(login_url="logistica:login")
@permission_required("logistica.lastmile_b2c", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def pre_recebimento_checkin(request):
    titulo = "Pré-Recebimento"
    client_choices = _carregar_clientes()
    modal_sucesso = request.session.get(SESSION_MODAL) or {}

    if request.method == "POST" and "voltar_modal" in request.POST:
        request.session.pop(SESSION_MODAL, None)
        request.session.modified = True
        return redirect("logistica:pre_recebimento_checkin")

    if request.method == "POST" and "iniciar_checkin" in request.POST:
        dados = request.session.get(SESSION_MODAL) or {}
        client_code = dados.get("client_code", "")
        client_name = dados.get("client_name", "")

        if not client_code:
            messages.error(request, "Cliente não encontrado para iniciar o check-in.")
            return redirect("logistica:pre_recebimento_checkin")

        request.session["selected_client"] = {
            "client_code": client_code,
            "client_name": client_name,
        }
        request.session.pop(SESSION_MODAL, None)
        request.session.modified = True

        return redirect(
            f"{reverse('logistica:client_checkin')}?client={quote(client_name)}"
        )

    form = PreRecebimentoCheckinForm(
        request.POST or None,
        nome_form=titulo,
        client_choices=client_choices,
    )

    if request.method == "POST" and "enviar_evento" in request.POST:
        if not form.is_valid():
            messages.warning(request, "Preencha o cliente e o número do romaneio.")
        else:
            client_code = form.cleaned_data["client"]
            numero_romaneio = form.cleaned_data["numero_romaneio"].strip()
            location_id = _location_id_usuario(request.user)

            if location_id is None:
                messages.error(request, "Usuário sem designação/GAI configurado.")
            else:
                try:
                    result = _finalizar_romaneio_pre_receive(
                        numero_romaneio,
                        location_id,
                        request.user.username,
                    )

                    if isinstance(result, dict) and result.get("detail"):
                        messages.error(request, result.get("detail"))
                    else:
                        client_name = _nome_cliente_por_code(client_choices, client_code)
                        request.session[SESSION_MODAL] = {
                            "client_code": client_code,
                            "client_name": client_name,
                            "numero_romaneio": numero_romaneio,
                        }
                        request.session.modified = True
                        modal_sucesso = request.session[SESSION_MODAL]
                        messages.success(
                            request,
                            f"Pré-recebimento do romaneio {numero_romaneio} realizado com sucesso.",
                        )
                        form = PreRecebimentoCheckinForm(
                            nome_form=titulo,
                            client_choices=client_choices,
                        )

                except Exception:
                    messages.error(request, "Erro ao finalizar o romaneio.")

    elif request.method != "POST":
        if not client_choices:
            messages.warning(request, "Não foi possível carregar a lista de clientes.")

    return render(
        request,
        "logistica/templates_checkin_checkout/pre_recebimento.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Enviar pré-recebimento",
            "abrir_modal": bool(modal_sucesso),
            "modal_client_name": modal_sucesso.get("client_name", ""),
            "modal_numero_romaneio": modal_sucesso.get("numero_romaneio", ""),
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "pre_recebimento",
        },
    )
