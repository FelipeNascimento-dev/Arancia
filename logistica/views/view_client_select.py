from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from ..forms import ClientSelectForm
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
import json

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def client_select(request):
    titulo = "Seleção de Cliente"
    choices = []

    if request.method == "POST":
        form = ClientSelectForm(request.POST, nome_form=titulo)

        # client_name = form.cleaned_data
        client = request.POST.get("client", None)
        order = request.POST.get("order", None)

        request.session["order"] = order

        if client:
            request.session["selected_client"] = {"client_name": client}

            if client.lower() == "cielo":
                if not order or order.strip() == "":
                    messages.error(
                        request,
                        "O campo 'Order' é obrigatório para o cliente Cielo.",
                    )
                    return redirect("logistica:client_select")
                return redirect("logistica:detalhe_pedido", order=order)
            else:
                return redirect("logistica:client_checkin")
        else:
            messages.error(request, "Falha ao selecionar o cliente.")

    request.session.pop("order", None)

    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=1000"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        try:
            if isinstance(result, (dict, list)):
                data = result
            elif isinstance(result, (str, bytes)):
                data = json.loads(result)
            elif hasattr(result, "json"):
                data = result.json()
            elif hasattr(result, "text"):
                data = json.loads(result.text)
            else:
                data = []
        except Exception:
            data = []

        if isinstance(data, list) and len(data) > 0:
            choices = [
                (str(i.get("client_code", "")), i.get("client_name", "Sem nome"))
                for i in data
            ]
        else:
            choices = [("", "Nenhum cliente encontrado")]

    except Exception as e:
        messages.error(request, f"Erro ao obter clientes: {e}")
        choices = [("", "Erro ao carregar clientes")]

    form = ClientSelectForm(nome_form=titulo, client_choices=choices)

    return render(
        request,
        "logistica/client_select.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Selecionar Cliente",
        },
    )
