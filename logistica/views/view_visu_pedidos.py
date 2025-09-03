from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect
from utils.request import RequestClient
from ..forms import Order

API_ENTRADA_PED = "http://192.168.0.214/IntegrationXmlAPI/api/v2/pedidos/entrada/"


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
            "created_at": "2025-08-29T10:00:18.856254",
            "updated_at": "2025-08-29T12:10:09.462959",
            "shipment_order_type": "NORMAL",
        }
    )

    def bf(name):
        try:
            return form[name]
        except Exception:
            return None

    produto_campos = [bf(n) for n in form.GRUPO_2 if n in form.fields]
    adicionais_campos = [bf(n) for n in form.GRUPO_3 if n in form.fields]

    return render(request, "logistica/visu_pedidos.html", {
        "order": order,
        "form": form,
        "produto_campos": produto_campos,
        "adicionais_campos": adicionais_campos,
        "botao_texto": getattr(form, "botao_texto", "Enviar"),
        "site_title": "Consultar Pedido Entrada",
        "nome_formulario": form.form_title
    })
