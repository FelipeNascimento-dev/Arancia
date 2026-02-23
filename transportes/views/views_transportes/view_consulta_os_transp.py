from ...forms import ConsultaOStranspForm
from django.shortcuts import render
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages


def consulta_os_transp(request):
    titulo = "Consulta OS"
    resultado_api = []

    url = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
    )

    resp = client.send_api_request()

    if 'detail' in resp:
        messages.error(request, resp['detail'])

    form = ConsultaOStranspForm(
        request.GET or None,
        payload=resp
    )

    if request.method == "POST" and "enviar_evento" in request.POST:
        params = {}

        tipo_os = request.POST.get("tipo_os")
        numero_os = request.POST.get("numero_os")

        if numero_os:
            if tipo_os == "IN":
                params["IN"] = numero_os
            elif tipo_os == "EX":
                params["EX"] = numero_os

        cliente_id = request.POST.get("client")
        if cliente_id:
            cliente_obj = next(
                (c for c in resp if str(c["id"]) == cliente_id),
                None,
            )

            if cliente_obj:
                params["cliente"] = cliente_obj["nome"]

        status_id = request.POST.get("status")
        if status_id:
            params["status_id"] = status_id

        order_type = request.POST.get("order_type")
        if order_type:
            params["order_type"] = order_type

        params["limit"] = 50
        params["offset"] = 0

        url_lista = f"{TRANSP_API_URL}/service_orders/list"

        lista_request = RequestClient(
            method="get",
            url=url_lista,
            headers={"accept": "application/json"},
            request_data=params,
        )

        resultado_api = lista_request.send_api_request()

        if 'detail' in resultado_api:
            messages.error(request, resultado_api['detail'])
        else:
            messages.success(
                request, f"Consulta realizada com sucesso. {len(resultado_api)} OS encontradas.")

        print(resultado_api)

    return render(
        request,
        "transportes/transportes/consulta_os_transp.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "orders": resultado_api if isinstance(resultado_api, list) else [],
        },
    )
