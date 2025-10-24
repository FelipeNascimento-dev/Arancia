from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect
from utils.request import RequestClient
from ..forms import Order

API_ENTRADA_PED = "http://192.168.0.214/IntegrationXmlAPI/api/v2/pedidos/entrada/"


def _normalize_item(item: dict, order_number: str) -> dict:
    return {
        "order_number": item.get("order_number") or order_number,
        "simcard_priority": item.get("simcard_priority"),
        "maquinetas_key": item.get("maquinetas_key"),
        "model": item.get("model"),
        "matnr": item.get("matnr"),
        "category": item.get("category"),
        "quantity": item.get("quantity"),
        "ultima_tracking": item.get("ultima_tracking"),
        "volume_number": item.get("volume_number"),
        "volume_name": item.get("volume_name"),
        "volume_state": item.get("volume_state"),
        "logistic_provider_name": item.get("logistic_provider_name"),
        "sales_channel": item.get("sales_channel"),
        "origin_name": item.get("origin_name"),
        "origin_quarter": item.get("origin_quarter"),
        "origin_city": item.get("origin_city"),
        "origin_state_code": item.get("origin_state_code"),
        "end_customer_id": item.get("end_customer_id"),
        "delivery_stage": item.get("delivery_stage"),
        "terminal_logical_numbers": item.get("terminal_logical_numbers"),
        "shipment_order_type": item.get("shipment_order_type"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def visu_pedido(request, order: str):

    form = Order(
        request.POST or None,
        dados={
            "order_number": "19113121917770",
            "simcard_priority": "1-CLARO|2-VIVO",
            "maquinetas_key": "2898704754",
            "model": "XI-POS COMBO NEWLAND SP930",
            "matnr": "605569",
            "category": "Máquinas",
            "quantity": 1,
            "ultima_tracking": "200 - Recebido para picking",
            "volume_number": 1,
            "volume_name": "VOLUME 1",
            "volume_state": "READY_FOR_SHIPPING",
            "logistic_provider_name": "EuEntrego",
            "sales_channel": "SFC-Ctrends Brasilia",
            "origin_name": "C-Trends Sales Force Brasilia",
            "origin_quarter": "Taguatinga Norte (Taguatinga)",
            "origin_city": "Brasília",
            "origin_state_code": "DF",
            "end_customer_id": 1738,
            "delivery_stage": "LASTMILE",
            "terminal_logical_numbers": "01657553",
            "shipment_order_type": "NORMAL",
            "created_at": "2025-08-29T10:00:18.856254",
            "updated_at": "2025-08-29T12:10:09.462959"
        }
    )

    return render(request, "logistica/visu_pedidos.html", {
        "order": order,
        "form": form,
        "botao_texto": getattr(form, "botao_texto", "Enviar"),
        "site_title": "Consultar Pedido Entrada",
        "nome_form": getattr(form, "form_title", "Consultar Pedido Entrada"),
    })
