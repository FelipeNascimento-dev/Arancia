from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from setup.local_settings import API_BASE, STOCK_API_URL, TOKEN
from transportes.views.views_controle_chamados.view_consulta_os_pend import (
    get_bases_from_arancia_pa,
)
from utils.request import RequestClient

from ...forms import AtrelarMotoboyForm
from .view_checkin_bag_tec import (
    _base_selecionada_post,
    _configurar_choices_base,
    _get_gai_por_base,
    _limpar_serial,
    _resolver_base,
    usuario_pode_ver_todas_bases,
)

JSON_CT = "application/json"
SESSION_SERIALS_KEY = "atrelar_motoboy_serials"


def _motoboy_choices(base):
    resp = RequestClient(
        method="get",
        url=f"{API_BASE}/v3/controle_campo/tecnicos/{base}",
        headers={
            "accept": "application/json",
            "access_token": TOKEN,
            "Content-Type": "application/json",
        },
    ).send_api_request()

    if isinstance(resp, dict) and resp.get("detail"):
        return [], resp.get("detail")

    if not isinstance(resp, list):
        return [], "Nenhum motoboy retornado."

    return [("", "Selecione o motoboy")] + [
        (str(item["uid"]), item["name"])
        for item in resp
        if item.get("uid") is not None and item.get("name")
    ], None


def _configurar_form(request, form, bases, post_data=None):
    _configurar_choices_base(form, request.user, bases)

    base_ref = _base_selecionada_post(request)
    if not base_ref and post_data:
        base_ref = (post_data.get("base") or "").strip()
    if not base_ref:
        base_ref = form.fields["base"].initial or ""

    if base_ref:
        motoboy_choices, erro = _motoboy_choices(base_ref)
        if erro:
            messages.error(request, erro)
    else:
        motoboy_choices = [("", "Selecione o motoboy")]

    form.fields["motoboy"].widget.choices = motoboy_choices

    base_travada = not usuario_pode_ver_todas_bases(request.user)
    if base_travada and base_ref:
        form.fields["base"].initial = base_ref

    return base_travada


def _montar_payload_movimento_lote(serials, gai, motoboy_uid, order_number=None):
    motoboy_uid = str(motoboy_uid)
    payload = {
        "item": [
            {
                "product_id": 0,
                "serial": serial,
                "extra_info": {
                    "motoboy_uid": motoboy_uid,
                    "volume_number": 1,
                    "kit_number": 1,
                },
            }
            for serial in serials
        ],
        "client_name": "",
        "movement_type": "TO_BE_DELIVERED",
        "to_location_id": gai.id,
        "order_origin_id": 3,
        "extra_info": {
            "motoboy_uid": motoboy_uid,
            "motoboy_operation": True,
        },
        "created_by": motoboy_uid,
    }

    if order_number:
        payload["order_number"] = str(order_number).strip()

    return payload


def _enviar_movimentos_motoboy(serials, gai, motoboy_uid, order_number=None):
    client = RequestClient(
        url=f"{STOCK_API_URL}/v1/movements/move-list-items",
        method="POST",
        headers={
            "Accept": JSON_CT,
            "Content-Type": JSON_CT,
        },
        request_data=_montar_payload_movimento_lote(
            serials,
            gai,
            motoboy_uid,
            order_number,
        ),
    )

    return client.send_api_request()


@csrf_protect
@login_required(login_url="logistica:login")
@permission_required("logistica.checkin_principal", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def atrelar_motoboy(request):
    titulo = "Atrelar Motoboy"
    bases = get_bases_from_arancia_pa()
    serials = list(request.session.get(SESSION_SERIALS_KEY) or [])
    form_initial = {}

    if request.method == "POST":
        form_initial = {
            "base": _base_selecionada_post(request) or (request.POST.get("base") or "").strip(),
            "motoboy": (request.POST.get("motoboy") or "").strip(),
            "order_number": (request.POST.get("order_number") or "").strip(),
        }

        if "add_serial" in request.POST:
            serial = _limpar_serial(request.POST.get("serial"))
            if not serial:
                messages.info(request, "Digite um serial.")
            elif serial in serials:
                messages.warning(request, "Serial já está na lista.")
            else:
                serials.append(serial)
                messages.success(request, f"Serial {serial} adicionado.")

        elif "remove_serial" in request.POST:
            try:
                idx = int(request.POST.get("remove_serial"))
                if 0 <= idx < len(serials):
                    removido = serials.pop(idx)
                    messages.success(request, f"Removido: {removido}")
            except (TypeError, ValueError):
                messages.error(request, "Não foi possível remover o serial.")

        elif "clear_serials" in request.POST:
            serials = []
            messages.success(request, "Lista de seriais limpa.")

        elif "enviar_evento" in request.POST:
            base_selecionada = _base_selecionada_post(request)
            motoboy_uid = form_initial["motoboy"]
            order_number = form_initial["order_number"]

            if not base_selecionada:
                messages.error(request, "Selecione uma base.")
            elif not motoboy_uid:
                messages.error(request, "Selecione um motoboy.")
            elif not serials:
                messages.error(request, "Adicione ao menos um serial.")
            else:
                gai = _get_gai_por_base(_resolver_base(request.user, base_selecionada))

                if not gai:
                    messages.error(request, "Base selecionada inválida.")
                else:
                    result = _enviar_movimentos_motoboy(
                        serials,
                        gai,
                        motoboy_uid,
                        order_number,
                    )

                    if isinstance(result, dict) and result.get("detail"):
                        messages.error(request, result.get("detail"))
                    elif result is None:
                        messages.error(request, "Erro ao atrelar seriais.")
                    else:
                        messages.success(
                            request,
                            f"{len(serials)} serial(is) atrelado(s) ao motoboy.",
                        )
                        serials = []

        request.session[SESSION_SERIALS_KEY] = serials
        request.session.modified = True

        if {"add_serial", "remove_serial", "clear_serials", "enviar_evento"} & request.POST.keys():
            form = AtrelarMotoboyForm(initial=form_initial, nome_form=titulo)
        else:
            form = AtrelarMotoboyForm(request.POST, nome_form=titulo)
    else:
        form = AtrelarMotoboyForm(nome_form=titulo)

    base_travada = _configurar_form(
        request,
        form,
        bases,
        post_data=request.POST if request.method == "POST" else None,
    )

    return render(
        request,
        "logistica/templates_checkin_checkout/atrelar_motoboy.html",
        {
            "form": form,
            "serials": serials,
            "base_travada": base_travada,
            "site_title": titulo,
            "botao_texto": "Atrelar Motoboy",
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "atrelar_motoboy",
        },
    )
