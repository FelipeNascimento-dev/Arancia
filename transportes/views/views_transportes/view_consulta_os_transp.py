from ...forms import ConsultaOStranspForm
from django.shortcuts import render
from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient
from django.contrib import messages
import math


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

    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    if page < 1:
        page = 1

    limit = 50
    offset = (page - 1) * limit

    total = 0
    total_pages = 1
    has_prev = page > 1
    has_next = False

    qs = request.GET.copy()
    qs.pop("page", None)
    base_qs = qs.urlencode()

    pages = [page]

    if (request.method == "POST" and "enviar_evento" in request.POST) or request.GET.get("page"):

        data = request.POST if request.method == "POST" else request.GET

        params = {}

        tipo_os = data.get("tipo_os")
        numero_os = data.get("numero_os")

        if numero_os:
            if tipo_os == "IN":
                params["IN"] = numero_os
            elif tipo_os == "EX":
                params["EX"] = numero_os

        cliente_id = data.get("client")
        if cliente_id:
            cliente_obj = next(
                (c for c in resp if str(c["id"]) == str(cliente_id)),
                None,
            )
            if cliente_obj:
                params["cliente"] = cliente_obj["nome"]

        status_id = data.get("status")
        if status_id:
            params["status_id"] = status_id

        order_type = data.get("order_type")
        if order_type:
            params["order_type"] = order_type

        params["limit"] = limit
        params["offset"] = offset

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
            resultado_api = []
        else:
            if isinstance(resultado_api, dict):
                items = (
                    resultado_api.get("items")
                    or resultado_api.get("results")
                    or resultado_api.get("data")
                    or []
                )
                total = (
                    resultado_api.get("total")
                    or resultado_api.get("count")
                    or resultado_api.get("total_count")
                    or 0
                )
                resultado_api = items if isinstance(items, list) else []
            else:
                total = 0

            if total:
                total_pages = max(1, math.ceil(total / limit))
                has_next = page < total_pages
            else:
                has_next = len(resultado_api) == limit
                total_pages = page + (1 if has_next else 0)

            start = max(1, page - 2)
            end = min(total_pages, page + 2)
            pages = list(range(start, end + 1))

    return render(
        request,
        "transportes/transportes/consulta_os_transp.html",
        {
            "form": form,
            "site_title": titulo,
            "botao_texto": "Consultar",
            "orders": resultado_api if isinstance(resultado_api, list) else [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_prev": has_prev,
                "has_next": has_next,
                "prev_page": page - 1,
                "next_page": page + 1,
                "pages": pages,
                "base_qs": base_qs,
            },
        },
    )
