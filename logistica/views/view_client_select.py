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

    # ======== CRIA NOVO CLIENTE ========
    if request.method == "POST" and request.POST.get("new_client") == "1":
        client_code = request.POST.get("client_code")
        client_name = request.POST.get("client_name")
        created_by = request.user.username
        extra_info_raw = request.POST.get("extra_info", "{}")

        try:
            extra_info = json.loads(
                extra_info_raw) if extra_info_raw.strip() else {}
        except Exception:
            extra_info = {}

        payload = {
            "client_code": client_code,
            "client_name": client_name,
            "created_by": created_by,
            "extra_info": extra_info,
        }

        url = f"{STOCK_API_URL}/v1/clients/"
        headers = {"Content-Type": JSON_CT, "Accept": JSON_CT}

        try:
            res = RequestClient(
                url=url,
                method="POST",
                headers=headers,
                request_data=payload,
            )
            result = res.send_api_request()

            if isinstance(result, dict) and result.get("client_code"):
                messages.success(
                    request, f"Cliente '{client_name}' criado com sucesso!"
                )
            else:
                messages.error(request, f"Erro ao criar cliente: {result}")
        except Exception as e:
            messages.error(request, f"Falha ao criar cliente: {e}")

        return redirect("logistica:client_select")

    # ======== SELECIONA CLIENTE EXISTENTE ========
    if request.method == "POST":
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

    # ======== LISTA CLIENTES EXISTENTES ========
    request.session.pop("order", None)

    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=100"
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
