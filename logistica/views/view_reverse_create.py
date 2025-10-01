import re
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import datetime
from ..forms import ReverseCreateForm
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from .view_send_quotes import send_quotes

JSON_CT = "application/json"


def reverse_create(request):
    titulo = 'Reversa de Equipamento'
    result = request.session.get('result', None)
    romaneio_in = request.session.get("romaneio_num", None)

    last_rom = request.session.get("current_romaneio")
    if romaneio_in and last_rom != romaneio_in:
        request.session["volums"] = []
        request.session["current_romaneio"] = romaneio_in

    user = request.user
    sales_channel = user.designacao.informacao_adicional.sales_channel
    location_id = 0 if sales_channel == 'all' else user.designacao.informacao_adicional_id

    user_sales_channel = None
    try:
        if (
            request.user.is_authenticated
            and hasattr(request.user, "designacao")
            and request.user.designacao.informacao_adicional
        ):
            user_sales_channel = (
                request.user.designacao.informacao_adicional.sales_channel or ""
            ).strip()
    except Exception:
        user_sales_channel = None

    form = ReverseCreateForm(
        request.POST or None,
        nome_form=titulo,
        user_sales_channel=user_sales_channel,
        romaneio_num=romaneio_in,
    )

    volums = result.get("volums", [])

    for v in volums:
        kits = v.get("kits", [])
        for idx, k in enumerate(kits, start=1):
            k["kit_number"] = idx

    if request.method == "POST" and form.is_valid() and "enviar_evento" in request.POST:
        serial = form.cleaned_data.get("serial")
        if serial:
            serial_norm = serial.strip().upper()

            if not volums:
                volums.append({"volum_number": 1, "kits": []})

            ultimo_volume = volums[-1]

            if len(ultimo_volume["kits"]) >= 10:
                if len(volums) >= 25:
                    messages.error(
                        request, "Limite máximo de 25 volumes atingido!")
                    return redirect("logistica:reverse_create")
                novo_numero = int(ultimo_volume["volum_number"]) + 1
                volums.append({"volum_number": novo_numero, "kits": []})
                ultimo_volume = volums[-1]

            kit_number = len(ultimo_volume["kits"]) + 1

            payload = {
                "serial": serial_norm,
                "volume_number": str(ultimo_volume["volum_number"]),
                "kit_number": str(kit_number),
                "client": "cielo",
                "location_id": location_id,
                "create_by": request.user.username if request.user.is_authenticated else "SYSTEM"
            }

            url = f"{STOCK_API_URL}/v1/romaneios/insert-items/{romaneio_in}"
            client = RequestClient(
                url=url,
                method="POST",
                headers={"Accept": JSON_CT,
                         "Content-Type": "application/json"},
                request_data=payload,
            )
            _result = client.send_api_request()
            if "detail" in _result:
                messages.error(request, _result.get("detail"))
            else:
                result = _result
                request.session["result"] = result
                request.session.modified = True

    if request.method == "POST" and form.is_valid() and "enviar_cotacao" in request.POST:
        _result = send_quotes(request)
        if 'detail' not in _result:
            result = _result

    if request.method == "POST" and "cancelar_rom" in request.POST:
        payload = {
            "status_rom": "CANCELADO",
            "update_by": request.user.username if request.user.is_authenticated else "SYSTEM"
        }
        url = f"{STOCK_API_URL}/v1/romaneios/{romaneio_in}"
        client = RequestClient(url=url, method="PUT",
                               headers={"Accept": JSON_CT,
                                        "Content-Type": JSON_CT},
                               request_data=payload)
        result = client.send_api_request()

        if not result:
            messages.warning(
                request, f"API retornou vazio para romaneio {romaneio_in}")
            result = {"status": "CANCELADO"}
        elif "detail" in result:
            messages.error(
                request, f"Erro ao cancelar romaneio: {result['detail']}")
        else:
            messages.success(
                request, f"Romaneio {romaneio_in} cancelado com sucesso!")
            request.session["result"] = result
            request.session.modified = True

    context = {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "result": result,
        "volums": result.get("volums", []),
    }
    return render(request, "logistica/reverse_create.html", context)


def delete_btn(request, serial):
    romaneio_in = request.session.get("romaneio_num", None)

    if not romaneio_in:
        messages.error(request, "Romaneio não encontrado na sessão.")
        return redirect("logistica:reverse_create")

    url = f"{STOCK_API_URL}/v1/romaneios/{romaneio_in}/?serial={serial}"
    client = RequestClient(
        url=url,
        method="DELETE",
        headers={"Accept": JSON_CT},
    )
    delete_result = client.send_api_request()

    if isinstance(delete_result, dict) and "detail" in delete_result:
        messages.error(
            request, f"Erro ao deletar na API: {delete_result['detail']}")
    else:
        messages.success(
            request, f"Serial {serial} removido com sucesso na API!")

    volums = delete_result.get("volums", [])
    request.session["volums"] = volums
    request.session["result"] = delete_result
    request.session.modified = True

    return redirect("logistica:reverse_create")


def cancel_btn(request, id):
    romaneio_in = request.session.get("romaneio_num", None)

    if request.method != "POST":
        return redirect("logistica:reverse_create")

    if "cancelar_rom" in request.POST:
        payload = {
            "status_rom": "CANCELADO",
            "update_by": request.user.username if request.user.is_authenticated else "SYSTEM"
        }

        url = f"{STOCK_API_URL}/v1/romaneios/{romaneio_in}"

        client = RequestClient(
            url=url,
            method="PUT",
            headers={
                "Accept": JSON_CT,
                "Content-Type": JSON_CT
            },
            request_data=payload,
        )

        result = client.send_api_request()

        if not result:
            messages.warning(request, f"API retornou vazio para romaneio {id}")
            result = {"status": "CANCELADO"}

        if isinstance(result, dict) and "detail" in result:
            messages.error(
                request, f"Erro ao cancelar romaneio: {result['detail']}")
        else:
            messages.success(
                request, f"Romaneio {romaneio_in} cancelado com sucesso!")
            request.session["result"] = result
            request.session.modified = True

        form = ReverseCreateForm(
            nome_form="Reversa de Equipamento",
            user_sales_channel=None,
            romaneio_num=romaneio_in,
        )

    return render(request, "logistica/reverse_create.html", {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "result": request.session.get("result", None),
    })
