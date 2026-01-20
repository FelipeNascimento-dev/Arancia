from typing import List, Dict, Any, Optional
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from ...forms import EtiquetasForm
from utils.request import RequestClient
from setup.local_settings import API_KEY_INTELIPOST, API_URL

SESSION_KEY = "consulta_etiquetas_itens"


def _get_items(request: HttpRequest) -> List[Dict[str, Any]]:
    raw = request.session.get(SESSION_KEY, [])
    norm: List[Dict[str, Any]] = []
    for it in raw:
        if isinstance(it, dict):
            norm.append({"pedido": it.get("pedido"), "volume": int(
                it.get("volume") or 1), "url": it.get("url")})
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


def _get_label_url(request, pedido: str, volume: int) -> Optional[str]:
    simplified = "true" if request.user.has_perm(
        "logistica.inst_simplified") else "false"
    url = (
        f"{API_URL}/api/order-sumary/get-label/"
        f"{pedido}/{volume}?simplificated={simplified}"
    )
    client = RequestClient(
        url=url,
        method="GET",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": API_KEY_INTELIPOST,
        },
    )
    resp = client.send_api_request_no_json(stream=False)
    if getattr(resp, "status_code", 0) == 500:
        return None
    try:
        data: Dict[str, Any] = resp.json()
    except Exception:
        return None
    if 'detail' in data:
        return data

    content = (data or {}).get("content") or {}
    return content.get("label_url")


def _fill_urls_with_api(items: List[Dict[str, Any]], request: Optional[HttpRequest] = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items:
        ped = it["pedido"]
        vol = int(it["volume"])
        try:
            url = _get_label_url(request, ped, vol)

            if not url:
                out.append({"pedido": ped, "volume": vol, "url": {
                           "detail": "Erro interno do servidor"}})
            elif 'detail' in url:
                out.append({"pedido": ped, "volume": vol,
                           "url": url})
            else:
                out.append({"pedido": ped, "volume": vol, "url": url})
        except Exception as e:
            if request:
                messages.error(
                    request, f"Erro na consulta do pedido {ped}: {e}")
            out.append({"pedido": ped, "volume": vol, "url": "INSUCESSO"})
    return out


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def consulta_etiquetas(request: HttpRequest) -> HttpResponse:
    pedido_sessao = (request.session.get("pedido") or "").strip()

    if request.method == "GET":
        if pedido_sessao:
            items = _add_item([], pedido_sessao, 1)
            _save_items(request, items)
            form = EtiquetasForm(initial={"pedido": pedido_sessao})
            return render(request, "logistica/templates_lastmile_consultas/consulta_etiquetas.html", {
                "form": form,
                "botao_texto": "Consultar",
                "rows": items,
                'site_title': 'Consulta de Etiquetas',
                "etapa_ativa": 'consulta_etiquetas',
                "current_parent_menu": "logistica",
                "current_menu": "lastmile",
                "current_submenu": "consultas",
                "current_subsubmenu": "consulta_etiquetas"
            })

        _save_items(request, [])
        return render(request, "logistica/templates_lastmile_consultas/consulta_etiquetas.html", {
            "form": EtiquetasForm(),
            "botao_texto": "Consultar",
            "rows": [],
            'site_title': 'Consulta de Etiquetas',
            "etapa_ativa": 'consulta_etiquetas',
            "current_parent_menu": "logistica",
            "current_menu": "lastmile",
            "current_submenu": "consultas",
            "current_subsubmenu": "consulta_etiquetas"
        })

    items = _get_items(request)

    if "enviar_evento" in request.POST:
        if not items:
            messages.info(
                request, "Nenhum pedido na lista. Digite um pedido e tecle Enter.")
            return render(request, "logistica/templates_lastmile_consultas/consulta_etiquetas.html", {
                "form": EtiquetasForm(),
                "botao_texto": "Consultar",
                "rows": [],
                "etapa_ativa": 'consulta_etiquetas',
                "current_parent_menu": "logistica",
                "current_menu": "lastmile",
                "current_submenu": "consultas",
                "current_subsubmenu": "consulta_etiquetas"
            })

        items = _fill_urls_with_api(items, request)
        _save_items(request, items)
        return render(request, "logistica/templates_lastmile_consultas/consulta_etiquetas.html", {
            "form": EtiquetasForm(),
            "botao_texto": "Consultar",
            "rows": items,
            "etapa_ativa": 'consulta_etiquetas',
            "current_parent_menu": "logistica",
            "current_menu": "lastmile",
            "current_submenu": "consultas",
            "current_subsubmenu": "consulta_etiquetas"
        })

    pedido = (request.POST.get("pedido") or "").strip()
    try:
        volume = int(request.POST.get("qtde_vol") or 1)
    except ValueError:
        volume = 1

    if pedido:
        items = _add_item(items, pedido, volume)
        _save_items(request, items)

    return render(request, "logistica/templates_lastmile_consultas/consulta_etiquetas.html", {
        "form": EtiquetasForm(),
        "botao_texto": "Consultar",
        "rows": items,
        'site_title': 'Consulta de Etiquetas',
        "etapa_ativa": 'consulta_etiquetas',
        "current_parent_menu": "logistica",
        "current_menu": "lastmile",
        "current_submenu": "consultas",
        "current_subsubmenu": "consulta_etiquetas"
    })
