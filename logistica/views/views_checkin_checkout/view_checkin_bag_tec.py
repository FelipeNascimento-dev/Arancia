import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from logistica.models import GroupAditionalInformation
from setup.local_settings import API_BASE, STOCK_API_URL, TOKEN
from transportes.views.views_controle_chamados.view_consulta_os_pend import (
    get_base_usuario,
    get_bases_from_arancia_pa,
    usuario_pode_ver_todas_bases,
)
from utils.request import RequestClient

from ...forms import CheckInBagTecForm

JSON_CT = "application/json"


def _configurar_choices_base(form, user, bases):
    base_usuario = get_base_usuario(user)

    if usuario_pode_ver_todas_bases(user):
        form.fields["base"].widget.choices = [("", "Selecione a base")] + bases
        return

    if base_usuario:
        form.fields["base"].widget.choices = [
            ("", "Selecione a base"),
            (base_usuario["value"], base_usuario["label"]),
        ]
    else:
        form.fields["base"].widget.choices = [("", "Selecione a base")]


def _resolver_base(user, base_informada):
    if usuario_pode_ver_todas_bases(user):
        return base_informada

    base_usuario = get_base_usuario(user)
    if base_usuario:
        return base_usuario["value"]

    return base_informada


def _get_gai_por_base(base_value):
    if not base_value or not str(base_value).startswith("PA_"):
        return None

    cod_iata = str(base_value)[3:]
    return (
        GroupAditionalInformation.objects
        .filter(group__name="arancia_PA", cod_iata=cod_iata)
        .select_related("group")
        .first()
    )


def _is_pa_sao_paulo(gai):
    if not gai:
        return False

    nome = (gai.nome or "").strip().lower()
    cod = (gai.cod_iata or "").strip().upper()

    if nome == "ctb tatuapé 81":
        return True
    if "são paulo" in nome or "sao paulo" in nome:
        return True
    if cod in ("SPO", "SAO", "SP"):
        return True

    return False


def _buscar_tecnicos(base):
    url = f"{API_BASE}/v3/controle_campo/tecnicos/{base}"
    headers = {
        "accept": "application/json",
        "access_token": TOKEN,
        "Content-Type": "application/json",
    }

    client = RequestClient(method="get", url=url, headers=headers)
    resp = client.send_api_request()

    if not isinstance(resp, list):
        return []

    return [("", "Selecione o técnico")] + [
        (tec["uid"], tec["name"])
        for tec in resp
        if tec.get("uid") is not None
    ]


def _movement_types_por_filtro(tipo_filtro):
    mapa = {
        "entrega": ["OUT"],
        "coletado": ["IN"],
    }
    return mapa.get(tipo_filtro)


def _consultar_bag(tecnico_uid, tipo_filtro):
    url = f"{STOCK_API_URL}/v1/items/search-by-movement"
    params = {
        "created_by": str(tecnico_uid),
        "offset": 0,
        "limit": 100,
    }

    movement_types = _movement_types_por_filtro(tipo_filtro or "ambos")
    if movement_types:
        params["movement_type"] = movement_types

    client = RequestClient(
        method="GET",
        url=url,
        headers={"Accept": JSON_CT},
        request_data=params,
    )

    return client.send_api_request()


def _normalizar_itens_bag(resposta):
    if isinstance(resposta, list):
        return resposta

    if isinstance(resposta, dict):
        if resposta.get("detail"):
            return resposta

        return (
            resposta.get("items")
            or resposta.get("results")
            or resposta.get("serials")
            or []
        )

    return []


def _formatar_itens_bag(itens):
    formatados = []

    for item in itens:
        if not isinstance(item, dict):
            continue

        product = item.get("product") or {}
        last_mov = item.get("last_movement") or item.get("last_mov") or {}
        formatados.append({
            "serial": item.get("serial") or item.get("serial_number") or "-",
            "product_id": item.get("product_id") or product.get("id") or "",
            "product_name": (
                item.get("product_name")
                or product.get("description")
                or product.get("sku")
                or "-"
            ),
            "tipo": (
                last_mov.get("movement_type")
                or item.get("movement_type")
                or item.get("item_type")
                or item.get("tipo")
                or item.get("type")
                or "-"
            ),
        })

    return formatados


def _carregar_produtos(client_code):
    if not client_code:
        return []

    url = f"{STOCK_API_URL}/v1/products/{client_code.lower()}"
    client = RequestClient(
        method="GET",
        url=url,
        headers={"Accept": JSON_CT},
    )

    resp = client.send_api_request()

    if isinstance(resp, list):
        return resp

    if isinstance(resp, dict):
        return (
            resp.get("items")
            or resp.get("results")
            or resp.get("products")
            or []
        )

    return []


def _extrair_product_id(item_info):
    if not isinstance(item_info, dict):
        return None

    product = item_info.get("product") or {}
    product_id = (
        item_info.get("product_id")
        or product.get("id")
        or item_info.get("id_product")
    )

    if product_id in [None, "", 0, "0"]:
        return None

    try:
        return int(product_id)
    except (TypeError, ValueError):
        return None


def _consultar_item_por_serial(serial, gai, client_code):
    url = (
        f"{STOCK_API_URL}/v1/items/delivery/{serial}"
        f"?client={client_code.lower()}&location_id={gai.id}"
    )

    client = RequestClient(
        method="GET",
        url=url,
        headers={"accept": JSON_CT},
    )

    resp = client.send_api_request()

    if isinstance(resp, dict) and "detail" not in resp:
        return resp

    return None


def _produto_obrigatorio(gai, item_info, product_id_informado):
    if product_id_informado:
        return False

    product_id_existente = _extrair_product_id(item_info)

    if product_id_existente and not _is_pa_sao_paulo(gai):
        return False

    return not product_id_existente


def _registrar_movimento_in(serial, gai, tecnico_uid, username, product_id=None, client_code="cielo"):
    item_payload = {
        "serial": serial,
        "extra_info": {
            "technician_uid": str(tecnico_uid),
        },
    }

    if product_id:
        item_payload["product_id"] = int(product_id)

    payload = {
        "item": item_payload,
        "client_name": client_code.lower(),
        "movement_type": "IN",
        "from_location_id": 0,
        "to_location_id": gai.id,
        "order_origin_id": 3,
        "extra_info": {
            "technician_uid": str(tecnico_uid),
            "bag_operation": True,
        },
        "created_by": str(tecnico_uid),
    }

    client = RequestClient(
        url=f"{STOCK_API_URL}/v1/movements/",
        method="POST",
        headers={
            "Accept": JSON_CT,
            "Content-Type": JSON_CT,
        },
        request_data=payload,
    )

    return client.send_api_request()


def _nome_tecnico(tecnicos_choices, tecnico_uid):
    for value, label in tecnicos_choices:
        if str(value) == str(tecnico_uid):
            return label
    return ""


@csrf_protect
@login_required(login_url="logistica:login")
@permission_required("logistica.checkin_principal", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def checkin_bag_tec(request):
    titulo = "Check-In de Bag Tec"
    bases = get_bases_from_arancia_pa()
    tecnicos_choices = [("", "Selecione o técnico")]
    itens_bag = []
    produtos_choices = []
    bag_consultada = False
    tecnico_nome = ""
    base_label = ""

    if request.method == "POST":
        form = CheckInBagTecForm(request.POST, nome_form=titulo)
        _configurar_choices_base(form, request.user, bases)

        base_selecionada = (request.POST.get("base") or "").strip()

        if base_selecionada:
            try:
                tecnicos_choices = _buscar_tecnicos(base_selecionada)
                if len(tecnicos_choices) <= 1 and "enviar_evento" not in request.POST:
                    messages.warning(
                        request,
                        "Essa base não possui técnicos cadastrados.",
                    )
            except Exception as exc:
                messages.error(request, f"Erro ao buscar técnicos: {exc}")

        form.fields["tecnico"].widget.choices = tecnicos_choices

        if "enviar_evento" in request.POST:
            tecnico_uid = (request.POST.get("tecnico") or "").strip()
            tipo_filtro = request.POST.get("tipo_filtro") or "ambos"

            if not base_selecionada:
                messages.error(request, "Selecione uma base.")
            elif not tecnico_uid:
                messages.error(request, "Selecione um técnico.")
            else:
                base = _resolver_base(request.user, base_selecionada)
                gai = _get_gai_por_base(base)

                if not gai:
                    messages.error(request, "Base selecionada inválida.")
                else:
                    base_label = gai.nome or base
                    tecnico_nome = _nome_tecnico(tecnicos_choices, tecnico_uid)
                    client_code = (gai.sales_channel or "cielo").lower()

                    try:
                        resp = _consultar_bag(tecnico_uid, tipo_filtro)

                        if isinstance(resp, dict) and resp.get("detail"):
                            messages.error(request, resp.get("detail"))
                        else:
                            itens_bag = _formatar_itens_bag(_normalizar_itens_bag(resp))
                            bag_consultada = True
                            messages.success(
                                request,
                                f"Bag consultada com sucesso. Itens encontrados: {len(itens_bag)}",
                            )

                        produtos_choices = _carregar_produtos(client_code)

                    except Exception as exc:
                        messages.error(request, f"Erro ao consultar bag: {exc}")

    else:
        form = CheckInBagTecForm(nome_form=titulo)
        _configurar_choices_base(form, request.user, bases)
        form.fields["tecnico"].widget.choices = tecnicos_choices

    return render(
        request,
        "logistica/templates_checkin_checkout/checkin_bag_tec.html",
        {
            "form": form,
            "itens_bag": itens_bag,
            "produtos_choices": produtos_choices,
            "bag_consultada": bag_consultada,
            "tecnico_nome": tecnico_nome,
            "base_label": base_label,
            "site_title": titulo,
            "botao_texto": "Consultar Bag",
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "checkin_bag_tec",
        },
    )


@login_required(login_url="logistica:login")
@permission_required("logistica.checkin_principal", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
@require_POST
def bipar_serial_bag_tec(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "ERROR",
            "message": "JSON inválido.",
        }, status=400)

    base = body.get("base")
    tecnico_uid = body.get("tecnico_uid")
    serial = str(body.get("serial") or "").strip().upper()
    product_id = body.get("product_id")

    if not base:
        return JsonResponse({
            "status": "ERROR",
            "message": "Base não informada.",
        }, status=400)

    if not tecnico_uid:
        return JsonResponse({
            "status": "ERROR",
            "message": "Técnico não informado.",
        }, status=400)

    if not serial:
        return JsonResponse({
            "status": "ERROR",
            "message": "Serial não informado.",
        }, status=400)

    base = _resolver_base(request.user, base)
    gai = _get_gai_por_base(base)

    if not gai:
        return JsonResponse({
            "status": "ERROR",
            "message": "Base inválida.",
        }, status=400)

    client_code = (gai.sales_channel or "cielo").lower()

    if product_id not in [None, "", "None", "null", 0, "0"]:
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return JsonResponse({
                "status": "NEED_PRODUCT",
                "serial": serial,
                "message": "Produto inválido. Informe um ID numérico.",
            }, status=400)
    else:
        product_id = None

    item_info = _consultar_item_por_serial(serial, gai, client_code)

    if _produto_obrigatorio(gai, item_info, product_id):
        return JsonResponse({
            "status": "NEED_PRODUCT",
            "serial": serial,
            "message": "Informe o produto para este serial.",
        }, status=400)

    product_id_final = product_id or _extrair_product_id(item_info)

    try:
        result = _registrar_movimento_in(
            serial=serial,
            gai=gai,
            tecnico_uid=tecnico_uid,
            username=request.user.username,
            product_id=product_id_final,
            client_code=client_code,
        )

        if isinstance(result, dict) and (
            result.get("id") or "success" in str(result).lower()
        ):
            return JsonResponse({
                "status": "SUCCESS",
                "serial": serial,
                "product_id": product_id_final,
                "message": "Movimento IN registrado com sucesso.",
            })

        detail = result.get("detail") if isinstance(result, dict) else str(result)
        return JsonResponse({
            "status": "ERROR",
            "serial": serial,
            "message": detail or "Não foi possível registrar o movimento.",
            "api_response": result,
        }, status=400)

    except Exception:
        return JsonResponse({
            "status": "ERROR",
            "message": "Erro ao comunicar com a API de movimentos.",
        }, status=500)
