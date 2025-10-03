from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
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
    request_success = request.session.pop('request_success', None)

    if request.method == "POST":
        result = request.session.get("result")
        form = OrderDetailForm(
            request.POST or None,
            dados=result
        )
        tipo = (
            form.fields['shipment_order_type'].initial or '').strip().upper()
        if tipo == "NORMAL":
            request.session["pedido"] = str(order)
            request.session[CARRY_PEDIDO_KEY] = True
            request.session.modified = True
            return redirect('logistica:pcp', code='201')
        elif tipo == "RETURN":
            return redirect('logistica:button_desn', order=order)
        # elif tipo == "REVERSE":
        #     return redirect('logistica:consulta_result_ec')

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

    def bf(name):
        try:
            return form[name]
        except Exception:
            return None
    produto_campos = [bf(n) for n in form.GRUPO_2 if n in form.fields]
    adicionais_campos = [bf(n) for n in form.GRUPO_3 if n in form.fields]
    historico_tracking = view_order(request, order, 'history')
    request.session["result"] = result

    botao_texto = "RECEBER DESINSTALAÇÃO" if tipo == "RETURN" else "RECEBER REVERSA"

    if request.method == "POST" and "cancelar_pedido" in request.POST:
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

    if request.method == "POST" and "troca_custodia" in request.POST:
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
    })
