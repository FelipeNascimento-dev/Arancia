"""Funções legadas extraídas da view lista_viagens (importadas por outros módulos)."""

from datetime import datetime
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

from setup.local_settings import TRANSP_API_URL
from utils.request import RequestClient


def formatar_data(data_str, com_hora=True):
    if not data_str or data_str == "None":
        return None
    try:
        dt = datetime.fromisoformat(str(data_str).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")
    except Exception:
        return data_str


def buscar_travels_list_resume(travel_id=None, order_number=None):
    params = {"Response": "resume"}
    if travel_id not in [None, ""]:
        params["travel_id"] = travel_id
    elif order_number not in [None, ""]:
        params["IN"] = order_number
    else:
        return {}

    url_travel = (
        f"{TRANSP_API_URL}/v2/order_travel/list/general?"
        f"{urlencode(params, safe=',')}"
    )
    client = RequestClient(
        method="get",
        url=url_travel,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    resp_travel = client.send_api_request()
    if not isinstance(resp_travel, list):
        return {}

    resultado = {}
    for item in resp_travel:
        travel = item.get("travel") or {}
        travel_id_val = travel.get("id")
        if travel_id_val is not None:
            resultado[int(travel_id_val)] = travel
    return resultado


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
@permission_required("transportes.ver_transportes", raise_exception=True)
def buscar_motoristas_travels(request):
    from transportes.utils.atribuir_motorista import validar_gai_id_busca_motorista

    nome = request.GET.get("nome", "").strip()
    carrier_id = request.GET.get("carrier_id", "").strip()
    gai_id = request.GET.get("gai_id", "").strip()

    if len(nome) < 2:
        return JsonResponse({"items": []})

    if gai_id:
        ok, gai_id, detail = validar_gai_id_busca_motorista(request.user, gai_id)
        if not ok:
            return JsonResponse({"items": [], "detail": detail}, status=400)

    if not carrier_id and not gai_id:
        return JsonResponse({"items": []})

    params = {"Nome": nome, "limit": 10}
    if carrier_id:
        params["carrier_id"] = carrier_id
    if gai_id:
        params["gai_id"] = gai_id

    url = f"{TRANSP_API_URL}/Carriers/driver/list?{urlencode(params)}"
    client = RequestClient(
        method="GET",
        url=url,
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    response_moto = client.send_api_request()

    raw_items = []
    if isinstance(response_moto, dict):
        raw_items = response_moto.get("items") or response_moto.get("results") or []
    elif isinstance(response_moto, list):
        raw_items = response_moto

    items = []
    for item in raw_items:
        items.append({
            "uid": item.get("uid") or item.get("id") or "",
            "name": item.get("name") or item.get("nome") or "",
        })
    return JsonResponse({"items": items})
