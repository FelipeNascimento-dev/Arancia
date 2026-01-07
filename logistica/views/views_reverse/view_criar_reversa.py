import re
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import datetime
from ...forms import ReverseCreateForm
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
from .view_enviar_cotacao import send_quotes
from django.contrib.auth.decorators import login_required, permission_required

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def reverse_create(request):
    titulo = 'Reversa de Equipamento'
    result = request.session.get('result', None)
    romaneio_in = request.session.get("romaneio_num", None)

    client_data = request.session.get("selected_client", {})
    client_code = client_data.get("client_code", "").lower()
    client_name = client_data.get("client_name", "")

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

    last_volume = volums[0] if volums else None
    last_kit_serial = None

    if last_volume and last_volume.get("kits"):
        last_kit_serial = last_volume["kits"][0]["serial"]

    for v in volums:
        kits = list(reversed(v.get("kits", [])))
        for idx, k in enumerate(kits, start=1):
            k["kit_number"] = idx
        v["kits"] = kits

    if request.method == "POST" and form.is_valid() and "enviar_evento" in request.POST:
        serial = form.cleaned_data.get("serial")
        if serial:
            serial_norm = serial.strip().upper()

            if not volums:
                volums.append({"volum_number": 1, "kits": []})

            ultimo_volume = volums[-1]

            if len(ultimo_volume["kits"]) >= 24:
                if len(volums) >= 10:
                    messages.error(
                        request, "Limite máximo de 5 volumes atingido!")
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
                volums = result.get("volums", [])
                last_volume = volums[0] if volums else None
                last_kit_serial = None
                if last_volume and last_volume.get("kits"):
                    kits = (last_volume.get("kits", []))
                    last_kit_serial = kits[0]["serial"]
                    last_volume["kits"] = kits
                return redirect("logistica:reverse_create")

    if request.method == "POST" and form.is_valid() and "enviar_cotacao" in request.POST:
        _result = send_quotes(request)
        order = _result.get('order_number')

        if _result and 'detail' not in _result:
            result = _result
            request.session["result"] = result
            request.session.modified = True
            return redirect('logistica:detalhe_pedido', order=order)

    if request.method == "POST" and form.is_valid() and "finalizar_rom" in request.POST:
        from_location_id = int(form.cleaned_data.get("sales_channel"))
        to_location_id = int(form.cleaned_data.get(
            "group_aditional_information"))
        if from_location_id == 0:
            messages.error(request, "Selecione uma PA válida.")
            return redirect("logistica:reverse_create")

        result = request.session.get("result", {})
        volums = result.get("volums", [])

        client_data = request.session.get("selected_client", {})

        items_list = []

        for v in volums:
            volume_number = v.get("volum_number") or v.get("volume_number")

            for kit in v.get("kits", []):
                kit_number = str(kit.get("kit_number"))

                items_list.append({
                    "product_id": 0,
                    "serial": kit["serial"],
                    "extra_info": {
                        "volume_number": volume_number,
                        "kit_number": str(kit_number),
                    }
                })

        if not items_list:
            messages.error(
                request, "Nenhum item encontrado para finalizar o romaneio.")
            return redirect("logistica:reverse_create")

        last_volume = items_list[-1]["extra_info"]["volume_number"]
        last_kit = items_list[-1]["extra_info"]["kit_number"]

        payload = {
            "item": items_list,
            "client_name": client_code,
            "movement_type": "RETURN",
            "from_location_id": from_location_id,
            "to_location_id": to_location_id,
            "order_origin_id": 8,
            "order_number": request.session.get("romaneio_num"),
            "volume_number": last_volume,
            "kit_number": last_kit,
            "created_by": request.user.username,
        }

        movement_extra_info = {}

        if movement_extra_info:
            payload["extra_info"] = movement_extra_info

        client = RequestClient(
            url=f"{STOCK_API_URL}/v1/movements/move-list-items",
            method="POST",
            headers={"Accept": JSON_CT, "Content-Type": JSON_CT},
            request_data=payload
        )

        response = client.send_api_request()

        if isinstance(response, dict) and "detail" in response:
            messages.error(request, response["detail"])
            return redirect("logistica:reverse_create")

        messages.success(request, "Romaneio finalizado com sucesso!")
        return redirect("logistica:consultar_romaneio")

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
        _result = client.send_api_request()

        if not _result:
            messages.warning(
                request, f"API retornou vazio para romaneio {romaneio_in}")
        elif "detail" in _result:
            messages.error(
                request, f"Erro ao cancelar romaneio: {_result['detail']}")
        else:
            messages.success(
                request, f"Romaneio {romaneio_in} cancelado com sucesso!")
            result['status'] = 'CANCELADO'
            request.session["result"] = result
            request.session.modified = True

    volums = result.get("volums", [])
    for v in volums:
        kits = v.get("kits", [])
        kits.sort(key=lambda k: k.get("created_at"),
                  reverse=True)
        v["kits"] = kits

    context = {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "result": result,
        "volums": volums,
        "last_kit_serial": last_kit_serial,
        "client": client_code,
    }
    return render(request, "logistica/templates_reverse/criar_reversa.html", context)


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
            request, f"Serial {serial} removido com sucesso!")

    volums = delete_result.get("volums", [])
    for v in volums:
        kits = v.get("kits", [])
        kits.sort(key=lambda k: k.get("created_at"), reverse=True)
        v["kits"] = kits

    delete_result["volums"] = volums

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

    return render(request, "logistica/templates_reverse/criar_reversa.html", {
        "form": form,
        "botao_texto": "Inserir",
        "site_title": "Reversa",
        "result": request.session.get("result", None),
    })
