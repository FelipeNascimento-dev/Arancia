from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect

from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient

from ...forms import PreRecebimentoCheckinForm

JSON_CT = "application/json"
SESSION_ROMANEIO = "pre_rec_romaneio"
SESSION_SERIALS = "pre_rec_serials"


def _normalizar_serial(serial):
    return str(serial or "").strip().upper()


def _location_id_usuario(user):
    gai = getattr(getattr(user, "designacao", None), "informacao_adicional", None)
    if gai and gai.sales_channel == "all":
        return 0
    return getattr(getattr(user, "designacao", None), "informacao_adicional_id", None)


def _montar_payload_pre_receive(serials, numero_romaneio, location_id, username):
    return {
        "item": [
            {
                "serial": serial,
                "product_id": 0,
                "extra_info": {},
            }
            for serial in serials
        ],
        "client_name": "",
        "movement_type": "PRE_RECEIVE",
        "to_location_id": location_id,
        "order_origin_id": 3,
        "order_number": numero_romaneio,
        "created_by": username,
    }


def _enviar_pre_recebimento_lote(serials, numero_romaneio, location_id, username):
    client = RequestClient(
        url=f"{STOCK_API_URL}/v1/movements/move-list-items",
        method="POST",
        headers={
            "Accept": JSON_CT,
            "Content-Type": JSON_CT,
        },
        request_data=_montar_payload_pre_receive(
            serials,
            numero_romaneio,
            location_id,
            username,
        ),
    )

    return client.send_api_request()


def _resposta_lote_sucesso(result):
    if isinstance(result, dict) and result.get("detail"):
        return False, result.get("detail")

    if result is None:
        return False, "Não foi possível registrar o pré-recebimento."

    if isinstance(result, dict) and (
        result.get("id")
        or result.get("items")
        or result.get("success")
        or "success" in str(result).lower()
    ):
        return True, ""

    if isinstance(result, list) and result:
        return True, ""

    return True, ""


def _salvar_romaneio_sessao(request, numero_romaneio):
    numero_romaneio = str(numero_romaneio or "").strip()
    if not numero_romaneio:
        return ""

    anterior = request.session.get(SESSION_ROMANEIO)
    if anterior and anterior != numero_romaneio:
        request.session[SESSION_SERIALS] = []

    request.session[SESSION_ROMANEIO] = numero_romaneio
    request.session.modified = True
    return numero_romaneio


@csrf_protect
@login_required(login_url="logistica:login")
@permission_required("logistica.lastmile_b2c", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def pre_recebimento_checkin(request):
    titulo = "Pré-Recebimento"

    numero_romaneio = (
        request.session.get(SESSION_ROMANEIO)
        or ""
    )
    serials = list(request.session.get(SESSION_SERIALS) or [])

    if request.method == "POST":
        numero_informado = _salvar_romaneio_sessao(
            request,
            request.POST.get("numero_romaneio"),
        )
        if numero_informado:
            numero_romaneio = numero_informado
        serials = list(request.session.get(SESSION_SERIALS) or [])

        if "add_serial" in request.POST:
            serial = _normalizar_serial(request.POST.get("serial"))

            if not numero_romaneio:
                messages.error(request, "Informe o número do romaneio antes de bipar.")
            elif not serial:
                messages.info(request, "Digite um serial.")
            elif serial in serials:
                messages.warning(request, "Serial já inserido.")
            else:
                serials.append(serial)
                request.session[SESSION_SERIALS] = serials
                request.session.modified = True
                messages.success(request, f"Serial {serial} inserido.")

            return redirect("logistica:pre_recebimento_checkin")

        if "remove_serial" in request.POST:
            try:
                idx = int(request.POST.get("remove_serial"))
                if 0 <= idx < len(serials):
                    removido = serials.pop(idx)
                    request.session[SESSION_SERIALS] = serials
                    request.session.modified = True
                    messages.success(request, f"Serial {removido} removido.")
            except (TypeError, ValueError):
                messages.error(request, "Não foi possível remover o serial.")
            return redirect("logistica:pre_recebimento_checkin")

        if "clear_serials" in request.POST:
            request.session[SESSION_SERIALS] = []
            request.session.modified = True
            messages.success(request, "Lista de seriais limpa.")
            return redirect("logistica:pre_recebimento_checkin")

        if "enviar_evento" in request.POST:
            if not numero_romaneio:
                messages.error(request, "Informe o número do romaneio.")
            elif not serials:
                messages.error(request, "Bipe ao menos um serial antes de enviar.")
            else:
                location_id = _location_id_usuario(request.user)
                if location_id is None:
                    messages.error(request, "Usuário sem designação/GAI configurado.")
                else:
                    try:
                        result = _enviar_pre_recebimento_lote(
                            serials,
                            numero_romaneio,
                            location_id,
                            request.user.username,
                        )
                        sucesso, detalhe = _resposta_lote_sucesso(result)

                        if sucesso:
                            messages.success(
                                request,
                                f"Pré-recebimento do romaneio {numero_romaneio} enviado com sucesso.",
                            )
                            request.session.pop(SESSION_ROMANEIO, None)
                            request.session.pop(SESSION_SERIALS, None)
                            request.session.modified = True
                            numero_romaneio = ""
                            serials = []
                        else:
                            messages.error(
                                request,
                                detalhe or "Não foi possível enviar o pré-recebimento.",
                            )
                    except Exception:
                        messages.error(request, "Erro ao comunicar com a API de movimentos.")

            return redirect("logistica:pre_recebimento_checkin")

    form = PreRecebimentoCheckinForm(
        initial={"numero_romaneio": numero_romaneio},
        nome_form=titulo,
    )

    return render(
        request,
        "logistica/templates_checkin_checkout/pre_recebimento.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Enviar pré-recebimento",
            "numero_romaneio": numero_romaneio,
            "serials": serials,
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "pre_recebimento",
        },
    )
