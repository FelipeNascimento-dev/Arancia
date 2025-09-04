from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.urls import reverse
from ..forms import OrderDetailForm

CARRY_PEDIDO_KEY = "carry_pedido_next"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def order_detail(request, order: str):

    form = OrderDetailForm(
        request.POST or None,
        dados={
            "order_number": order,
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

    tipo = (form.fields['shipment_order_type'].initial or '').strip().upper()

    botao_texto = "RECEBER DESINSTALAÇÃO" if tipo == "NORMAL" else "RECEBER REVERSA"

    if tipo == "RETURN":
        acao_url = reverse('logistica:consulta_result_ma')
    elif tipo == "NORMAL":
        acao_url = reverse('logistica:pcp', kwargs={'code': '201'})
    elif tipo == "REVERSE":
        acao_url = reverse('logistica:consulta_result_ec')
    else:
        acao_url = request.path

    if request.method == "POST":
        if tipo == "NORMAL":
            request.session["pedido"] = str(order)
            request.session[CARRY_PEDIDO_KEY] = True
            request.session.modified = True
            return redirect('logistica:pcp', code='201')
        elif tipo == "RETURN":
            return redirect('logistica:consulta_result_ma')
        elif tipo == "REVERSE":
            return redirect('logistica:consulta_result_ec')

    produto_campos = [bf(n) for n in form.GRUPO_2 if n in form.fields]
    adicionais_campos = [bf(n) for n in form.GRUPO_3 if n in form.fields]

    return render(request, "logistica/visu_pedidos.html", {
        "order": order,
        "form": form,
        "produto_campos": produto_campos,
        "adicionais_campos": adicionais_campos,
        "botao_texto": botao_texto,
        "acao_url": acao_url,
        "site_title": "Consultar Pedido Entrada",
        "nome_formulario": form.form_title
    })
