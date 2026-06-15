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
    for travel_id in travel_ids:
        item = _buscar_viagem_por_id(travel_id)
        if item:
            items_impressao.append(montar_contexto_impressao_os(item))

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
