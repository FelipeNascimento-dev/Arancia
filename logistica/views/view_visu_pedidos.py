from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect
from utils.request import RequestClient

API_ENTRADA_PED = "http://192.168.0.214/IntegrationXmlAPI/api/v2/pedidos/entrada/"


def _normalize_item(it: dict, order: str) -> dict:
    return {
        "order_number": it.get("order_number") or it.get("order") or order,
        "simcard_priority": it.get("simcard_priority") or it.get("sim_card_priority") or "-",
        "maquinetas_key": it.get("maquinetas_key") or it.get("key") or "-",
        "model": it.get("model") or it.get("descricao_modelo") or "-",
        "matnr": it.get("matnr") or it.get("sku") or "-",
        "category": it.get("category") or "-",
        "quantity": it.get("quantity") or 1,
        "ultima_tracking": it.get("ultima_tracking") or it.get("last_tracking") or it.get("tracking") or "-",
        "volume_number": it.get("volume_number") or 1,
        "volume_name": it.get("volume_name") or f"VOLUME {it.get('volume_number') or 1}",
        "volume_state": it.get("volume_state") or "-",
        "logistic_provider_name": it.get("logistic_provider_name") or it.get("carrier") or "-",
        "sales_channel": it.get("sales_channel") or it.get("canal_vendas") or "-",
        "origin_name": it.get("origin_name") or "-",
        "origin_quarter": it.get("origin_quarter") or "-",
        "origin_city": it.get("origin_city") or "-",
        "origin_state_code": it.get("origin_state_code") or "-",
        "end_customer_id": it.get("end_customer_id") or "",
        "delivery_stage": it.get("delivery_stage") or "-",
        "terminal_logical_numbers": it.get("terminal_logical_numbers") or it.get("logical_numbers") or "-",
        "shipment_order_type": it.get("shipment_order_type") or it.get("order_type") or "NORMAL",
        "created_at": it.get("created_at") or it.get("data_criacao") or "",
        "updated_at": it.get("updated_at") or "",
    }


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def visu_pedido(request, order: str):
    order = (order or "").strip()
    if not order:
        messages.error(request, "Pedido não informado.")
        return redirect('logistica:entrada_pedido')

    dados = None
    try:
        client = RequestClient(
            url=f"{API_ENTRADA_PED}{order}",
            method="GET",
            headers={"Accept": "application/json"},
        )
        resp = client.send_api_request_no_json(stream=False)

        try:
            data = resp.json()
        except Exception:
            data = []

        if isinstance(data, dict):
            item = data
        elif isinstance(data, list) and data:
            item = data[0]
        else:
            item = {}

        if item:
            dados = _normalize_item(item, order)
        else:
            messages.info(
                request, "Nenhum registro encontrado para o pedido informado.")

    except Exception as e:
        messages.error(request, f"Falha ao consultar pedido {order}: {e}")

    return render(request, "logistica/visu_pedidos.html", {
        "dados": dados,
        "order": order,
        "botao_texto": "Consultar",
        "site_title": "Consultar Pedido Entrada",
        "nome_form": "Consultar Pedido Entrada",
    })
