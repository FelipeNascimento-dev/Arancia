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

TRACKING_URL = API_URL + "/api/v2/trackings/send"
SESSION_PREFIX = "retorno_serials_"
TRACKING_HEADERS = {"Content-Type": "application/json",
                    "accept": "application/json"}
CARRY_PEDIDO_KEY = "carry_pedido_next"

KIT_DATA = {
    "KIT123": [
        {"serial": "ABC123", "chip": "999"},
        {"serial": "DEF456", "chip": "888"},
    ],
    "KIT999": [
        {"serial": "XYZ111", "chip": "777"},
    ],
    "KIT777": [
        {"serial": "EFG0102", "chip": "714"},
    ],
}


# ================= Helpers =================
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


def _session_key(pedido: Optional[str]) -> str:
    return f"{SESSION_PREFIX}{pedido or 'tmp'}"


def _get_pedido_atual(request: HttpRequest) -> Optional[str]:
    return request.POST.get("pedido") or request.session.get("pedido")


def _get_serials_from_session(request: HttpRequest, pedido: Optional[str]) -> list[str]:
    return request.session.get(_session_key(pedido), [])


def _save_serials_to_session(request: HttpRequest, pedido: Optional[str], serials: Iterable[str]) -> None:
    request.session[_session_key(pedido)] = list(serials)
    request.session.modified = True


def _ensure_pedido_in_session(request: HttpRequest, pedido: Optional[str]) -> None:
    if pedido:
        request.session["pedido"] = pedido


def _build_initial(form_obj, request: HttpRequest, pedido_atual: Optional[str], exclude=("serial",)):
    initial = {}
    for name in getattr(form_obj, "fields", {}):
        if name in exclude:
            continue
        val = request.POST.get(name)
        if val:
            initial[name] = val
    if "pedido" in getattr(form_obj, "fields", {}) and not initial.get("pedido"):
        initial["pedido"] = pedido_atual or request.session.get("pedido", "")
    return initial


def _dedup_upper(values: Iterable[str]) -> list[str]:
    seen, out = set(), []
    for v in values:
        s = (v or "").strip().upper()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


# ================= Render =================
def _render_pcp(request: HttpRequest, form, code_info: TrackingOriginalCode, serials: list[str], busca_kit=None,
                itens_kit=None) -> HttpResponse:
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
            "busca_kit": busca_kit,
            "itens_kit": itens_kit,
        },
    )


def _force_pedido(request):
    ped = (request.POST.get("pedido") or "").strip()

    if ped:
        request.session["pedido"] = ped
        request.session.modified = True
        return ped

    return request.session.get("pedido", "")


# ================= Serial Actions =================
def _handle_add_serial(request, code_info, pedido_atual, form):
    pedido_atual = _force_pedido(request)  # garante pedido

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
        show_serial=code_info.show_serial,
        modo_insercao=request.session.get("retorno_picking_modo"),
    )

    return render(
        request,
        "logistica/templates_fluxo_entrega/pcp.html",
        {
            "form": form,
            "etapa_ativa": code_info.etapa_ativa,
            "botao_texto": "Enviar",
            "serials": _get_serials_from_session(request, pedido_atual),
            "show_serial": True,
            "show_modal": show_modal,
            "modal_serial": modal_serial,
        },
    )


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
        show_serial=code_info.show_serial,
        modo_insercao=request.session.get("retorno_picking_modo"),
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
        show_serial=code_info.show_serial,
        modo_insercao=request.session.get("retorno_picking_modo"),
    )

    return _render_pcp(request, form, code_info, [])


def _dispatch_serial_actions_if_any(request, code_info, pedido_atual, form):
    if code_info.original_code != "202":
        return None

    modo = request.session.get("retorno_picking_modo")

    if not modo:
        messages.warning(request, "Escolha primeiro o modo de inserção.")
        return redirect(request.path)

    if "remove_serial" in request.POST:
        return _handle_remove_serial(request, code_info, pedido_atual, form)

    if "clear_serials" in request.POST:
        return _handle_clear_serials(request, code_info, pedido_atual, form)

    if "add_serial" in request.POST:
        return _handle_add_serial(request, code_info, pedido_atual, form)

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
                "serial": s,
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
    if "enviar_evento" not in request.POST:
        return None

    if not form.is_valid():
        messages.warning(
            request, f"Corrija os erros do formulário: {form.errors.as_text()}"
        )
        return _render_pcp(request, form, code_info, serials)

    numero_pedido = str(form.cleaned_data.get("pedido"))
    _ensure_pedido_in_session(request, numero_pedido)

    if code_info.original_code == "202":
        modo = request.session.get("retorno_picking_modo")
        serials = _get_serials_from_session(request, numero_pedido)

        if modo == "kit" and not serials:
            messages.warning(request, "Adicione ao menos um kit.")
            return _render_pcp(request, form, code_info, serials)

        if modo == "bipagem" and not serials:
            messages.warning(request, "Adicione ao menos um serial.")
            return _render_pcp(request, form, code_info, serials)

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
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('logistica.lastmile_b2c', raise_exception=True)
def trackingIPV2(request: HttpRequest, code: str) -> HttpResponse:
    code_info = TrackingOriginalCode(code)
    titulo = f"IP - {code_info.description}"

    pedido_atual = _get_pedido_atual(request)
    modo = request.session.get("retorno_picking_modo")
    pedido_modo = request.session.get("retorno_picking_pedido")

    if modo and pedido_atual and pedido_modo != pedido_atual:
        request.session.pop("retorno_picking_modo", None)
        request.session.pop("retorno_picking_pedido", None)
        request.session.pop("kit_preview", None)
        request.session.modified = True

    serials = _get_serials_from_session(
        request, pedido_atual) if code == "202" else []

    modo_insercao = request.session.get("retorno_picking_modo")

    if request.method == "POST":

        if request.POST.get("definir_modo_retorno"):
            modo = request.POST.get("modo_insercao")

            if modo not in ("bipagem", "kit"):
                messages.error(request, "Escolha uma forma de inserção.")
                return redirect(request.path)

            request.session["retorno_picking_modo"] = modo
            request.session["retorno_picking_pedido"] = request.session.get(
                "pedido")
            request.session.modified = True

            return redirect(request.path)

        pedido_atual = _force_pedido(request)

        if request.POST.get("add_kit"):
            kit_number = (request.POST.get("kit_number") or "").strip().upper()

            if not kit_number:
                messages.warning(request, "Informe o número do kit.")
                return redirect(request.path)

            itens = KIT_DATA.get(kit_number)

            if not itens:
                messages.error(request, "Kit não encontrado.")
                return redirect(request.path)

            pedido_atual = _force_pedido(request)
            serials = _get_serials_from_session(request, pedido_atual)
            chip_map = request.session.get("chip_map", {})

            adicionados = 0

            for item in itens:
                s = item["serial"].upper()
                if s not in serials:
                    serials.append(s)
                    chip_map[s] = item.get("chip", "")
                    adicionados += 1

            _save_serials_to_session(request, pedido_atual, serials)
            request.session["chip_map"] = chip_map
            request.session.modified = True

            messages.success(
                request, f"{adicionados} seriais inseridos a partir do kit.")
            return redirect(request.path)

        if request.POST.get("buscar_kit"):
            kit_number = (request.POST.get("kit_number") or "").strip().upper()

            itens = KIT_DATA.get(kit_number)
            form = trackingIPForm(
                request.POST or None,
                nome_form=titulo,
                show_serial=code_info.show_serial,
                modo_insercao=modo_insercao
            )

            if not itens:
                messages.error(request, "Kit não encontrado.")
                return _render_pcp(
                    request,
                    form,
                    code_info,
                    serials
                )

            request.session["kit_preview"] = {
                "kit": kit_number,
                "itens": itens
            }
            request.session.modified = True

            return render(
                request,
                "logistica/templates_fluxo_entrega/pcp.html",
                {
                    "form": form,
                    "etapa_ativa": code_info.etapa_ativa,
                    "serials": serials,
                    "show_serial": True,
                    "busca_kit": kit_number,
                    "itens_kit": itens,
                },
            )

        if request.POST.get("confirmar_kit"):
            preview = request.session.get("kit_preview")

            if not preview:
                messages.error(request, "Nenhum kit carregado para inserção.")
                return redirect(request.path)

            pedido_atual = _force_pedido(request)
            serials = _get_serials_from_session(request, pedido_atual)
            chip_map = request.session.get("chip_map", {})

            adicionados = 0

            for item in preview["itens"]:
                s = item["serial"].upper()
                if s not in serials:
                    serials.append(s)
                    chip_map[s] = item.get("chip", "")
                    adicionados += 1

            _save_serials_to_session(request, pedido_atual, serials)
            request.session["chip_map"] = chip_map

            # limpa preview
            request.session.pop("kit_preview", None)
            request.session.modified = True

            messages.success(
                request, f"{adicionados} seriais inseridos a partir do kit."
            )
            return redirect(request.path)

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

        form = trackingIPForm(
            request.POST,
            nome_form=titulo,
            show_serial=code_info.show_serial,
            modo_insercao=modo_insercao
        )

        resp = _dispatch_serial_actions_if_any(
            request, code_info, pedido_atual, form)
        if resp:
            return resp

        resp = _process_enviar_evento(request, code_info, form, serials)
        if resp:
            return resp

        return _render_pcp(request, form, code_info, serials)

    initial = {}
    if _consume_carry_next(request):
        ped = (request.session.get("pedido") or "").strip()
        if ped:
            initial["pedido"] = ped

    form = trackingIPForm(initial=initial,
                          nome_form=titulo,
                          show_serial=code_info.show_serial,
                          modo_insercao=modo_insercao
                          )
    kit_preview = request.session.get("kit_preview")

    return _render_pcp(
        request,
        form,
        code_info,
        serials,
        busca_kit=kit_preview["kit"] if kit_preview else None,
        itens_kit=kit_preview["itens"] if kit_preview else None,
    )
