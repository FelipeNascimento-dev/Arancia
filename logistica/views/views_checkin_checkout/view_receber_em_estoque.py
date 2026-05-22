from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ...forms import ReceberEmEstoqueForm
from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient


JSON_CT = "application/json"


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def receber_em_estoque(request):
    titulo = "Receber em Estoque"

    form = ReceberEmEstoqueForm(
        request.POST or None,
        nome_form=titulo
    )

    numero_romaneio = None
    result = None
    itens_romaneio = []
    produtos_choices = []
    client_code = None

    if request.method == "POST":
        numero_romaneio = request.POST.get("numero_romaneio")

        if numero_romaneio:
            numero_romaneio = numero_romaneio.strip()

            try:
                url = f"{STOCK_API_URL}/v2/romaneios/read_for_receive/{numero_romaneio}"

                client = RequestClient(
                    url=url,
                    method="GET",
                    headers={
                        "Accept": JSON_CT,
                        "Content-Type": JSON_CT,
                    },
                )

                result = client.send_api_request()

                if result and "detail" in result:
                    messages.error(request, result.get("detail"))
                    result = None
                    itens_romaneio = []
                else:
                    itens_romaneio = result.get("items", []) if result else []

                    client_code = result.get("client_code") if result else None

                    if client_code:
                        try:
                            url_produtos = f"{STOCK_API_URL}/v1/products/{client_code}"

                            product_client = RequestClient(
                                url=url_produtos,
                                method="GET",
                                headers={
                                    "Accept": JSON_CT,
                                    "Content-Type": JSON_CT,
                                },
                            )

                            produtos_result = product_client.send_api_request()

                            if isinstance(produtos_result, list):
                                produtos_choices = produtos_result

                            elif isinstance(produtos_result, dict):
                                produtos_choices = (
                                    produtos_result.get("items")
                                    or produtos_result.get("results")
                                    or produtos_result.get("products")
                                    or []
                                )

                        except Exception:
                            produtos_choices = []
                            messages.warning(
                                request,
                                "Romaneio encontrado, mas não foi possível carregar a lista de produtos."
                            )

                    messages.success(
                        request,
                        f"Romaneio {numero_romaneio} encontrado com sucesso!"
                    )

            except Exception:
                messages.error(request, "Erro ao consultar o romaneio.")
                result = None
                itens_romaneio = []

        else:
            messages.error(request, "Informe o número do romaneio.")

    return render(
        request,
        'logistica/templates_checkin_checkout/receber_em_estoque.html',
        {
            'form': form,
            'site_title': titulo,
            'botao_texto': 'Consultar Romaneio',
            'romaneio_data': result,
            'itens_romaneio': itens_romaneio,
            'numero_romaneio': numero_romaneio,
            'produtos_choices': produtos_choices,
            'client_code': client_code,
        }
    )


@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
@require_POST
def bipar_serial_recebimento(request):
    try:
        body = json.loads(request.body.decode("utf-8"))

        numero_romaneio = body.get("romaneio")
        serial = body.get("serial")
        product_id = body.get("product_id")

        if not numero_romaneio:
            return JsonResponse({
                "status": "ERROR",
                "message": "Número do romaneio não informado.",
            }, status=400)

        if not serial:
            return JsonResponse({
                "status": "ERROR",
                "message": "Serial não informado.",
            }, status=400)

        numero_romaneio = str(numero_romaneio).strip()
        serial = str(serial).strip().upper()

        if product_id in [None, "", "None", "null", 0, "0"]:
            return JsonResponse({
                "status": "NEED_PRODUCT",
                "serial": serial,
                "message": "Produto não informado para este serial.",
            }, status=400)

        try:
            product_id = int(product_id)
        except ValueError:
            return JsonResponse({
                "status": "NEED_PRODUCT",
                "serial": serial,
                "message": "Produto inválido. Informe um ID numérico.",
            }, status=400)

        payload = {
            "romaneio_number": numero_romaneio,
            "serial": serial,
            "product_id": product_id,
            "updated_by": request.user.username,
        }

        print(payload)

        url = f"{STOCK_API_URL}/v2/romaneios/mark-ck/"

        client = RequestClient(
            url=url,
            method="POST",
            headers={
                "Accept": JSON_CT,
                "Content-Type": JSON_CT,
            },
            request_data=payload,
        )

        result = client.send_api_request()

        api_status = result.get("status") if isinstance(result, dict) else None

        if api_status == "SUCCESS":
            return JsonResponse({
                "status": "SUCCESS",
                "serial": serial,
                "product_id": product_id,
                "message": result.get("message", "Serial recebido com sucesso."),
            })

        return JsonResponse({
            "status": "ERROR",
            "serial": serial,
            "product_id": product_id,
            "message": result.get("message", "Não foi possível receber o serial."),
            "api_response": result,
        }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "ERROR",
            "message": "JSON inválido.",
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "ERROR",
            "message": "Erro ao comunicar com a API de recebimento.",
        }, status=500)
