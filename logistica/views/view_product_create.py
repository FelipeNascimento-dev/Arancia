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
    client_map = {}
    cliente_id_para_modal = None

    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=100"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        if isinstance(result, (list, dict)):
            data = result
        elif isinstance(result, (str, bytes)):
            data = json.loads(result)
        elif hasattr(result, "json"):
            data = result.json()
        elif hasattr(result, "text"):
            data = json.loads(result.text)
        else:
            data = []

        if isinstance(data, list) and data:
            choices = [
                (str(i.get("client_code", "")), i.get("client_name", "Sem nome"))
                for i in data
            ]

            client_map = {
                str(i.get("client_code", "")): i.get("id")
                for i in data
                if i.get("client_code")
            }
        else:
            choices = [("", "Nenhum cliente encontrado")]

    except Exception as e:
        messages.error(request, f"Erro ao obter clientes: {e}")
        choices = [("", "Erro ao carregar clientes")]

    if request.method == "POST" and 'criar_produto' in request.POST:
        try:
            sku = request.POST.get("sku")
            description = request.POST.get("description")
            category = request.POST.get("category")
            client_id = request.POST.get("client_id")  # já vem numérico oculto
            extra_info_json = request.POST.get("extra_info_json")

            payload = {
                "sku": sku,
                "description": description,
                "category": category,
                "client_id": int(client_id) if client_id else None,
                "created_by": request.user.username,
                "extra_info": json.loads(extra_info_json or "{}"),
            }

            url = f"{STOCK_API_URL}/v1/products/"
            res = RequestClient(
                url=url,
                method="POST",
                headers={
                    "Content-Type": JSON_CT,
                    "Accept": JSON_CT,
                },
                request_data=payload,
            )
            api_response = res.send_api_request()

            print(payload)

            if isinstance(api_response, (dict, list)):
                messages.success(request, f"Produto {sku} criado com sucesso!")
            else:
                messages.warning(
                    request, f"Resposta inesperada da API: {api_response}"
                )

        except Exception as e:
            messages.error(request, f"Erro ao criar produto: {e}")

        form = ProductCreateForm(nome_form=titulo, client_choices=choices)

    elif request.method == "GET" and 'enviar_evento' in request.GET:
        form = ProductCreateForm(
            request.GET, nome_form=titulo, client_choices=choices)
        if form.is_valid():
            client_selected = form.cleaned_data.get("client")
            client_id_selected = client_map.get(client_selected)

            cliente_id_para_modal = client_id_selected

            messages.success(
                request, f"Cliente selecionado: {client_selected}"
            )

            try:
                url = f"{STOCK_API_URL}/v1/products/{client_selected}"
                res = RequestClient(
                    url=url,
                    method="GET",
                    headers={"Accept": JSON_CT},
                )
                produtos_response = res.send_api_request()

                if isinstance(produtos_response, str):
                    produtos_response = json.loads(produtos_response)

                if isinstance(produtos_response, list):
                    produtos = produtos_response
                elif isinstance(produtos_response, dict):
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
            "cliente_id_para_modal": cliente_id_para_modal,
        },
    )
