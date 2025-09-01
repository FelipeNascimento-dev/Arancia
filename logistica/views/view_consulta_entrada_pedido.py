from ..forms import ConsultaEntradaPedForm
from utils.request import RequestClient
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import json

API_ENTRADA_PED = "http://192.168.0.214/IntegrationXmlAPI/api/v2/pedidos/entrada/"


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def entrada_pedido(request):
    form = ConsultaEntradaPedForm(request.POST or None)
    titulo = 'Consultar Pedido Entrada'
    dados = None

    if request.method == "POST":
        if form.is_valid():
            order = (form.cleaned_data.get("order") or "").strip()
            if not order:
                messages.warning(request, "Informe o número do pedido.")
            else:
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
                        items = (
                            data.get("results")
                            or data.get("data")
                            or data.get("items")
                            or [data]
                        )
                    elif isinstance(data, list):
                        items = data
                    else:
                        items = []

                    dados = []
                    for it in items:
                        dados.append({
                            "order_number": it.get("order_number") or it.get("order") or order,
                            "ultima_tracking": it.get("ultima_tracking") or it.get("last_tracking") or it.get("tracking") or "-",
                            "created_at": it.get("created_at") or it.get("data_criacao") or "",
                            "sales_channel": it.get("sales_channel") or it.get("canal_vendas") or "-",
                        })

                    if not dados:
                        messages.info(
                            request, "Nenhum registro encontrado para o pedido informado.")
                except Exception as e:
                    messages.error(request, f"Falha ao consultar pedido: {e}")
        else:
            messages.error(
                request, "Formulário inválido. Verifique os campos.")

    return render(
        request,
        "logistica/consultar_entrada_pedido.html",
        {
            "form": form,
            "dados": dados,
            "botao_texto": "Consultar",
            "site_title": "Consultar Pedido Entrada",
            "nome_form": titulo,
        },
    )
