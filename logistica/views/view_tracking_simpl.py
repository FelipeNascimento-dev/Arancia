import datetime
from typing import Iterable, Tuple, Optional

from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from ..forms import trackingIPForm
from utils.request import RequestClient
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, permission_required
from setup.local_settings import API_URL

#####  TRACKING CODIGOS PARA RETORNO DO PICKING #####

SESSION_PREFIX = "retorno_serials_"


class TrackingOriginalCode:
    def __init__(self, code: str):
        self.original_code = code
        self.show_serial = False
        self.etapa_ativa: Optional[str] = None

        if code == "200":
            self.description = "Recebido para picking"
        elif code == "201":
            self.description = "PCP"
            self.etapa_ativa = "pcp"
        elif code == "202":
            self.description = "Retorno do picking"
            self.etapa_ativa = "retorno_picking"
            self.show_serial = True
        elif code == "203":
            self.description = "Consolidação"
            self.etapa_ativa = "consolidacao"
        elif code == "204":
            self.description = "Expedição"
            self.etapa_ativa = "expedicao"
        elif code == "205":
            self.description = "Troca de custodia"
            self.etapa_ativa = "troca_custodia"
        else:
            self.description = "Etapa desconhecida"


###### FUNÇÕES PARA MODULARIZAÇÃO #####
def _session_key(pedido: Optional[str]) -> str:
    return f"{SESSION_PREFIX}{pedido or 'tmp'}"


def _get_pedido_atual(request: HttpRequest) -> Optional[str]:
    return request.POST.get("pedido") or request.session.get("pedido")


def _get_codigos_from_session(request: HttpRequest, pedido: Optional[str]) -> list[str]:
    key = _session_key(pedido)
    return request.session.get(key, [])


def _ensure_pedido_in_session(request: HttpRequest, pedido: Optional[str]) -> None:
    if pedido:
        request.session["pedido"] = pedido


#####  AÇÕES PARA CODIGOS #####

def _handle_add_codigos(request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form) -> HttpResponse:
    codes = (request.POST.get("codigos") or "").strip().upper()

    if not pedido_atual:
        messages.error(
            request, "Informe o número do pedido antes de inserir seriais.")
    elif not codes:
        messages.info(request, "Digite um serial.")
    else:
        codigos = _get_codigos_from_session(request, pedido_atual)
        if codes not in codigos:
            codigos.append(codes)
            messages.success(request, "Serial inserido.")
        else:
            messages.info(request, "Serial já está na lista.")
        _save_codigos_to_session(request, pedido_atual, codigos)

    _ensure_pedido_in_session(request, pedido_atual)
    initial = _build_initial(form, request, pedido_atual, exclude=("codigo",))
    form = trackingIPForm(
        initial=initial, nome_form=f"IP - {code_info.description}", show_serial=code_info.show_serial)
    codigos = _get_codigos_from_session(request, pedido_atual)
    return _render_pcp(request, form, code_info, codigos)


def _handle_remove_codigos


def _dispatch_codigos_actions_if_any(
        request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form
) -> Optional[HttpResponse]:
    if code_info.original_code != "202":
         return None

    posted_pedido = request.POST.get("pedido")
    if posted_pedido and request.session.get("pedido") != posted_pedido:
        request.session["pedido"] = posted_pedido

    if "add_serials" in request.POST:
         return _handle_add_codigos(request, code_info, _get_pedido_atual(request), form)
    if "remove_serial" in request.POST:
         return _handle_remove_codigos(request, code_info, _get_pedido_atual(request), form)
    if "clear_serials" in request.POST:
         return _handle_clear_codigos(request, code_info, _get_pedido_atual(request), form)

    return None

###### view principal tracking IP #####


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
    def trackingIP(request: HttpRequest, code: str) -> HttpResponse:
    code_info = TrackingOriginalCode(code)
    titulo = f"IP - {code_info.description}"

    pedido_atual = _get_pedido_atual(request)
    codigos = _get_codigos_from_session(
       request, pedido_atual) if code in ["202", "0001"] else []

        if request.method == "POST":
        posted_pedido = (request.POST.get("pedido") or "").strip()
        if posted_pedido:
        _ensure_pedido_in_session(request, posted_pedido)
            pedido_atual = posted_pedido

        form = trackingIPForm(request.POST, nome_form=titulo,
                              show_serial=code_info.show_serial)

                              resp = _dispatch_codigos_actions_if_any(
            request, code_info, pedido_atual, form)
            if resp is not None:
            return resp
