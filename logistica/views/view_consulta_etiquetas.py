# views/view_consulta_etiquetas.py
import re
from typing import List, Tuple, Optional, Dict, Any
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from ..forms import EtiquetasForm
from utils.request import RequestClient

LABEL_API_URL = "http://192.168.0.214/IntegrationXmlAPI/api/v2/labels/get-link"
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
    client = RequestClient(
        url=LABEL_API_URL,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        request_data={"order_number": pedido, "volume_number": int(volume)},
    )
    resp = client.send_api_request_no_json(stream=False)
    if getattr(resp, "status_code", 0) != 200:
        return None
    try:
        data: Dict[str, Any] = resp.json()
    except Exception:
        return None
    return data.get("url") or data.get("link") or data.get("label_url")

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

def consulta_etiquetas(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        _save_items(request, [])  
        form = EtiquetasForm()
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": form,
            "botao_texto": "Adicionar", 
            "rows": [],  
        })

    items = _get_items(request)
    rows: List[Dict[str, Any]] = []
    form = EtiquetasForm(request.POST)

    if "remove" in request.POST:
        try:
            idx = int(request.POST.get("remove", -1))
            if 0 <= idx < len(items):
                items.pop(idx)
                _save_items(request, items)
        except Exception:
            pass
        rows = _rows_from_items_no_api(items)
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": EtiquetasForm(), "botao_texto": "Adicionar", "rows": rows,
        })
    
    if "clear" in request.POST:
        _save_items(request, [])
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": EtiquetasForm(), "botao_texto": "Adicionar", "rows": [],
        })

    if "consultar" in request.POST:
        rows = _rows_from_items_with_api(items)
        _save_items(request, [])
        return render(request, "logistica/consulta_etiquetas.html", {
            "form": EtiquetasForm(), "botao_texto": "Adicionar", "rows": rows,
        })
    
    if form.is_valid():
        raw = form.cleaned_data.get("pedidos")
        novos = _parse_pedidos(raw) if raw else []
        if not novos:
            pedido = (form.cleaned_data.get("pedido") or "").strip()
            vol = int(form.cleaned_data.get("qtde_vol") or 1)
            if pedido:
                novos = [(pedido, vol)]

        for ped, vol in novos:
            pair = [ped, int(vol)]
            if pair not in items:
                items.append(pair)

        _save_items(request, items)
        rows = _rows_from_items_no_api(items)
    else:
        rows = _rows_from_items_no_api(items)

    return render(request, "logistica/consulta_etiquetas.html", {
        "form": EtiquetasForm(),
        "botao_texto": "Adicionar",
        "rows": rows, 
    })
