from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from setup.local_settings import API_URL
from utils.request import RequestClient
from ..forms import OrderDetailForm

CARRY_PEDIDO_KEY = "carry_pedido_next"
JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def order_detail(request, order: str):

    url = f"{API_URL}/api/order-sumary/{order}"
    client = RequestClient(
        url=url,
        method="GET",
        headers={"Accept": JSON_CT},
    )

    request_success = request.session.pop('request_success', None)
    if request_success:
        print("Request success true")

    try:
        result = client.send_api_request()
    except Exception as e:
        messages.error(request, f"Erro ao consultar pedido: {e}")
        return redirect('logistica:consultar_pedido')

    if 'detail' in result and isinstance(result['detail'], str):
        messages.error(request, f"{result['detail']}")
        return redirect('logistica:consultar_pedido')

    form = OrderDetailForm(
        request.POST or None,
        dados=result
    )

    def bf(name):
        try:
            return form[name]
        except Exception:
            return None

    tipo = (form.fields['shipment_order_type'].initial or '').strip().upper()

    botao_texto = "RECEBER DESINSTALAÇÃO" if tipo == "RETURN" else "RECEBER REVERSA"

    if request.method == "POST":
        if tipo == "NORMAL":
            request.session["pedido"] = str(order)
            request.session[CARRY_PEDIDO_KEY] = True
            request.session.modified = True
            return redirect('logistica:pcp', code='201')
        elif tipo == "RETURN":
            return redirect('logistica:button_desn', order=order)
        elif tipo == "REVERSE":
            return redirect('logistica:consulta_result_ec')

    produto_campos = [bf(n) for n in form.GRUPO_2 if n in form.fields]
    adicionais_campos = [bf(n) for n in form.GRUPO_3 if n in form.fields]

    return render(request, "logistica/detalhe_pedidos.html", {
        'order': order,
        'request_success': request_success,
        "form": form,
        "produto_campos": produto_campos,
        "adicionais_campos": adicionais_campos,
        "botao_texto": botao_texto,
        "site_title": "Detalhe do Pedido",
        "nome_formulario": form.form_title
    })
