# views/view_consulta_etiquetas.py
import re
from typing import List, Tuple, Optional, Dict, Any
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from ..forms import EtiquetasForm
from utils.request import RequestClient
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import API_KEY_INTELIPOST

LABEL_API_URL = "https://api.intelipost.com.br/api/v1/shipment_order/get_label"
SESSION_KEY = "consulta_etiquetas_itens"


def _parse_pedidos(raw: str) -> List[Tuple[str, int]]:
    lines = [l.strip() for l in (raw or "").splitlines() if l.strip()]
    out: List[Tuple[str, int]] = []
    for line in lines:
        parts = re.split(r"[;, \t]+", line)
        pedido = (parts[0] or "").strip()
        if not pedido:
            continue
        vol = 1
        if len(parts) > 1 and str(parts[1]).isdigit():
            vol = int(parts[1])
        out.append((pedido, vol))
    return out


def _get_label_url(pedido: str, volume: int) -> Optional[str]:
    url_request = f'{LABEL_API_URL}/{pedido}/{volume}'
    client = RequestClient(
        url=url_request,
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

    content = data.get("content") or {}
    link = content.get("label_url")
    return link


def _get_items(request: HttpRequest) -> List[List]:
    return list(request.session.get(SESSION_KEY, []))


def _save_items(request: HttpRequest, items: List[List]) -> None:
    request.session[SESSION_KEY] = items
    request.session.modified = True


def _rows_from_items_no_api(items: List[List]) -> List[Dict[str, Any]]:
    return [{"pedido": ped, "volume": int(vol), "url": None} for ped, vol in items]


def _rows_from_items_with_api(items: List[List]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ped, vol in items:
        url = _get_label_url(ped, int(vol))
        rows.append({"pedido": ped, "volume": int(vol), "url": url})
    return rows


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
        })

    items = _get_items(request)
    form = EtiquetasForm(request.POST)

    if "consultar" in request.POST:
        rows = _rows_from_items_with_api(items)
        _save_items(request, [])
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": EtiquetasForm(),
            "botao_texto": "Consultar",
            "rows": rows,
        })

    if form.is_valid():
        labels = []
        novos = items
        if not novos:
            pedido = (form.cleaned_data.get("pedido") or "").strip()
            vol = int(form.cleaned_data.get("qtde_vol") or 1)
            if pedido:
                novos = [(pedido, vol)]

        for ped, vol in novos:
            pair = [ped, int(vol)]
            if pair not in items:
                items.append(pair)
            label = _get_label_url(pedido=ped, volume=vol)
            row = {
                "pedido": ped,
                "volume": vol,
                "url": label
            }
            labels.append(row)

        # print(labels)
        _save_items(request, items)
        rows = _rows_from_items_no_api(items)
    else:
        rows = _rows_from_items_no_api(items)

    return render(request, "logistica/consulta_etiquetas.html", {
        "form": EtiquetasForm(),
        "botao_texto": "Consultar",
        "rows": labels,
    })
