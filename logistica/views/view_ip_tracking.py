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

TRACKING_URL = API_URL + "/api/order-sumary/add-tracking"
SESSION_PREFIX = "retorno_serials_"
TRACKING_HEADERS = {"Content-Type": "application/json",
                    "accept": "application/json"}

CARRY_PEDIDO_KEY = "carry_pedido_next"


def _mark_carry_next(request: HttpRequest) -> None:
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True


def _consume_carry_next(request: HttpRequest) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


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


# ---------- Helpers de sessão e formulário ----------

def _session_key(pedido: Optional[str]) -> str:
    return f"{SESSION_PREFIX}{pedido or 'tmp'}"


def _get_pedido_atual(request: HttpRequest) -> Optional[str]:
    return request.POST.get("pedido") or request.session.get("pedido")


def _get_serials_from_session(request: HttpRequest, pedido: Optional[str]) -> list[str]:
    key = _session_key(pedido)
    return request.session.get(key, [])


def _save_serials_to_session(request: HttpRequest, pedido: Optional[str], serials: Iterable[str]) -> None:
    key = _session_key(pedido)
    request.session[key] = list(serials)
    request.session.modified = True


def _ensure_pedido_in_session(request: HttpRequest, pedido: Optional[str]) -> None:
    if pedido:
        request.session["pedido"] = pedido


def _build_initial(form_obj, request: HttpRequest, pedido_atual: Optional[str], exclude=("serial",)):
    initial = {}
    for name in getattr(form_obj, "fields", {}):
        if name in exclude:
            continue
        val = request.POST.get(name, None)
        if val not in (None, ""):
            initial[name] = val

    if "pedido" in getattr(form_obj, "fields", {}) and not initial.get("pedido"):
        if pedido_atual:
            initial["pedido"] = pedido_atual
        elif request.session.get("pedido"):
            initial["pedido"] = request.session["pedido"]
    return initial


def _dedup_upper(values: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for v in values:
        s = (v or "").strip().upper()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


# ---------- Render ----------

def _render_pcp(request: HttpRequest, form, code_info: TrackingOriginalCode, serials: list[str]) -> HttpResponse:
    titulo = f"IP - {code_info.description}"
    return render(
        request,
        "logistica/pcp.html",
        {
            "form": form,
            "etapa_ativa": code_info.etapa_ativa,
            "botao_texto": "Enviar",
            "serials": serials if code_info.original_code == "202" else [],
            "show_serial": code_info.show_serial,
            "site_title": titulo,
        },
    )


# ---------- Ações de seriais (code == '202') ----------

def _handle_add_serial(request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form) -> HttpResponse:
    s = (request.POST.get("serial") or "").strip().upper()

    if not pedido_atual:
        messages.error(
            request, "Informe o número do pedido antes de inserir seriais.")
    elif not s:
        messages.info(request, "Digite um serial.")
    else:
        serials = _get_serials_from_session(request, pedido_atual)
        if s not in serials:
            serials.append(s)
            messages.success(request, "Serial inserido.")
        else:
            messages.info(request, "Serial já está na lista.")
        _save_serials_to_session(request, pedido_atual, serials)

    _ensure_pedido_in_session(request, pedido_atual)
    initial = _build_initial(form, request, pedido_atual, exclude=("serial",))
    form = trackingIPForm(
        initial=initial, nome_form=f"IP - {code_info.description}", show_serial=code_info.show_serial)
    serials = _get_serials_from_session(request, pedido_atual)
    return _render_pcp(request, form, code_info, serials)


def _handle_remove_serial(request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form) -> HttpResponse:
    serials = _get_serials_from_session(request, pedido_atual)
    try:
        idx = int(request.POST.get("remove_serial"))
        if 0 <= idx < len(serials):
            removido = serials.pop(idx)
            messages.success(request, f"Removido: {removido}")
            _save_serials_to_session(request, pedido_atual, serials)
    except Exception:
        messages.error(request, "Não foi possível remover o serial.")

    initial = _build_initial(form, request, pedido_atual, exclude=())
    form = trackingIPForm(
        initial=initial, nome_form=f"IP - {code_info.description}", show_serial=code_info.show_serial)
    return _render_pcp(request, form, code_info, serials)


def _handle_clear_serials(request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form) -> HttpResponse:
    _save_serials_to_session(request, pedido_atual, [])
    messages.success(request, "Lista de seriais limpa.")

    initial = _build_initial(form, request, pedido_atual, exclude=("serial",))
    form = trackingIPForm(
        initial=initial, nome_form=f"IP - {code_info.description}", show_serial=code_info.show_serial)
    return _render_pcp(request, form, code_info, [])


def _dispatch_serial_actions_if_any(
    request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form
) -> Optional[HttpResponse]:
    if code_info.original_code != "202":
        return None

    # Se mudou o pedido, zera a key e recarrega lista
    posted_pedido = request.POST.get("pedido")
    if posted_pedido and request.session.get("pedido") != posted_pedido:
        request.session["pedido"] = posted_pedido

    if "add_serial" in request.POST:
        return _handle_add_serial(request, code_info, _get_pedido_atual(request), form)

    if "remove_serial" in request.POST:
        return _handle_remove_serial(request, code_info, _get_pedido_atual(request), form)

    if "clear_serials" in request.POST:
        return _handle_clear_serials(request, code_info, _get_pedido_atual(request), form)

    return None


# ---------- Payloads e envio ----------

def _build_event_payload(code_info: TrackingOriginalCode, seriais_concat: str) -> dict:
    payload = {
        "event_date": datetime.datetime.now().astimezone().isoformat(),
        "original_code": code_info.original_code,
        "original_message": code_info.description,
    }
    if code_info.original_code == "202":
        payload["extra"] = {"serialNumbers": seriais_concat}
    return payload


def _build_request_data(numero_pedido: str, event_payload: dict) -> dict:
    return {
        "shipper": "C-Trends",
        "shipper_federal_tax_id": "20056828000179",
        "order_number": numero_pedido,
        "volume_number": 1,
        "events": [event_payload],
    }


def _send_tracking(request_data: dict) -> Tuple[bool, int, Optional[object]]:
    client = RequestClient(url=TRACKING_URL, method="POST",
                           headers=TRACKING_HEADERS, request_data=request_data)
    resp = client.send_api_request()

    status = resp['status'] if "status" in resp else 'error'
    # detail = getattr(resp, "detail", 'no detail')
    return (status, resp)


def _post_success_redirect(code_info: TrackingOriginalCode, numero_pedido: str) -> HttpResponse:
    if code_info.original_code == "201":
        return redirect("logistica:reserva_equip", tp_reg=84)
    elif code_info.original_code == "203":
        return redirect("logistica:saida_campo", tp_reg=1)
    elif code_info.original_code == "204":
        return redirect("logistica:pcp", code=201)
    elif code_info.original_code == "205":
        return redirect("logistica:pcp", code=205)
    else:
        prox = int(code_info.original_code) + 1
        return redirect("logistica:pcp", code=prox)


def _process_enviar_evento(
    request: HttpRequest, code_info: TrackingOriginalCode, form, serials: list[str]
) -> Optional[HttpResponse]:
    if "enviar_evento" not in request.POST:
        return None

    if not form.is_valid():
        messages.warning(
            request, f"Corrija os erros do formulário: {form.errors.as_text()}")
        return _render_pcp(request, form, code_info, serials)

    numero_pedido = str(form.cleaned_data.get("pedido"))
    _ensure_pedido_in_session(request, numero_pedido)

    # Seriais somente para 202
    if code_info.original_code == "202":
        serials = _get_serials_from_session(request, numero_pedido)
        serials = _dedup_upper(serials)
        if not serials:
            messages.warning(
                request, "Adicione ao menos 1 serial antes de enviar o Retorno do picking.")
            return _render_pcp(request, form, code_info, _get_serials_from_session(request, numero_pedido))
        seriais_concat = "|".join(serials)
    else:
        seriais_concat = ""

    event_payload = _build_event_payload(code_info, seriais_concat)
    request_data = _build_request_data(numero_pedido, event_payload)

    try:
        status, resp = _send_tracking(request_data)
        if status == 'success':
            messages.success(
                request, f'A mensagem "{code_info.description}" foi enviada com sucesso!'
            )

            if code_info.original_code == "202":
                _save_serials_to_session(request, numero_pedido, [])

            _ensure_pedido_in_session(request, numero_pedido)
            _mark_carry_next(request)

            return _post_success_redirect(code_info, numero_pedido)
        elif 'detail' in resp:
            messages.error(request, resp['detail'])
        else:
            messages.warning(
                request, f"Falha ao enviar rastreamento (status {status}).")
    except Exception as e:
        messages.error(request, f"{e}")

    return _render_pcp(request, form, code_info, serials)


# ---------- View principal ----------
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def trackingIP(request: HttpRequest, code: str) -> HttpResponse:
    code_info = TrackingOriginalCode(code)
    titulo = f"IP - {code_info.description}"

    pedido_atual = _get_pedido_atual(request)
    serials = _get_serials_from_session(
        request, pedido_atual) if code in ["202", ""] else []

    if request.method == "POST":
        posted_pedido = (request.POST.get("pedido") or "").strip()
        if posted_pedido:
            _ensure_pedido_in_session(request, posted_pedido)
            pedido_atual = posted_pedido

        form = trackingIPForm(request.POST, nome_form=titulo,
                              show_serial=code_info.show_serial)

        resp = _dispatch_serial_actions_if_any(
            request, code_info, pedido_atual, form)
        if resp is not None:
            return resp

        resp = _process_enviar_evento(request, code_info, form, serials)
        if resp is not None:
            return resp

        return _render_pcp(request, form, code_info, serials)

    initial = {}
    if _consume_carry_next(request):
        ped = (request.session.get("pedido") or "").strip()
        if ped:
            initial["pedido"] = ped

    form = trackingIPForm(initial=initial,
                          nome_form=titulo,
                          show_serial=code_info.show_serial)

    return _render_pcp(request, form, code_info, serials)
