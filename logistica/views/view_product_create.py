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
    produtos = []
    client_map = {}
    cliente_id_para_modal = None
    form = None
    choices = []

    # === BUSCA CLIENTES ===
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

    # === CRIAR PRODUTO ===
    if request.method == "POST" and request.POST.get("criar_produto"):
        form = ProductCreateForm(nome_form=titulo, client_choices=choices)
        try:
            sku = request.POST.get("sku")
            description = request.POST.get("description")
            category = request.POST.get("category")
            client_id = request.POST.get("client_id")
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
                headers={"Content-Type": JSON_CT, "Accept": JSON_CT},
                request_data=payload,
            )
            api_response = res.send_api_request()

            if isinstance(api_response, (dict, list)):
                messages.success(request, f"Produto {sku} criado com sucesso!")
            else:
                messages.warning(
                    request, f"Resposta inesperada da API: {api_response}"
                )

        except json.JSONDecodeError:
            messages.error(request, "Formato inválido no campo extra_info.")
        except Exception as e:
            messages.error(request, f"Erro ao criar produto: {e}")

    # === EDITAR PRODUTO ===
    elif request.method == "POST" and request.POST.get("editar_produto"):
        form = ProductCreateForm(nome_form=titulo, client_choices=choices)
        try:
            product_id = request.POST.get("product_id")
            if not product_id:
                messages.error(request, "ID do produto ausente.")
            else:
                payload = {
                    "sku": request.POST.get("sku"),
                    "description": request.POST.get("description"),
                    "category": request.POST.get("category"),
                    "client_id": request.POST.get("client_id"),
                    "created_by": request.user.username,
                    "extra_info": json.loads(request.POST.get("extra_info_json") or "{}"),
                }

                url = f"{STOCK_API_URL}/v1/products/{product_id}"
                res = RequestClient(
                    url=url,
                    method="PUT",
                    headers={"Content-Type": JSON_CT, "Accept": JSON_CT},
                    request_data=payload,
                )
                api_response = res.send_api_request()

                if isinstance(api_response, dict):
                    messages.success(
                        request, f"Produto {payload['sku']} atualizado com sucesso!"
                    )
                else:
                    messages.warning(
                        request, f"Resposta inesperada da API: {api_response}"
                    )

        except json.JSONDecodeError:
            messages.error(request, "Erro no formato de extra_info ao editar.")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar produto: {e}")

    # === CONSULTAR PRODUTOS ===
    elif request.method == "GET" and request.GET.get("enviar_evento"):
        form = ProductCreateForm(
            request.GET, nome_form=titulo, client_choices=choices)
        if form.is_valid():
            client_selected = form.cleaned_data.get("client")
            client_id_selected = client_map.get(client_selected)
            cliente_id_para_modal = client_id_selected

            try:
                url = f"{STOCK_API_URL}/v1/products/{client_selected}"
                res = RequestClient(url=url, method="GET",
                                    headers={"Accept": JSON_CT})
                produtos_response = res.send_api_request()

                if isinstance(produtos_response, str):
                    produtos_response = json.loads(produtos_response)

                if isinstance(produtos_response, list):
                    produtos = produtos_response
                elif isinstance(produtos_response, dict):
                    produtos = [produtos_response]

                for produto in produtos:
                    extra_info = produto.get("extra_info")
                    if isinstance(extra_info, (dict, list)):
                        produto["extra_info_json"] = json.dumps(
                            extra_info, ensure_ascii=False)
                    elif isinstance(extra_info, str):
                        try:
                            produto["extra_info_json"] = json.dumps(
                                json.loads(extra_info), ensure_ascii=False)
                        except Exception:
                            produto["extra_info_json"] = "{}"
                    else:
                        produto["extra_info_json"] = "{}"

                if produtos:
                    messages.success(
                        request, f"Cliente {client_selected} carregado com sucesso.")
                else:
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
