# views.py
from typing import List, Dict, Any, Optional
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from ..forms import EtiquetasForm
from utils.request import RequestClient
from setup.local_settings import API_KEY_INTELIPOST

LABEL_API_URL = "https://api.intelipost.com.br/api/v1/shipment_order/get_label"
SESSION_KEY = "consulta_etiquetas_itens"


def _get_items(request: HttpRequest) -> List[Dict[str, Any]]:
    raw = request.session.get(SESSION_KEY, [])
    norm: List[Dict[str, Any]] = []
    for it in raw:
        if isinstance(it, dict):
            norm.append({"pedido": it.get("pedido"), "volume": int(it.get("volume") or 1), "url": it.get("url")})
        elif isinstance(it, (list, tuple)) and it:
            ped = (it[0] or "").strip()
            vol = int(it[1] if len(it) > 1 else 1)
            norm.append({"pedido": ped, "volume": vol, "url": None})
    return norm

def _save_items(request: HttpRequest, items: List[Dict[str, Any]]) -> None:
    request.session[SESSION_KEY] = items
    request.session.modified = True

def _add_item(items: List[Dict[str, Any]], pedido: str, volume: int) -> List[Dict[str, Any]]:
    pedido = (pedido or "").strip()
    if not pedido:
        return items
    volume = int(volume or 1)
    if not any(i["pedido"] == pedido and int(i["volume"]) == volume for i in items):
        items.append({"pedido": pedido, "volume": volume, "url": None})
    return items

def _get_label_url(pedido: str, volume: int) -> Optional[str]:
    client = RequestClient(
        url=f"{LABEL_API_URL}/{pedido}/{volume}",
        method="GET",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": API_KEY_INTELIPOST,
        },
    )
    resp = client.send_api_request_no_json(stream=False)
    if getattr(resp, "status_code", 0) != 200:
        return None
    try:
        data: Dict[str, Any] = resp.json()
    except Exception:
        return None
    content = (data or {}).get("content") or {}
    return content.get("label_url")

def _fill_urls_with_api(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items:
        ped = it["pedido"]
        vol = int(it["volume"])
        url = _get_label_url(ped, vol)
        out.append({"pedido": ped, "volume": vol, "url": url})
    return out

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def consulta_etiquetas(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        _save_items(request, [])
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": EtiquetasForm(),
            "botao_texto": "Consultar",
            "rows": [],
            'site_title': 'Consulta de Etiquetas'
        })

    items = _get_items(request)

    if "enviar_evento" in request.POST:
        if not items:
            messages.info(request, "Nenhum pedido na lista. Digite um pedido e tecle Enter.")
            return render(request, "logistica/consulta_etiquetas.html", {
                "form": EtiquetasForm(),
                "botao_texto": "Consultar",
                "rows": [],
            })

        items = _fill_urls_with_api(items)
        _save_items(request, items)
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": EtiquetasForm(),
            "botao_texto": "Consultar",
            "rows": items,
        })

    pedido = (request.POST.get("pedido") or "").strip()
    try:
        volume = int(request.POST.get("qtde_vol") or 1)
    except ValueError:
        volume = 1

    if pedido:
        items = _add_item(items, pedido, volume)
        _save_items(request, items)

    return render(request, "logistica/consulta_etiquetas.html", {
        "form": EtiquetasForm(),
        "botao_texto": "Consultar",
        "rows": items,
        'site_title': 'Consulta de Etiquetas'
    })
