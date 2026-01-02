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

<<<<<<< HEAD
#####  TRACKING CODIGOS PARA RETORNO DO PICKING #####

TRACKING_URL = API_URL + "/api/order-sumary/add-tracking"
SESSION_PREFIX = "retorno_codigos_"
TRACKING_HEADERS = {"Content-Type": "application/json",
                    "accept": "application/json"}

CARRY_PEDIDO_KEY = "carry_pedido_next"


=======
TRACKING_URL = API_URL + "/api/v2/trackings/send"
SESSION_PREFIX = "retorno_serials_"
TRACKING_HEADERS = {"Content-Type": "application/json",
                    "accept": "application/json"}
CARRY_PEDIDO_KEY = "carry_pedido_next"


# ================= Helpers =================
>>>>>>> release7-MERGE
def _mark_carry_next(request: HttpRequest) -> None:
    request.session[CARRY_PEDIDO_KEY] = True
    request.session.modified = True


def _consume_carry_next(request: HttpRequest) -> bool:
    return request.session.pop(CARRY_PEDIDO_KEY, False)


class TrackingOriginalCode:
    def __init__(self, code: str):
        self.original_code = code
<<<<<<< HEAD
        self.show_codigo = False
        self.etapa_ativa: Optional[str] = None

        if code == "200":
            self.description = "Recebido para picking"
        elif code == "201":
            self.description = "PCP"
            self.etapa_ativa = "pcp"
        elif code == "202":
            self.description = "Retorno do picking"
            self.etapa_ativa = "retorno_picking"
            self.show_codigo = True
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
=======
        self.show_serial = False
        self.etapa_ativa: Optional[str] = None

        etapas = {
            "200": ("Recebido para picking", None),
            "201": ("PCP", "pcp"),
            "202": ("Retorno do picking", "retorno_picking"),
            "203": ("Consolidação", "consolidacao"),
            "204": ("Expedição", "expedicao"),
            "205": ("Troca de custodia", "troca_custodia"),
        }
        self.description, self.etapa_ativa = etapas.get(
            code, ("Etapa desconhecida", None))
        if code == "202":
            self.show_serial = True


>>>>>>> release7-MERGE
def _session_key(pedido: Optional[str]) -> str:
    return f"{SESSION_PREFIX}{pedido or 'tmp'}"


def _get_pedido_atual(request: HttpRequest) -> Optional[str]:
    return request.POST.get("pedido") or request.session.get("pedido")


<<<<<<< HEAD
def _get_codigos_from_session(request: HttpRequest, pedido: Optional[str]) -> list[str]:
    key = _session_key(pedido)
    return request.session.get(key, [])


def _save_codigos_to_session(request: HttpRequest, pedido: Optional[str]) -> list[str]:
    key = _session_key(pedido)
    return request.session.get(key, [])
=======
def _get_serials_from_session(request: HttpRequest, pedido: Optional[str]) -> list[str]:
    return request.session.get(_session_key(pedido), [])


def _save_serials_to_session(request: HttpRequest, pedido: Optional[str], serials: Iterable[str]) -> None:
    request.session[_session_key(pedido)] = list(serials)
    request.session.modified = True
>>>>>>> release7-MERGE


def _ensure_pedido_in_session(request: HttpRequest, pedido: Optional[str]) -> None:
    if pedido:
        request.session["pedido"] = pedido


<<<<<<< HEAD
def _build_initial(form_obj, request: HttpRequest, pedido_atual: Optional[str], exclude=("codigo",)):
=======
def _build_initial(form_obj, request: HttpRequest, pedido_atual: Optional[str], exclude=("serial",)):
>>>>>>> release7-MERGE
    initial = {}
    for name in getattr(form_obj, "fields", {}):
        if name in exclude:
            continue
<<<<<<< HEAD
        val = request.POST.get(name, None)
        if val not in (None, ""):
            initial[name] = val

    if "pedido" in getattr(form_obj, "fields", {}) and not initial.get("pedido"):
        if pedido_atual:
            initial["pedido"] = pedido_atual
        elif request.session.get("pedido"):
            initial["pedido"] = request.session["pedido"]
=======
        val = request.POST.get(name)
        if val:
            initial[name] = val
    if "pedido" in getattr(form_obj, "fields", {}) and not initial.get("pedido"):
        initial["pedido"] = pedido_atual or request.session.get("pedido", "")
>>>>>>> release7-MERGE
    return initial


def _dedup_upper(values: Iterable[str]) -> list[str]:
<<<<<<< HEAD
    seen = set()
    out = []
    for v in values:
        codes = (v or "").strip().upper()
        if codes and codes not in seen:
            seen.add(codes)
            out.append(codes)
    return out

#####  PAYLOAD  #####


def _build_event_payload(code_info: TrackingOriginalCode, codigos_concat: str) -> dict:
    payload = {
        "event_date": datetime.datetime.now().astimezone().isoformat(),
        "original_code": code_info.original_code,
        "original_message": code_info.description,
    }
    if code_info.original_code == "202":
        payload["extra"] = {"codigosNumbers": codigos_concat}
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
    request: HttpRequest, code_info: TrackingOriginalCode, form, codigos: list[str]
) -> Optional[HttpResponse]:
=======
    seen, out = set(), []
    for v in values:
        s = (v or "").strip().upper()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


# ================= Render =================
def _render_pcp(request: HttpRequest, form, code_info: TrackingOriginalCode, serials: list[str]) -> HttpResponse:
    return render(
        request,
        "logistica/templates_fluxo_entrega/pcp.html",
        {
            "form": form,
            "etapa_ativa": code_info.etapa_ativa,
            "botao_texto": "Enviar",
            "serials": serials if code_info.original_code == "202" else [],
            "show_serial": code_info.show_serial,
            "site_title": f"IP - {code_info.description}",
            "chip_map": request.session.get("chip_map", {}),
        },
    )


def _force_pedido(request):
    # pega pedido do POST
    ped = (request.POST.get("pedido") or "").strip()

    # se vier no POST, salva na sessão
    if ped:
        request.session["pedido"] = ped
        request.session.modified = True
        return ped

    # senão pega da sessão
    return request.session.get("pedido", "")


# ================= Serial Actions =================
def _handle_add_serial(request, code_info, pedido_atual, form):
    pedido_atual = _force_pedido(request)   # <<< SEMPRE GARANTE O PEDIDO

    serial = (request.POST.get("serial") or "").strip().upper()
    show_modal = False
    modal_serial = None

    if not serial:
        messages.info(request, "Digite um serial.")
    else:
        serials = _get_serials_from_session(request, pedido_atual)

        if serial not in serials:
            serials.append(serial)
            _save_serials_to_session(request, pedido_atual, serials)

            show_modal = True
            modal_serial = serial

            messages.success(request, "Serial inserido.")
        else:
            messages.info(request, "Serial já está na lista.")

    initial = _build_initial(form, request, pedido_atual, exclude=("serial",))
    initial["pedido"] = pedido_atual

    form = trackingIPForm(
        initial=initial,
        nome_form=f"IP - {code_info.description}",
        show_serial=code_info.show_serial
    )

    return render(request, "logistica/templates_fluxo_entrega/pcp.html", {
        "form": form,
        "etapa_ativa": code_info.etapa_ativa,
        "botao_texto": "Enviar",
        "serials": _get_serials_from_session(request, pedido_atual),
        "show_serial": True,
        "show_modal": show_modal,
        "modal_serial": modal_serial,
    })


def _handle_remove_serial(request, code_info, pedido_atual, form):
    serials = _get_serials_from_session(request, pedido_atual)

    try:
        idx = int(request.POST.get("remove_serial"))
        if 0 <= idx < len(serials):
            removido = serials.pop(idx)
            messages.success(request, f"Removido: {removido}")

            _save_serials_to_session(request, pedido_atual, serials)

            chip_map = request.session.get("chip_map", {})
            chip_map.pop(removido, None)
            request.session["chip_map"] = chip_map
            request.session.modified = True

    except Exception:
        messages.error(request, "Não foi possível remover o serial.")

    form = trackingIPForm(
        initial=_build_initial(form, request, pedido_atual),
        nome_form=f"IP - {code_info.description}",
        show_serial=code_info.show_serial
    )

    return _render_pcp(request, form, code_info, serials)


def _handle_clear_serials(request, code_info, pedido_atual, form):
    _save_serials_to_session(request, pedido_atual, [])
    request.session["chip_map"] = {}
    request.session.modified = True

    messages.success(request, "Lista de seriais limpa.")

    initial = _build_initial(form, request, pedido_atual, exclude=("serial",))
    initial["pedido"] = pedido_atual or request.session.get("pedido", "")

    form = trackingIPForm(
        initial=initial,
        nome_form=f"IP - {code_info.description}",
        show_serial=code_info.show_serial
    )

    return _render_pcp(request, form, code_info, [])


def _dispatch_serial_actions_if_any(request, code_info, pedido_atual, form):
    if code_info.original_code != "202":
        return None
    if "add_serial" in request.POST:
        return _handle_add_serial(request, code_info, _get_pedido_atual(request), form)
    if "remove_serial" in request.POST:
        return _handle_remove_serial(request, code_info, _get_pedido_atual(request), form)
    if "clear_serials" in request.POST:
        return _handle_clear_serials(request, code_info, _get_pedido_atual(request), form)
    return None


# ================= Tracking =================
def _build_request_data(code_info: TrackingOriginalCode, numero_pedido: str, seriais_concat: str, request) -> dict:
    location_id = request.user.designacao.informacao_adicional_id
    payload = {
        "order_number": numero_pedido,
        "volume_number": 1,
        "order_type": "NORMAL",
        "tracking_code": code_info.original_code,
        "created_by": request.user.username,
        "from_location_id": location_id,
    }

    if code_info.original_code == "202" and seriais_concat:
        serials = seriais_concat.split("|")
        chip_map = request.session.get("chip_map", {})

        payload["bar_codes_v2"] = [
            {
                "serial_number": s,
                "product_id": 0,
                "chip_number": chip_map.get(s, "")
            }
            for s in serials
        ]

        print(payload)

    return payload


def _send_tracking(request_data: dict) -> Tuple[str, dict]:
    client = RequestClient(
        url=TRACKING_URL,
        method="POST",
        headers=TRACKING_HEADERS,
        request_data=request_data
    )
    print(request_data)
    resp = client.send_api_request()

    if isinstance(resp, str):
        if "sucesso" in resp.lower() or "success" in resp.lower():
            return "success", {"detail": resp}
        return "error", {"detail": resp}

    if isinstance(resp, dict):
        detail = str(resp.get("detail", "")).lower()
        if "sucesso" in detail or "success" in detail:
            return "success", resp
        return "error", resp

    return "error", {"detail": str(resp)}


def _post_success_redirect(code_info: TrackingOriginalCode, numero_pedido: str) -> HttpResponse:
    redirect_map = {
        "201": ("logistica:pcp_simpl", 202),
        "202": ("logistica:pcp_simpl", 203),
        "203": ("logistica:pcp_simpl", 204),
        "204": ("logistica:consulta_etiquetas", None),
    }
    view_name, next_code = redirect_map.get(
        code_info.original_code,
        ("logistica:pcp_simpl", int(code_info.original_code) +
         1 if code_info.original_code != "205" else "201")
    )
    return redirect(view_name, code=next_code) if next_code else redirect(view_name)


def _process_enviar_evento(request, code_info, form, serials):
>>>>>>> release7-MERGE
    if "enviar_evento" not in request.POST:
        return None

    if not form.is_valid():
        messages.warning(
<<<<<<< HEAD
            request, f"Corrija os erros do formulário: {form.errors.as_text()}")
        return _render_pcp(request, form, code_info, codigos)
=======
            request, f"Corrija os erros do formulário: {form.errors.as_text()}"
        )
        return _render_pcp(request, form, code_info, serials)
>>>>>>> release7-MERGE

    numero_pedido = str(form.cleaned_data.get("pedido"))
    _ensure_pedido_in_session(request, numero_pedido)

<<<<<<< HEAD
    # Seriais somente para 202
    if code_info.original_code == "202":
        codigos = _get_codigos_from_session(request, numero_pedido)
        codigos = _dedup_upper(codigos)
        if not codigos:
            messages.warning(
                request, "Adicione ao menos 1 serial antes de enviar o Retorno do picking.")
            return _render_pcp(request, form, code_info, _get_codigos_from_session(request, numero_pedido))
        codigos_concat = "|".join(codigos)
    else:
        codigos_concat = ""

    event_payload = _build_event_payload(code_info, codigos_concat)
    request_data = _build_request_data(numero_pedido, event_payload)

    try:
        status, resp = _send_tracking(request_data)
        if status == 'success':
            messages.success(
                request, f'A mensagem "{code_info.description}" foi enviada com sucesso!'
            )

            if code_info.original_code == "202":
                _save_codigos_to_session(request, numero_pedido, [])

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

    return _render_pcp(request, form, code_info, codigos)


#####  RENDER  #####


def _render_pcp(request: HttpRequest, form, code_info: TrackingOriginalCode, codigos: list[str]) -> HttpResponse:
    titulo = f"IP - {code_info.description}"
    return render(
        request,
        "logistica/pcp.html",
        {
            "form": form,
            "etapa_ativa": code_info.etapa_ativa,
            "botao_texto": "Enviar",
            "serials": codigos if code_info.original_code == "202" else [],
            "show_serial": code_info.show_serial,
            "site_title": titulo,
        },
    )


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


def _handle_remove_codigos(request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form) -> HttpResponse:
    codigos = _get_codigos_from_session(request, pedido_atual)
    try:
        idx = int(request.POST.get("remove_codigo"))
        if 0 <= len(codigos):
            removido = codigos.pop(idx)
            messages.success(request, f"Removido: {removido}")
            _save_codigos_to_session(request, pedido_atual, codigos)
    except Exception:
        messages.error(request, "Não foi possivel remover o serial.")

    initial = _build_initial(form, request, pedido_atual, exclude=())
    form = trackingIPForm(
        initial=initial, nome_form=f"IP - {code_info.description}", show_serial=code_info.show_serial)
    return _render_pcp(request, form, code_info, codigos)


def _handle_clear_codigos(request: HttpRequest, code_info: TrackingOriginalCode, pedido_atual: Optional[str], form) -> HttpResponse:
    _save_codigos_to_session(request, pedido_atual, [])
    messages.success(request, "Lista de seriais limpa.")

    initial = _build_initial(form, request, pedido_atual, exclude=("codigo",))
    form = trackingIPForm(
        initial=initial, nome_form=f"IP - {code_info.description}", show_serial=code_info.show_serial)
    return _render_pcp(request, form, code_info, [])


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


=======
    if code_info.original_code == "202":
        serials = _dedup_upper(
            _get_serials_from_session(request, numero_pedido))
        if not serials:
            messages.warning(
                request,
                "Adicione ao menos 1 serial antes de enviar o Retorno do picking."
            )
            return _render_pcp(request, form, code_info, serials)
        seriais_concat = "|".join(serials)
    else:
        seriais_concat = ""

    request_data = _build_request_data(
        code_info, numero_pedido, seriais_concat, request
    )

    try:
        status, resp = _send_tracking(request_data)

        resp_text = (
            resp.lower()
            if isinstance(resp, str)
            else " ".join(str(v).lower() for v in resp.values())
        )

        if "sucesso" in resp_text or "success" in resp_text:

            messages.success(
                request,
                resp.get(
                    "detail", f'A mensagem "{code_info.description}" foi enviada com sucesso!')
                if isinstance(resp, dict)
                else str(resp)
            )

            if code_info.original_code == "202":
                _save_serials_to_session(request, numero_pedido, [])
                request.session["chip_map"] = {}
                request.session.modified = True

            _mark_carry_next(request)
            return _post_success_redirect(code_info, numero_pedido)

        messages.error(
            request,
            resp.get(
                "detail", f"Falha ao enviar rastreamento — resposta: {resp}")
            if isinstance(resp, dict)
            else str(resp),
        )
        return _render_pcp(request, form, code_info, serials)

    except Exception as e:
        messages.error(request, f"Erro ao enviar rastreamento: {e}")
        return _render_pcp(request, form, code_info, serials)


# ================= View Principal =================
>>>>>>> release7-MERGE
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def trackingIPV2(request: HttpRequest, code: str) -> HttpResponse:
    code_info = TrackingOriginalCode(code)
    titulo = f"IP - {code_info.description}"

    pedido_atual = _get_pedido_atual(request)
<<<<<<< HEAD
    codigos = _get_codigos_from_session(
        request, pedido_atual) if code in ["202", "0001"] else []

    if request.method == "POST":
        posted_pedido = (request.POST.get("pedido") or "").strip()
    if posted_pedido:
        _ensure_pedido_in_session(request, posted_pedido)
        pedido_atual = posted_pedido
=======
    serials = _get_serials_from_session(
        request, pedido_atual) if code == "202" else []

    if request.method == "POST":
        pedido_atual = _force_pedido(request)

        # ------------------ SALVAR CHIP ------------------
        if request.POST.get("save_chip"):
            serial = request.POST.get("serial").strip().upper()
            chip_number = request.POST.get("chip_number").strip()

            chip_map = request.session.get("chip_map", {})
            chip_map[serial] = chip_number

            request.session["chip_map"] = chip_map
            request.session.modified = True

            messages.success(
                request, f"Chip {chip_number} associado ao serial {serial}."
            )
            return redirect(request.path)
        # --------------------------------------------------
>>>>>>> release7-MERGE

        form = trackingIPForm(request.POST, nome_form=titulo,
                              show_serial=code_info.show_serial)

<<<<<<< HEAD
        resp = _dispatch_codigos_actions_if_any(
            request, code_info, pedido_atual, form)
        if resp is not None:
            return resp

        resp = _process_enviar_evento(request, code_info, form, codigos)
        if resp is not None:
            return resp

        return _render_pcp(request, form, code_info, codigos)
=======
        resp = _dispatch_serial_actions_if_any(
            request, code_info, pedido_atual, form)
        if resp:
            return resp

        resp = _process_enviar_evento(request, code_info, form, serials)
        if resp:
            return resp

        return _render_pcp(request, form, code_info, serials)
>>>>>>> release7-MERGE

    initial = {}
    if _consume_carry_next(request):
        ped = (request.session.get("pedido") or "").strip()
        if ped:
            initial["pedido"] = ped

<<<<<<< HEAD
    form = trackingIPForm(initial=initial,
                          nome_form=titulo,
                          show_serial=code_info.show_serial)

    return _render_pcp(request, form, code_info, codigos)
=======
    form = trackingIPForm(initial=initial, nome_form=titulo,
                          show_serial=code_info.show_serial)
    return _render_pcp(request, form, code_info, serials)
>>>>>>> release7-MERGE
