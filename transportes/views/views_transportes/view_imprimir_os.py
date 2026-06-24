from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from setup.local_settings import TRANSP_API_URL
from transportes.utils.imprimir_os import montar_contexto_impressao_os
from utils.request import RequestClient


def _buscar_viagem_por_id(travel_id):
    params = {
        "travel_id": travel_id,
        "Response": "resume",
    }
    url = f"{TRANSP_API_URL}/v2/order_travel/list/general?{urlencode(params)}"

    client = RequestClient(
        method="get",
        url=url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    response = client.send_api_request()

    if isinstance(response, list) and response:
        return response[0]

    return None


def _buscar_itens_os(order_number):
    if not order_number:
        return []

    url = f"{TRANSP_API_URL}/service_orders/{order_number}"
    client = RequestClient(
        method="get",
        url=url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    response = client.send_api_request()

    if not isinstance(response, dict):
        return []

    return response.get("items") or response.get("results") or []


def _filtrar_itens_por_viagem(itens, travel_id):
    if not itens or travel_id is None:
        return []

    travel_id_str = str(travel_id)
    return [
        item for item in itens
        if str(item.get("travel_order_id")) == travel_id_str
    ]


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def imprimir_os_viagens(request):
    ids_param = request.GET.get("ids", "")
    travel_ids = []

    for raw_id in ids_param.split(","):
        raw_id = raw_id.strip()
        if raw_id.isdigit():
            travel_ids.append(int(raw_id))

    if not travel_ids:
        return HttpResponseBadRequest("Nenhuma viagem selecionada.")

    items_impressao = []
    cache_itens_os = {}

    for travel_id in travel_ids:
        item = _buscar_viagem_por_id(travel_id)
        if not item:
            continue

        service_order = item.get("service_order") or {}
        order_number = service_order.get("order_number")
        travel_id_viagem = (item.get("travel") or {}).get("id")

        if order_number not in cache_itens_os:
            cache_itens_os[order_number] = _buscar_itens_os(order_number)

        os_items = _filtrar_itens_por_viagem(
            cache_itens_os[order_number],
            travel_id_viagem,
        )
        items_impressao.append(montar_contexto_impressao_os(item, os_items=os_items))

    if not items_impressao:
        return HttpResponseBadRequest("Não foi possível carregar as viagens selecionadas.")

    return render(
        request,
        "transportes/transportes/imprimir_os.html",
        {
            "items": items_impressao,
            "vias": ["CLIENTE", "TECNICO"],
        },
    )
