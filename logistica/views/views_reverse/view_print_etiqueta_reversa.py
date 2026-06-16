from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from logistica.utils.etiqueta_reversa import (
    montar_etiqueta_reversa,
    montar_etiquetas_todos_volumes,
)
from setup.local_settings import STOCK_API_URL
from utils.request import RequestClient

JSON_CT = "application/json"


def _location_id_from_user(user) -> int:
    sales_channel = user.designacao.informacao_adicional.sales_channel
    if sales_channel == "all":
        return 0
    return user.designacao.informacao_adicional_id


def _buscar_romaneio(numero_romaneio: str, location_id: int):
    url = f"{STOCK_API_URL}/v1/romaneios/{numero_romaneio}?location_id={location_id}"
    client = RequestClient(
        url=url,
        method="GET",
        headers={"Accept": JSON_CT},
    )
    return client.send_api_request()


@login_required(login_url="logistica:login")
@permission_required("logistica.acesso_arancia", raise_exception=True)
def print_etiqueta_reversa(request, romaneio, volume):
    location_id = _location_id_from_user(request.user)

    try:
        romaneio_data = _buscar_romaneio(romaneio, location_id)
    except Exception as exc:
        return HttpResponseBadRequest(f"Erro ao consultar romaneio: {exc}")

    if not isinstance(romaneio_data, dict) or romaneio_data.get("detail"):
        detail = (romaneio_data or {}).get("detail", "Romaneio não encontrado.")
        return HttpResponseBadRequest(detail)

    imprimir_todos = request.GET.get("todos") == "1"

    if imprimir_todos:
        etiquetas = montar_etiquetas_todos_volumes(
            romaneio_data,
            romaneio_fallback=romaneio,
        )
        if not etiquetas:
            return HttpResponseBadRequest("Nenhum volume encontrado para impressão.")
    else:
        etiqueta = montar_etiqueta_reversa(
            romaneio_data,
            volume,
            romaneio_fallback=romaneio,
        )
        if not etiqueta:
            return HttpResponseBadRequest(f"Volume {volume} não encontrado no romaneio.")
        etiquetas = [etiqueta]

    return render(
        request,
        "logistica/templates_reverse/print_etiqueta_reversa.html",
        {
            "etiquetas": etiquetas,
            "auto_print": request.GET.get("auto") == "1",
        },
    )
