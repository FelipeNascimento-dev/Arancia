from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from logistica.views.view_button_desn import button_desn
from setup.local_settings import API_URL
from utils.request import RequestClient
from ..forms import OrderDetailForm
import json

CARRY_PEDIDO_KEY = "carry_pedido_next"
JSON_CT = "application/json"


def view_order(request, order: str, ep_name: str):

    if ep_name == 'history':
        url = f"{API_URL}/api/v2/tracking-history/{order}"
    elif ep_name == 'detail':
        url = f"{API_URL}/api/order-sumary/{order}"
    else:
        return []

    client = RequestClient(
        url=url,
        method="GET",
        headers={"Accept": JSON_CT},
    )
    try:
        result = client.send_api_request()
    except Exception as e:
        if ep_name == 'detail':
            messages.error(request, f"Erro ao consultar pedido: {e}")
        if ep_name == 'history':
            print(f"Erro ao buscar histórico da tracking: {e}")
            return []

        return None

    if 'detail' in result and isinstance(result['detail'], str):
        messages.error(request, f"{result['detail']}")
        return None

    if isinstance(result, list):
        for row in result:
            if isinstance(row, dict):
                if "payload" in row and not isinstance(row["payload"], str):
                    row["payload"] = json.dumps(
                        row["payload"], ensure_ascii=False)
                if "response" in row and not isinstance(row["response"], str):
                    row["response"] = json.dumps(
                        row["response"], ensure_ascii=False)
    elif isinstance(result, dict):
        if "payload" in result and not isinstance(result["payload"], str):
            result["payload"] = json.dumps(
                result["payload"], ensure_ascii=False)
        if "response" in result and not isinstance(result["response"], str):
            result["response"] = json.dumps(
                result["response"], ensure_ascii=False)

    return result


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def order_detail(request, order: str):
    request_success = False

    if request.method == "POST":
        result = request.session.get("result")
        form = OrderDetailForm(
            request.POST or None,
            dados=result
        )

        if "receber_insucesso" in request.POST:
            return redirect('logistica:unsuccessful_insert', order=order)

        tipo = (
            form.fields['shipment_order_type'].initial or '').strip().upper()
        if tipo == "NORMAL":
            try:
                tracking_atual = int(
                    (result.get("ultima_tracking") or "200").split(" ")[0])
                proxima_tracking = min(tracking_atual + 1, 205)
            except Exception:
                proxima_tracking = 201

            request.session["pedido"] = str(order)
            request.session[CARRY_PEDIDO_KEY] = True
            request.session.modified = True

            return redirect("logistica:pcp", code=proxima_tracking)

        elif tipo in ["RETURN", "REVERSE"]:
            try:
                client = RequestClient(
                    url=f"{API_URL}/api/order-sumary/{order}",
                    method="GET",
                    headers={"Accept": "application/json"},
                )
                result_detail = client.send_api_request()
                ultima_tracking = (result_detail.get(
                    "ultima_tracking") or "").strip().upper()
            except Exception:
                ultima_tracking = ""

            import re
            match = re.match(r"(\d+)", ultima_tracking)
            if match:
                code = match.group(1)
                return redirect("logistica:pcp", code=code)

            return redirect("logistica:pcp", code=201)

        elif tipo == "RETURN":
            request_success = button_desn(request, order)
            botao_texto = "RECEBER DESINSTALAÇÃO"

        if "cancelar_pedido" in request.POST:
            url = f"{API_URL}/api/reverse-order/cancel/AR{order}?canceled_by={request.user.username}"
            client = RequestClient(
                url=url,
                method="POST",
                headers={"Accept": JSON_CT,
                         "Content-Type": JSON_CT
                         })
            _result = client.send_api_request()
            if "detail" in _result:
                messages.error(
                    request, f"Erro ao cancelar pedido: {_result['detail']}")
            else:
                messages.success(
                    request, f"Pedido {order} cancelado com sucesso!")
                result['status'] = 'CANCELLED'
                request.session["result"] = result
                request.session.modified = True

        if "troca_custodia" in request.POST:
            user = request.user
            location_id = user.designacao.informacao_adicional_id

            url = f"{API_URL}/api/v2/trackings/send"
            payload = {
                "order_number": result.get("order_number"),
                "volume_number": result.get("volume_number") or 1,
                "order_type": result.get("shipment_order_type"),
                "tracking_code": "205",
                "created_by": request.user.username,
                "to_location_id": location_id,
            }

            client = RequestClient(
                url=url,
                method="POST",
                headers={"Accept": JSON_CT,
                         "Content-Type": JSON_CT},
                request_data=payload)
            _result = client.send_api_request()
            if "detail" in _result:
                messages.error(
                    request, f"Erro ao enviar troca de custódia: {_result['detail']}")
            else:
                messages.success(
                    request, f"Troca de custódia enviada para pedido {payload['order_number']}")

    result = view_order(request, order, 'detail')
    if not result:
        return redirect('logistica:consultar_pedido')
    form = OrderDetailForm(
        request.POST or None,
        dados=result
    )
    tipo = (form.fields['shipment_order_type'].initial or '').strip().upper()
    volume_state = (result.get("volume_state") or "").strip().upper()
    ultima_tracking = (result.get("ultima_tracking") or "").strip().upper()

    mostrar_acoes = (
        tipo == "REVERSE"
        and volume_state != "CANCELLED"
        and ultima_tracking != "205 - TROCA DE CUSTODIA"
    )

    mostrar_receber_insucesso = (
        tipo == "NORMAL"
        and volume_state == "DELIVERY_FAILED"
        and "TROCA DE CUSTODIA" in ultima_tracking
    )

    def bf(name):
        try:
            return form[name]
        except Exception:
            return None
    produto_campos = [bf(n) for n in form.GRUPO_2 if n in form.fields]
    adicionais_campos = [bf(n) for n in form.GRUPO_3 if n in form.fields]
    historico_tracking = view_order(request, order, 'history')
    request.session["result"] = result

    dict_botao_texto = {
        "RETURN": "RECEBER DESINSTALAÇÃO",
        "REVERSE": "RECEBER REVERSA",
        "NORMAL": "PROXIMA TRACKING"
    }

    botao_texto = dict_botao_texto.get(tipo)

    if mostrar_receber_insucesso:
        botao_texto = "RECEBER INSUCESSO"

    return render(request, "logistica/detalhe_pedidos.html", {
        'order': order,
        'request_success': request_success,
        "form": form,
        "produto_campos": produto_campos,
        "adicionais_campos": adicionais_campos,
        "historico_tracking": historico_tracking,
        "botao_texto": botao_texto,
        "site_title": "Detalhe do Pedido",
        "nome_formulario": form.form_title,
        "mostrar_acoes": mostrar_acoes,
        "mostrar_receber_insucesso": mostrar_receber_insucesso,
    })
