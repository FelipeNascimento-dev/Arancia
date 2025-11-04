from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from ..forms import ProductCreateForm
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL
import json

JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def product_create(request):
    titulo = "Consultar Produto"
    choices = []

    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=100"
        res = RequestClient(
            url=url,
            method="GET",
            headers={
                "Accept": JSON_CT
            })
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

    form = ProductCreateForm(nome_form=titulo, client_choices=choices)

    return render(
        request,
        "logistica/product_create.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar Produto",
        },
    )
