import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from logistica.models import GroupAditionalInformation
from setup.local_settings import API_BASE, STOCK_API_URL, TOKEN
from transportes.views.views_controle_chamados.view_consulta_os_pend import (
    get_base_usuario,
    get_bases_from_arancia_pa,
)
from utils.request import RequestClient

from ...forms import CheckInBagTecForm

JSON_CT = "application/json"
SESSION_BAG_TEC = "bag_tec_consulta"


def usuario_pode_ver_todas_bases(user):
    if user.has_perm("transportes.CC_admin"):
        return True

    gai = getattr(getattr(user, "designacao", None), "informacao_adicional", None)
    if gai and gai.group and gai.group.name == "arancia_CD":
        return True

    return False


def _configurar_choices_base(form, user, bases):
    base_usuario = get_base_usuario(user)

    if usuario_pode_ver_todas_bases(user):
        form.fields["base"].widget.choices = [("", "Selecione a base")] + bases
        return

    if base_usuario:
        form.fields["base"].widget.choices = [
            (base_usuario["value"], base_usuario["label"]),
        ]
        form.fields["base"].initial = base_usuario["value"]
        form.fields["base"].widget.attrs["disabled"] = "disabled"
    else:
        form.fields["base"].widget.choices = [("", "Selecione a base")]


def _base_selecionada_post(request):
    if usuario_pode_ver_todas_bases(request.user):
        return (request.POST.get("base") or "").strip()

    base_usuario = get_base_usuario(request.user)
    if base_usuario:
        return base_usuario["value"]

    return (request.POST.get("base") or "").strip()


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


_GAIS_NAO_EXIGEM_PRODUTO = frozenset({
    "ctb tatuapé 81",
    "ctb tatuapé 128",
})


def _normalizar_nome_gai(nome):
    return (nome or "").strip().lower()


def _usuario_nao_exige_produto(user):
    gai = getattr(getattr(user, "designacao", None), "informacao_adicional", None)
    if not gai:
        return False

    return _normalizar_nome_gai(gai.nome) in _GAIS_NAO_EXIGEM_PRODUTO


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
    if not tipo_filtro or tipo_filtro == "ambos":
        return None

    mapa = {
        "TO_BE_DELIVERED": ["TO_BE_DELIVERED"],
        "COLLECTED": ["COLLECTED"],
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


def _limpar_serial(serial):
    return str(serial or "").strip()


def _chave_serial(serial):
    return _limpar_serial(serial).upper()


def _extrair_order_number_consulta(item):
    if not isinstance(item, dict):
        return ""

    last_mov = item.get("last_movement") or item.get("last_mov") or {}
    extra_info = item.get("extra_info") or last_mov.get("extra_info") or {}

    order_number = (
        last_mov.get("order_number")
        or item.get("order_number")
        or last_mov.get("external_order_number")
        or item.get("external_order_number")
        or extra_info.get("order_number")
        or ""
    )

    return str(order_number).strip() if order_number else ""


def _extrair_nome_produto(item):
    if not isinstance(item, dict):
        return "-"

    product = item.get("product") or {}

    nome = (
        item.get("product_name")
        or product.get("description")
        or product.get("name")
        or product.get("product_name")
        or product.get("sku")
        or ""
    )

    return str(nome).strip() or "-"


def _extrair_client_code_item(item):
    if not isinstance(item, dict):
        return ""

    product = item.get("product") or {}
    last_mov = item.get("last_movement") or item.get("last_mov") or {}
    extra_info = item.get("extra_info") or last_mov.get("extra_info") or {}

    client_code = (
        item.get("client_code")
        or item.get("client_name")
        or last_mov.get("client_name")
        or last_mov.get("client_code")
        or product.get("client_code")
        or extra_info.get("client_code")
        or extra_info.get("client_name")
        or ""
    )

    return str(client_code).strip().lower()


def _formatar_itens_bag(itens):
    formatados = []

    for item in itens:
        if not isinstance(item, dict):
            continue

        product = item.get("product") or {}
        last_mov = item.get("last_movement") or item.get("last_mov") or {}
        order_number = _extrair_order_number_consulta(item)
        formatados.append({
            "serial": item.get("serial") or item.get("serial_number") or "-",
            "order_number": order_number,
            "product_id": _extrair_product_id(item) or "",
            "product_name": _extrair_nome_produto(item),
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


def _montar_mapa_seriais_bag(itens):
    mapa = {}

    for item in itens:
        if not isinstance(item, dict):
            continue

        serial = item.get("serial") or item.get("serial_number")
        if not serial:
            continue

        product_id = _extrair_product_id(item)
        mapa[_chave_serial(serial)] = {
            "order_number": _extrair_order_number_consulta(item),
            "product_id": product_id,
            "client_code": _extrair_client_code_item(item),
            "product_name": _extrair_nome_produto(item),
        }

    return mapa


def _resolver_dados_serial_bag(request, serial):
    estado = _obter_estado_sessao(request)
    seriais_bag = estado.get("seriais_bag") or estado.get("seriais_ordens") or {}
    dados = seriais_bag.get(_chave_serial(serial), {})

    if isinstance(dados, str):
        return {"order_number": dados}

    return dados if isinstance(dados, dict) else {}


def _buscar_dados_serial_na_bag(tecnico_uid, tipo_filtro, serial):
    if not tecnico_uid or not serial:
        return {}

    try:
        resp = _consultar_bag(tecnico_uid, tipo_filtro)
    except Exception:
        return {}

    if isinstance(resp, dict) and resp.get("detail"):
        return {}

    for item in _normalizar_itens_bag(resp):
        item_serial = item.get("serial") or item.get("serial_number")
        if item_serial and _chave_serial(item_serial) == _chave_serial(serial):
            return {
                "order_number": _extrair_order_number_consulta(item),
                "product_id": _extrair_product_id(item),
                "client_code": _extrair_client_code_item(item),
                "product_name": _extrair_nome_produto(item),
            }

    return {}


def _serial_tem_produto(product_id, dados_bag=None):
    if product_id:
        return True

    if not dados_bag:
        return False

    if dados_bag.get("product_id"):
        return True

    nome = (dados_bag.get("product_name") or "").strip()
    return bool(nome and nome != "-")


def _resolver_dados_serial_completos(request, tecnico_uid, tipo_filtro, serial):
    dados = _resolver_dados_serial_bag(request, serial)

    if dados.get("product_id"):
        return dados

    dados_api = _buscar_dados_serial_na_bag(
        tecnico_uid,
        tipo_filtro or _obter_estado_sessao(request).get("tipo_filtro") or "ambos",
        serial,
    )

    if not dados_api:
        return dados

    return {
        "order_number": dados_api.get("order_number") or dados.get("order_number") or "",
        "product_id": dados_api.get("product_id") or dados.get("product_id"),
        "client_code": dados_api.get("client_code") or dados.get("client_code") or "",
        "product_name": dados_api.get("product_name") or dados.get("product_name") or "-",
    }


def _buscar_order_number_na_bag(tecnico_uid, tipo_filtro, serial):
    if not tecnico_uid or not serial:
        return ""

    try:
        resp = _consultar_bag(tecnico_uid, tipo_filtro)
    except Exception:
        return ""

    if isinstance(resp, dict) and resp.get("detail"):
        return ""

    for item in _normalizar_itens_bag(resp):
        item_serial = item.get("serial") or item.get("serial_number")
        if item_serial and _chave_serial(item_serial) == _chave_serial(serial):
            return _extrair_order_number_consulta(item)

    return ""


def _resolver_order_number_bag(request, tecnico_uid, tipo_filtro, serial):
    dados = _resolver_dados_serial_bag(request, serial)
    order_number = dados.get("order_number") or ""

    if not order_number:
        order_number = _buscar_order_number_na_bag(
            tecnico_uid,
            tipo_filtro or _obter_estado_sessao(request).get("tipo_filtro") or "ambos",
            serial,
        )

    return order_number


def _carregar_clientes():
    try:
        url = f"{STOCK_API_URL}/v1/clients/?skip=0&limit=1000"
        res = RequestClient(url=url, method="GET", headers={"Accept": JSON_CT})
        result = res.send_api_request()

        if isinstance(result, list):
            data = result
        elif isinstance(result, dict):
            data = result.get("items") or result.get("results") or []
        else:
            data = json.loads(result) if result else []

        if not isinstance(data, list):
            return []

        return [
            (str(item.get("client_code", "")), item.get("client_name", "Sem nome"))
            for item in data
            if item.get("client_code")
        ]

    except Exception:
        return []


def _listar_produtos(client_code):
    if not client_code:
        return []

    url_produtos = f"{STOCK_API_URL}/v1/products/{client_code.lower()}"
    product_client = RequestClient(
        url=url_produtos,
        method="GET",
        headers={
            "Accept": JSON_CT,
            "Content-Type": JSON_CT,
        },
    )

    produtos_result = product_client.send_api_request()

    if isinstance(produtos_result, list):
        return produtos_result

    if isinstance(produtos_result, dict):
        return (
            produtos_result.get("items")
            or produtos_result.get("results")
            or produtos_result.get("products")
            or []
        )

    return []


def _normalizar_product_id(valor):
    if valor in [None, "", "0", 0]:
        return None

    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _extrair_product_id_deep(data, profundidade=0, dentro_product=False):
    if profundidade > 12 or data is None:
        return None

    if isinstance(data, dict):
        for chave in ("product_id", "productId", "id_product"):
            pid = _normalizar_product_id(data.get(chave))
            if pid:
                return pid

        if dentro_product:
            pid = _normalizar_product_id(data.get("id"))
            if pid:
                return pid

        for chave, valor in data.items():
            if chave == "product":
                pid = _extrair_product_id_deep(valor, profundidade + 1, dentro_product=True)
            elif isinstance(valor, dict):
                pid = _extrair_product_id_deep(valor, profundidade + 1, dentro_product=False)
            elif isinstance(valor, list):
                pid = None
                for elemento in valor:
                    pid = _extrair_product_id_deep(elemento, profundidade + 1, dentro_product=False)
                    if pid:
                        break
            else:
                continue

            if pid:
                return pid

    return None


def _extrair_product_id(item_info):
    if not isinstance(item_info, dict):
        return None

    product = item_info.get("product") or {}
    item_nested = item_info.get("item") or {}
    last_mov = item_info.get("last_movement") or item_info.get("last_mov") or {}
    last_mov_item = last_mov.get("item") or {}
    last_mov_product = last_mov.get("product") or {}
    extra_info = item_info.get("extra_info") or last_mov.get("extra_info") or {}
    product_id = (
        item_info.get("product_id")
        or item_info.get("productId")
        or item_nested.get("product_id")
        or item_nested.get("productId")
        or product.get("id")
        or product.get("product_id")
        or product.get("productId")
        or item_info.get("id_product")
        or last_mov.get("product_id")
        or last_mov.get("productId")
        or last_mov_item.get("product_id")
        or last_mov_item.get("productId")
        or last_mov_product.get("id")
        or last_mov_product.get("product_id")
        or extra_info.get("product_id")
        or extra_info.get("productId")
    )

    pid = _normalizar_product_id(product_id)
    if pid:
        return pid

    return _extrair_product_id_deep(item_info)


def _buscar_product_id_por_nome(client_code, product_name):
    nome_busca = (product_name or "").strip().lower()
    if not client_code or not nome_busca or nome_busca == "-":
        return None

    for produto in _listar_produtos(client_code):
        descricao = (produto.get("description") or produto.get("product_name") or "").strip().lower()
        sku = (produto.get("sku") or produto.get("product_code") or "").strip().lower()

        if nome_busca == descricao or nome_busca == sku:
            pid = _normalizar_product_id(produto.get("id"))
            if pid:
                return pid

    return None


def _consultar_item_por_serial_com_clientes(serial, gai, client_codes=None):
    vistos = set()
    candidatos = []

    for code in client_codes or []:
        code = (code or "").strip().lower()
        if not code or code in vistos:
            continue
        vistos.add(code)
        candidatos.append(code)

    for code_padrao in ("cielo", "claro"):
        if code_padrao not in vistos:
            candidatos.append(code_padrao)

    item_encontrado = None
    client_encontrado = None

    for code in candidatos:
        item = _consultar_item_por_serial(serial, gai, code)
        if not item:
            continue

        if not item_encontrado:
            item_encontrado = item
            client_encontrado = code

        pid = _extrair_product_id(item)
        if pid:
            return item, code, pid

    return item_encontrado, client_encontrado, (
        _extrair_product_id(item_encontrado) if item_encontrado else None
    )


def _resolver_product_id_serial(
    serial,
    gai,
    tecnico_uid,
    tipo_filtro,
    dados_bag,
    client_code=None,
    item_info=None,
    product_id_informado=None,
):
    pid = _normalizar_product_id(product_id_informado)
    if pid:
        return pid

    pid = _normalizar_product_id((dados_bag or {}).get("product_id"))
    if pid:
        return pid

    dados_frescos = _buscar_dados_serial_na_bag(tecnico_uid, tipo_filtro, serial)
    pid = _normalizar_product_id(dados_frescos.get("product_id"))
    if pid:
        return pid

    clientes = []
    for code in (
        client_code,
        (dados_bag or {}).get("client_code"),
        dados_frescos.get("client_code"),
    ):
        code = (code or "").strip().lower()
        if code and code not in clientes:
            clientes.append(code)

    if item_info:
        pid = _extrair_product_id(item_info)
        if pid:
            return pid

    item_resolvido, client_resolvido, pid = _consultar_item_por_serial_com_clientes(
        serial,
        gai,
        clientes,
    )
    if pid:
        return pid

    product_name = (
        (dados_bag or {}).get("product_name")
        or dados_frescos.get("product_name")
        or (_extrair_nome_produto(item_resolvido) if item_resolvido else "")
    )

    for code in clientes + ([client_resolvido] if client_resolvido else []) + ["cielo", "claro"]:
        code = (code or "").strip().lower()
        if not code:
            continue
        pid = _buscar_product_id_por_nome(code, product_name)
        if pid:
            return pid

    if item_resolvido:
        return _extrair_product_id(item_resolvido)

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


def _precisa_modal_produto(user, product_id):
    if product_id:
        return False

    return not _usuario_nao_exige_produto(user)


def _montar_payload_in_lote(itens, gai, tecnico_uid, username, client_code, order_number=None):
    tecnico_uid = str(tecnico_uid)
    payload = {
        "item": [
            {
                "serial": item["serial"],
                "product_id": int(item["product_id"]),
                "extra_info": {
                    "technician_uid": tecnico_uid,
                    "volume_number": 1,
                    "kit_number": 1,
                },
            }
            for item in itens
        ],
        "client_name": (client_code or "cielo").upper(),
        "movement_type": "IN",
        "to_location_id": gai.id,
        "order_origin_id": 3,
        "extra_info": {
            "technician_uid": tecnico_uid,
            "bag_operation": True,
        },
        "created_by": username or tecnico_uid,
    }

    if order_number:
        payload["order_number"] = str(order_number).strip()

    return payload


def _agrupar_pendentes_para_lote(pendentes):
    grupos = {}

    for item in pendentes:
        chave = (
            (item.get("client_code") or "cielo").strip().lower(),
            (item.get("order_number") or "").strip(),
        )
        grupos.setdefault(chave, []).append(item)

    return grupos


def _enviar_movimentos_in_lote(itens, gai, tecnico_uid, username, client_code, order_number=None):
    client = RequestClient(
        url=f"{STOCK_API_URL}/v1/movements/move-list-items",
        method="POST",
        headers={
            "Accept": JSON_CT,
            "Content-Type": JSON_CT,
        },
        request_data=_montar_payload_in_lote(
            itens,
            gai,
            tecnico_uid,
            username,
            client_code,
            order_number,
        ),
    )

    return client.send_api_request()


def _resposta_lote_sucesso(result):
    if isinstance(result, dict) and result.get("detail"):
        return False, result.get("detail")

    if result is None:
        return False, "Não foi possível registrar os movimentos."

    if isinstance(result, dict) and (
        result.get("id")
        or result.get("items")
        or result.get("success")
        or "success" in str(result).lower()
    ):
        return True, ""

    if isinstance(result, list) and result:
        return True, ""

    return True, ""


def _nome_tecnico(tecnicos_choices, tecnico_uid):
    for value, label in tecnicos_choices:
        if str(value) == str(tecnico_uid):
            return label
    return ""


def _redirect_checkin_bag_tec():
    return redirect(reverse("logistica:checkin_bag_tec"))


def _obter_estado_sessao(request):
    return request.session.get(SESSION_BAG_TEC) or {}


def _obter_seriais_pendentes_in(estado):
    pendentes = estado.get("seriais_pendentes_in") or []
    return pendentes if isinstance(pendentes, list) else []


def _chaves_seriais_pendentes(pendentes):
    return {_chave_serial(item.get("serial")) for item in pendentes if item.get("serial")}


def _marcar_itens_inseridos(itens_bag, pendentes):
    chaves_pendentes = _chaves_seriais_pendentes(pendentes)

    for item in itens_bag:
        item["inserido"] = _chave_serial(item.get("serial")) in chaves_pendentes

    return itens_bag


def _salvar_estado_sessao(
    request,
    base,
    tecnico_uid,
    tipo_filtro,
    modal_serial="",
    modal_client_code="",
    seriais_bag=None,
    seriais_pendentes_in=None,
):
    estado_atual = _obter_estado_sessao(request)

    if seriais_bag is None:
        seriais_bag = estado_atual.get("seriais_bag") or estado_atual.get("seriais_ordens") or {}

    if seriais_pendentes_in is None:
        seriais_pendentes_in = _obter_seriais_pendentes_in(estado_atual)

    request.session[SESSION_BAG_TEC] = {
        "base": base,
        "tecnico_uid": tecnico_uid,
        "tipo_filtro": tipo_filtro or "ambos",
        "modal_serial": modal_serial or "",
        "modal_client_code": modal_client_code or "",
        "seriais_bag": seriais_bag,
        "seriais_pendentes_in": seriais_pendentes_in,
    }
    request.session.modified = True


def _limpar_estado_sessao(request):
    request.session.pop(SESSION_BAG_TEC, None)
    request.session.modified = True


def _limpar_modal_sessao(request):
    estado = _obter_estado_sessao(request)
    if not estado:
        return

    estado["modal_serial"] = ""
    estado["modal_client_code"] = ""
    request.session[SESSION_BAG_TEC] = estado
    request.session.modified = True


def _consultar_bag_contexto(request, user, bases, base, tecnico_uid, tipo_filtro):
    base = _resolver_base(user, base)
    gai = _get_gai_por_base(base)

    if not gai:
        messages.error(request, "Base selecionada inválida.")
        return None

    try:
        tecnicos_choices = _buscar_tecnicos(base)
    except Exception as exc:
        messages.error(request, f"Erro ao buscar técnicos: {exc}")
        tecnicos_choices = [("", "Selecione o técnico")]

    try:
        resp = _consultar_bag(tecnico_uid, tipo_filtro)
    except Exception as exc:
        messages.error(request, f"Erro ao consultar bag: {exc}")
        return None

    if isinstance(resp, dict) and resp.get("detail"):
        messages.error(request, resp.get("detail"))
        return None

    itens_raw = _normalizar_itens_bag(resp)
    itens_bag = _formatar_itens_bag(itens_raw)
    client_choices = _carregar_clientes()

    if not client_choices:
        messages.warning(request, "Não foi possível carregar a lista de clientes.")

    return {
        "itens_bag": itens_bag,
        "client_choices": client_choices,
        "seriais_bag": _montar_mapa_seriais_bag(itens_raw),
        "bag_consultada": True,
        "base_consulta": base,
        "base_label": gai.nome or base,
        "tecnico_nome": _nome_tecnico(tecnicos_choices, tecnico_uid),
        "tecnico_uid_consulta": tecnico_uid,
        "tipo_filtro_consulta": tipo_filtro or "ambos",
        "tecnicos_choices": tecnicos_choices,
    }


def _processar_bipar_serial(
    request,
    base,
    tecnico_uid,
    serial,
    client_code=None,
    product_id=None,
):
    serial = _limpar_serial(serial)
    client_code = (client_code or "").strip().lower() or None

    if not base:
        messages.error(request, "Base não informada.")
        return "error"

    if not tecnico_uid:
        messages.error(request, "Técnico não informado.")
        return "error"

    if not serial:
        messages.error(request, "Serial não informado.")
        return "error"

    base = _resolver_base(request.user, base)
    gai = _get_gai_por_base(base)

    if not gai:
        messages.error(request, "Base inválida.")
        return "error"

    if product_id not in [None, "", "None", "null", 0, "0"]:
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            messages.warning(request, "Produto inválido. Informe um ID numérico.")
            return "need_modal"
    else:
        product_id = None

    estado = _obter_estado_sessao(request)
    tipo_filtro = estado.get("tipo_filtro") or "ambos"
    dados_bag = _resolver_dados_serial_completos(
        request,
        tecnico_uid,
        tipo_filtro,
        serial,
    )

    if not product_id and dados_bag.get("product_id"):
        product_id = dados_bag["product_id"]

    if not client_code and dados_bag.get("client_code"):
        client_code = dados_bag["client_code"]

    client_code_consulta = client_code or "cielo"
    item_info, client_resolvido, _ = _consultar_item_por_serial_com_clientes(
        serial,
        gai,
        [client_code_consulta, dados_bag.get("client_code")],
    )
    if client_resolvido and not client_code:
        client_code = client_resolvido

    product_id = _resolver_product_id_serial(
        serial=serial,
        gai=gai,
        tecnico_uid=tecnico_uid,
        tipo_filtro=tipo_filtro,
        dados_bag=dados_bag,
        client_code=client_code,
        item_info=item_info,
        product_id_informado=product_id,
    )

    if _precisa_modal_produto(request.user, product_id):
        messages.warning(request, "Selecione o cliente e o produto.")
        return "need_modal"

    client_code_final = client_code or _extrair_client_code_item(item_info) or "cielo"
    product_id_final = product_id

    if product_id_final is None and _usuario_nao_exige_produto(request.user):
        product_id_final = 0

    if product_id_final is None:
        messages.warning(request, "Selecione o cliente e o produto.")
        return "need_modal"

    order_number = _resolver_order_number_bag(request, tecnico_uid, tipo_filtro, serial)

    if not order_number and item_info:
        order_number = _extrair_order_number_consulta(item_info)

    pendentes = _obter_seriais_pendentes_in(estado)
    chave = _chave_serial(serial)

    if chave in _chaves_seriais_pendentes(pendentes):
        messages.warning(request, "Serial já inserido na lista de envio.")
        return "already_queued"

    pendentes.append({
        "serial": serial,
        "product_id": product_id_final,
        "client_code": client_code_final,
        "order_number": order_number or "",
    })

    request.session[SESSION_BAG_TEC] = {
        **estado,
        "seriais_pendentes_in": pendentes,
    }
    request.session.modified = True

    messages.success(request, f"Serial {serial} inserido. Total pendente: {len(pendentes)}.")
    return "success"


def _processar_finalizar_in(request, base, tecnico_uid):
    if not base:
        messages.error(request, "Base não informada.")
        return False

    if not tecnico_uid:
        messages.error(request, "Técnico não informado.")
        return False

    estado = _obter_estado_sessao(request)
    pendentes = _obter_seriais_pendentes_in(estado)

    if not pendentes:
        messages.warning(request, "Nenhum serial pendente para registrar.")
        return False

    base = _resolver_base(request.user, base)
    gai = _get_gai_por_base(base)

    if not gai:
        messages.error(request, "Base inválida.")
        return False

    grupos = _agrupar_pendentes_para_lote(pendentes)
    username = request.user.username
    enviados = 0
    erros = []
    chaves_enviadas = set()

    for (client_code, order_number), itens_grupo in grupos.items():
        try:
            result = _enviar_movimentos_in_lote(
                itens_grupo,
                gai,
                tecnico_uid,
                username,
                client_code,
                order_number or None,
            )
            sucesso, detalhe = _resposta_lote_sucesso(result)

            if sucesso:
                enviados += len(itens_grupo)
                for item in itens_grupo:
                    chaves_enviadas.add(_chave_serial(item.get("serial")))
            else:
                erros.append(detalhe or f"Falha ao registrar lote ({client_code}).")

        except Exception:
            erros.append(f"Erro ao comunicar com a API ({client_code}).")

    if enviados:
        messages.success(request, f"{enviados} movimento(s) IN registrado(s) com sucesso.")

    if erros:
        for erro in erros:
            messages.error(request, erro)

    restantes = [
        item for item in pendentes
        if _chave_serial(item.get("serial")) not in chaves_enviadas
    ]
    _salvar_estado_sessao(
        request,
        base,
        tecnico_uid,
        estado.get("tipo_filtro") or "ambos",
        seriais_pendentes_in=restantes,
    )

    return bool(enviados)


def _montar_form_consulta(request, titulo, bases, estado=None):
    if estado:
        initial = {
            "base": estado.get("base", ""),
            "tecnico": estado.get("tecnico_uid", ""),
            "tipo_filtro": estado.get("tipo_filtro", "ambos"),
        }
        form = CheckInBagTecForm(initial=initial, nome_form=titulo)
    else:
        form = CheckInBagTecForm(nome_form=titulo)

    _configurar_choices_base(form, request.user, bases)

    base_ref = (estado or {}).get("base") or _base_selecionada_post(request)
    if base_ref:
        try:
            tecnicos_choices = _buscar_tecnicos(base_ref)
        except Exception as exc:
            messages.error(request, f"Erro ao buscar técnicos: {exc}")
            tecnicos_choices = [("", "Selecione o técnico")]
    else:
        tecnicos_choices = [("", "Selecione o técnico")]

    form.fields["tecnico"].widget.choices = tecnicos_choices

    base_travada = not usuario_pode_ver_todas_bases(request.user)
    if base_travada and base_ref:
        form.fields["base"].initial = base_ref

    return form, tecnicos_choices


@csrf_protect
@login_required(login_url="logistica:login")
@permission_required("logistica.checkin_principal", raise_exception=True)
@permission_required("logistica.acesso_arancia", raise_exception=True)
def checkin_bag_tec(request):
    titulo = "Check-In de Bag Tec"
    bases = get_bases_from_arancia_pa()
    base_travada = not usuario_pode_ver_todas_bases(request.user)

    itens_bag = []
    client_choices = []
    produtos_modal_choices = []
    bag_consultada = False
    tecnico_nome = ""
    base_label = ""
    base_consulta = ""
    tecnico_uid_consulta = ""
    tipo_filtro_consulta = "ambos"
    modal_serial = ""
    modal_client_code = ""
    abrir_modal = False
    pendentes_count = 0

    estado_sessao = _obter_estado_sessao(request)
    pendentes_count = len(_obter_seriais_pendentes_in(estado_sessao))

    if request.method == "POST":
        if "cancelar_modal_bag_tec" in request.POST:
            _limpar_modal_sessao(request)
            messages.warning(request, "Seleção de cliente/produto cancelada.")
            return _redirect_checkin_bag_tec()

        if "carregar_produtos_modal" in request.POST:
            estado = _obter_estado_sessao(request)
            modal_serial = _limpar_serial(
                request.POST.get("modal_serial") or estado.get("modal_serial")
            )
            modal_client_code = (request.POST.get("client_code") or "").strip()

            if not modal_serial:
                messages.error(request, "Serial não informado.")
                return _redirect_checkin_bag_tec()

            if not modal_client_code:
                messages.error(request, "Cliente não informado.")
            else:
                produtos = _listar_produtos(modal_client_code)
                if not produtos:
                    messages.warning(request, "Nenhum produto encontrado para este cliente.")

            _salvar_estado_sessao(
                request,
                estado.get("base", ""),
                estado.get("tecnico_uid", ""),
                estado.get("tipo_filtro", "ambos"),
                modal_serial=modal_serial,
                modal_client_code=modal_client_code,
            )
            return _redirect_checkin_bag_tec()

        if "confirmar_bipar_modal" in request.POST:
            estado = _obter_estado_sessao(request)
            resultado = _processar_bipar_serial(
                request,
                base=estado.get("base"),
                tecnico_uid=estado.get("tecnico_uid"),
                serial=request.POST.get("modal_serial") or estado.get("modal_serial"),
                client_code=request.POST.get("client_code") or estado.get("modal_client_code"),
                product_id=request.POST.get("product_id"),
            )

            if resultado == "success":
                _salvar_estado_sessao(
                    request,
                    estado.get("base", ""),
                    estado.get("tecnico_uid", ""),
                    estado.get("tipo_filtro", "ambos"),
                )
            elif resultado == "need_modal":
                _salvar_estado_sessao(
                    request,
                    estado.get("base", ""),
                    estado.get("tecnico_uid", ""),
                    estado.get("tipo_filtro", "ambos"),
                    modal_serial=_limpar_serial(
                        request.POST.get("modal_serial") or estado.get("modal_serial")
                    ),
                    modal_client_code=(request.POST.get("client_code") or estado.get("modal_client_code") or "").strip(),
                )
            else:
                _salvar_estado_sessao(
                    request,
                    estado.get("base", ""),
                    estado.get("tecnico_uid", ""),
                    estado.get("tipo_filtro", "ambos"),
                    modal_serial=_limpar_serial(
                        request.POST.get("modal_serial") or estado.get("modal_serial")
                    ),
                    modal_client_code=(request.POST.get("client_code") or estado.get("modal_client_code") or "").strip(),
                )

            return _redirect_checkin_bag_tec()

        if "finalizar_in" in request.POST:
            estado = _obter_estado_sessao(request)
            base = estado.get("base") or _base_selecionada_post(request)
            tecnico_uid = estado.get("tecnico_uid") or (request.POST.get("tecnico") or "").strip()
            tipo_filtro = estado.get("tipo_filtro") or request.POST.get("tipo_filtro") or "ambos"

            _processar_finalizar_in(request, base, tecnico_uid)

            if estado.get("base") and estado.get("tecnico_uid"):
                consulta = _consultar_bag_contexto(
                    request,
                    request.user,
                    bases,
                    _resolver_base(request.user, base),
                    tecnico_uid,
                    tipo_filtro,
                )

                if consulta:
                    pendentes = _obter_seriais_pendentes_in(_obter_estado_sessao(request))
                    itens_bag = _marcar_itens_inseridos(consulta["itens_bag"], pendentes)
                    _salvar_estado_sessao(
                        request,
                        consulta["base_consulta"],
                        consulta["tecnico_uid_consulta"],
                        consulta["tipo_filtro_consulta"],
                        seriais_bag=consulta.get("seriais_bag"),
                        seriais_pendentes_in=pendentes,
                    )

            return _redirect_checkin_bag_tec()

        if "bipar_serial" in request.POST:
            estado = _obter_estado_sessao(request)
            base = estado.get("base") or _base_selecionada_post(request)
            tecnico_uid = estado.get("tecnico_uid") or (request.POST.get("tecnico") or "").strip()
            tipo_filtro = estado.get("tipo_filtro") or request.POST.get("tipo_filtro") or "ambos"
            serial = request.POST.get("serial")

            resultado = _processar_bipar_serial(
                request,
                base=base,
                tecnico_uid=tecnico_uid,
                serial=serial,
            )

            if resultado == "need_modal":
                _salvar_estado_sessao(
                    request,
                    base,
                    tecnico_uid,
                    tipo_filtro,
                    modal_serial=_limpar_serial(serial),
                )
            elif resultado == "success":
                _salvar_estado_sessao(request, base, tecnico_uid, tipo_filtro)
            else:
                _salvar_estado_sessao(request, base, tecnico_uid, tipo_filtro)

            return _redirect_checkin_bag_tec()

        form = CheckInBagTecForm(request.POST, nome_form=titulo)
        _configurar_choices_base(form, request.user, bases)

        base_selecionada = _base_selecionada_post(request)

        if base_selecionada and {"enviar_evento", "finalizar_in"} & request.POST.keys() == set():
            _limpar_estado_sessao(request)
            estado_sessao = {}
            pendentes_count = 0

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
                tecnicos_choices = [("", "Selecione o técnico")]
        else:
            tecnicos_choices = [("", "Selecione o técnico")]

        form.fields["tecnico"].widget.choices = tecnicos_choices

        if base_travada and base_selecionada:
            form.fields["base"].initial = base_selecionada

        if "enviar_evento" in request.POST:
            tecnico_uid = (request.POST.get("tecnico") or "").strip()
            tipo_filtro = request.POST.get("tipo_filtro") or "ambos"

            if not base_selecionada:
                messages.error(request, "Selecione uma base.")
            elif not tecnico_uid:
                messages.error(request, "Selecione um técnico.")
            else:
                base = _resolver_base(request.user, base_selecionada)
                consulta = _consultar_bag_contexto(
                    request,
                    request.user,
                    bases,
                    base,
                    tecnico_uid,
                    tipo_filtro,
                )

                if consulta:
                    pendentes = []
                    itens_bag = _marcar_itens_inseridos(consulta["itens_bag"], pendentes)
                    client_choices = consulta["client_choices"]
                    bag_consultada = consulta["bag_consultada"]
                    base_consulta = consulta["base_consulta"]
                    base_label = consulta["base_label"]
                    tecnico_nome = consulta["tecnico_nome"]
                    tecnico_uid_consulta = consulta["tecnico_uid_consulta"]
                    tipo_filtro_consulta = consulta["tipo_filtro_consulta"]
                    form.fields["tecnico"].widget.choices = consulta["tecnicos_choices"]

                    messages.success(
                        request,
                        f"Bag consultada com sucesso. Itens encontrados: {len(itens_bag)}",
                    )

                    _salvar_estado_sessao(
                        request,
                        base_consulta,
                        tecnico_uid_consulta,
                        tipo_filtro_consulta,
                        seriais_bag=consulta.get("seriais_bag"),
                        seriais_pendentes_in=[],
                    )
                    estado_sessao = _obter_estado_sessao(request)
                    pendentes_count = len(pendentes)

    else:
        form, _ = _montar_form_consulta(request, titulo, bases, estado_sessao)

        if estado_sessao.get("base") and estado_sessao.get("tecnico_uid"):
            consulta = _consultar_bag_contexto(
                request,
                request.user,
                bases,
                estado_sessao["base"],
                estado_sessao["tecnico_uid"],
                estado_sessao.get("tipo_filtro", "ambos"),
            )

            if consulta:
                pendentes = _obter_seriais_pendentes_in(estado_sessao)
                itens_bag = _marcar_itens_inseridos(consulta["itens_bag"], pendentes)
                client_choices = consulta["client_choices"]
                bag_consultada = consulta["bag_consultada"]
                base_consulta = consulta["base_consulta"]
                base_label = consulta["base_label"]
                tecnico_nome = consulta["tecnico_nome"]
                tecnico_uid_consulta = consulta["tecnico_uid_consulta"]
                tipo_filtro_consulta = consulta["tipo_filtro_consulta"]
                form.fields["tecnico"].widget.choices = consulta["tecnicos_choices"]

                modal_serial = _limpar_serial(estado_sessao.get("modal_serial"))
                modal_client_code = (estado_sessao.get("modal_client_code") or "").strip()
                abrir_modal = bool(modal_serial)

                _salvar_estado_sessao(
                    request,
                    base_consulta,
                    tecnico_uid_consulta,
                    tipo_filtro_consulta,
                    modal_serial=modal_serial,
                    modal_client_code=modal_client_code,
                    seriais_bag=consulta.get("seriais_bag"),
                    seriais_pendentes_in=pendentes,
                )
                estado_sessao = _obter_estado_sessao(request)
                pendentes_count = len(pendentes)

                if modal_client_code:
                    produtos_modal_choices = _listar_produtos(modal_client_code)

        elif not bag_consultada and not estado_sessao:
            if base_travada:
                base_usuario = get_base_usuario(request.user)
                if base_usuario:
                    try:
                        tecnicos_choices = _buscar_tecnicos(base_usuario["value"])
                        form.fields["tecnico"].widget.choices = tecnicos_choices
                    except Exception as exc:
                        messages.error(request, f"Erro ao buscar técnicos: {exc}")

    return render(
        request,
        "logistica/templates_checkin_checkout/checkin_bag_tec.html",
        {
            "form": form,
            "itens_bag": itens_bag,
            "client_choices": client_choices,
            "produtos_modal_choices": produtos_modal_choices,
            "bag_consultada": bag_consultada,
            "base_travada": base_travada,
            "base_consulta": base_consulta,
            "tecnico_nome": tecnico_nome,
            "tecnico_uid_consulta": tecnico_uid_consulta,
            "tipo_filtro_consulta": tipo_filtro_consulta,
            "base_label": base_label,
            "modal_serial": modal_serial,
            "modal_client_code": modal_client_code,
            "abrir_modal": abrir_modal,
            "pendentes_count": pendentes_count,
            "site_title": titulo,
            "botao_texto": "Consultar Bag",
            "current_parent_menu": "logistica",
            "current_menu": "checkin",
            "current_submenu": "checkin_bag_tec",
        },
    )
