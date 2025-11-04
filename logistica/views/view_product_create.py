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
    titulo = "Consultar Produtos"
    choices = []
    produtos = []

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

    if request.method == "GET" and 'enviar_evento' in request.GET:
        form = ProductCreateForm(
            request.GET, nome_form=titulo, client_choices=choices)
        if form.is_valid():
            client_selected = form.cleaned_data.get("client")
            messages.success(
                request, f"Cliente selecionado: {client_selected}")

            try:
                url = f"{STOCK_API_URL}/v1/products/{client_selected}"
                res = RequestClient(
                    url=url,
                    method="GET",
                    headers={
                        "Accept": JSON_CT
                    })
                produtos_response = res.send_api_request()
                # produtos_response = [
                #     {
                #         "sku": "605081",
                #         "description": "TERMINAL ELETRONICO MOVE 5000 POS COMBO",
                #         "category": "POS",
                #         "client_id": 1,
                #         "created_by": "ARC0000",
                #         "extra_info": {
                #             "measures": {
                #                 "height": 6.7,
                #                 "length": 18.3,
                #                 "price": 150.55,
                #                 "quantity": 1,
                #                 "weight": 0.737,
                #                 "width": 22.4
                #             }
                #         },
                #         "id": 10
                #     },
                #     {
                #         "sku": "605081",
                #         "description": "TERMINAL ELETRONICO MOVE 5000 POS COMBO",
                #         "category": "POS",
                #         "client_id": 1,
                #         "created_by": "ARC0000",
                #         "extra_info": {
                #             "height": 6.7,
                #             "length": 18.3,
                #             "price": 150.55,
                #             "quantity": 1,
                #             "weight": 0.737,
                #             "width": 22.4,
                #             "more": {
                #                        "item1": 1,
                #                 "item2": 2,
                #                 "item3": 3,
                #                 "item4": 4
                #             }
                #         },
                #         "id": 10
                #     },
                #     {
                #         "sku": "605081",
                #         "description": "TERMINAL ELETRONICO MOVE 5000 POS COMBO",
                #         "category": "POS",
                #         "client_id": 1,
                #         "created_by": "ARC0000",
                #         "extra_info": {
                #             "measures": {
                #                 "height": 6.7,
                #                 "length": 18.3,
                #                 "price": 150.55,
                #                 "quantity": 1,
                #                 "weight": 0.737,
                #                 "width": 22.4,
                #                 "more": {
                #                     "item1": 1,
                #                     "item2": 2,
                #                     "item3": 3,
                #                     "more": {
                #                        "item1": 1,
                #                         "item2": 2,
                #                         "item3": 3,
                #                         "item4": 4
                #                     }
                #                 }
                #             }
                #         },
                #         "id": 10
                #     }
                # ]
                if isinstance(produtos_response, str):
                    produtos_response = json.loads(produtos_response)

                if isinstance(produtos_response, list):
                    produtos = produtos_response
                else:
                    produtos = [produtos_response]

                if not produtos:
                    messages.info(
                        request, "Nenhum produto encontrado para este cliente.")

            except Exception as e:
                messages.error(request, f"Erro ao obter produtos: {e}")

        else:
            messages.error(request, "Formulário inválido. Verifique os dados.")
    else:
        form = ProductCreateForm(nome_form=titulo, client_choices=choices)

    return render(
        request,
        "logistica/product_create.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar Produtos",
            "produtos": produtos,
        },
    )
