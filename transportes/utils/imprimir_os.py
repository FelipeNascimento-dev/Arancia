from datetime import datetime
import json


def _formatar_data(data_str, com_hora=False):
    if not data_str or data_str == "None":
        return None

    try:
        dt = datetime.fromisoformat(str(data_str).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M" if com_hora else "%d/%m/%Y")
    except Exception:
        return str(data_str)


def _normalizar_equipamento_serial(serial):
    if isinstance(serial, dict):
        nr_chamado = serial.get("nr_chamado") or serial.get("patrimonio") or "-"
        serie = (
            serial.get("serial_number")
            or serial.get("serie")
            or serial.get("serial")
            or "-"
        )
        if nr_chamado in (None, "", "None"):
            nr_chamado = "-"
        if serie in (None, "", "None"):
            serie = "-"
        return {
            "nr_chamado": str(nr_chamado),
            "serie": str(serie),
        }

    if serial in (None, "", "None"):
        return {"nr_chamado": "-", "serie": "-"}

    return {"nr_chamado": "-", "serie": str(serial)}


def _extrair_extra_information(extra):
    if isinstance(extra, dict):
        return extra
    if isinstance(extra, str) and extra.strip():
        try:
            parsed = json.loads(extra)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


def extrair_nr_chamado_item(item):
    extra = _extrair_extra_information((item or {}).get("extra_information"))
    nr_chamado = extra.get("nr_chamado") or "-"
    if nr_chamado in (None, "", "None"):
        return "-"
    return str(nr_chamado)


def enriquecer_itens_viagem(itens):
    enriquecidos = []
    for item in itens or []:
        if not isinstance(item, dict):
            continue
        enriquecidos.append({
            **item,
            "nr_chamado": extrair_nr_chamado_item(item),
        })
    return enriquecidos


def _montar_equipamentos(extra, os_items=None, tipo_descricao="", os_externa="-"):
    equipamentos = []

    if os_items:
        for item in os_items:
            item_extra = _extrair_extra_information(item.get("extra_information"))
            nr_chamado = item_extra.get("nr_chamado") or "-"
            serie = item.get("serial_number") or "-"
            if nr_chamado in (None, "", "None"):
                nr_chamado = "-"
            if serie in (None, "", "None"):
                serie = "-"
            equipamentos.append({
                "nr_chamado": str(nr_chamado),
                "serie": str(serie),
                "descricao": tipo_descricao or "-",
            })

    if not equipamentos:
        for serial in extra.get("seriais") or []:
            dados_serial = _normalizar_equipamento_serial(serial)
            equipamentos.append({
                "nr_chamado": dados_serial["nr_chamado"],
                "serie": dados_serial["serie"],
                "descricao": tipo_descricao or "-",
            })

    if not equipamentos:
        equipamentos.append({
            "nr_chamado": "-",
            "serie": "-",
            "descricao": f"OS: {os_externa} | {tipo_descricao}".strip(" |"),
        })

    return equipamentos


def _montar_endereco(local, endereco_extra=None):
    endereco_extra = endereco_extra or {}

    cep = endereco_extra.get("cep") or local.get("CEP") or ""
    logradouro = endereco_extra.get("logradouro") or local.get("logradouro") or ""
    numero = endereco_extra.get("numero") or local.get("numero") or ""
    bairro = endereco_extra.get("bairro") or local.get("bairro") or ""
    cidade = endereco_extra.get("cidade") or local.get("cidade") or ""
    uf = endereco_extra.get("uf") or local.get("UF") or ""

    linha_rua = f"{logradouro} {numero}".strip()
    if complemento := (endereco_extra.get("complemento") or local.get("complemento")):
        linha_rua = f"{linha_rua} {complemento}".strip()

    if not linha_rua and local.get("endereco"):
        partes = [p.strip() for p in str(local.get("endereco")).split(",") if p.strip()]
        if partes:
            linha_rua = partes[0]
            if len(partes) > 1:
                bairro = bairro or partes[1]
            if len(partes) > 2:
                cidade = cidade or partes[2]

    linha_cidade = ", ".join(filter(None, [bairro, f"{cidade} - {uf}" if cidade and uf else cidade or uf]))

    return {
        "cep": cep,
        "linha_rua": linha_rua or "-",
        "linha_cidade": linha_cidade or "-",
        "nome": local.get("nome") or "-",
    }


def montar_contexto_impressao_os(item, os_items=None):
    travel = item.get("travel") or {}
    service_order = item.get("service_order") or {}
    extra = service_order.get("extra_information") or {}
    destination = service_order.get("destination") or {}
    origin = service_order.get("origin") or {}
    client = service_order.get("client") or {}
    order_type = service_order.get("order_type") or {}

    direction = str(order_type.get("direction") or "normal").lower()
    local = destination if direction == "normal" else origin
    endereco = _montar_endereco(local, extra.get("endereco"))

    phones = extra.get("phones") or []
    fones = ", ".join(str(phone) for phone in phones if phone)

    os_externa = service_order.get("external_order_number") or service_order.get("order_number") or "-"
    tipo_descricao = order_type.get("description") or order_type.get("type") or ""

    equipamentos = _montar_equipamentos(
        extra,
        os_items=os_items,
        tipo_descricao=tipo_descricao,
        os_externa=os_externa,
    )

    ag_data = extra.get("ag_data") or travel.get("created_at")
    driver = travel.get("driver") or {}

    return {
        "travel_id": travel.get("id"),
        "os_numero": os_externa,
        "operacao": extra.get("cod_staff") or driver.get("nome_unidade") or "-",
        "tecnico": extra.get("cod_staff") or driver.get("name") or "-",
        "data": _formatar_data(ag_data, com_hora=False) or "-",
        "servico_de": (
            extra.get("cliente_logomarca")
            or extra.get("cliente_empresa")
            or client.get("nome")
            or "-"
        ),
        "assinante": extra.get("bordero_empresa") or endereco["nome"],
        "documento": extra.get("bordero_documento") or "",
        "cep": endereco["cep"] or "-",
        "endereco_linha1": endereco["linha_rua"],
        "endereco_linha2": endereco["linha_cidade"],
        "contato": extra.get("bordero_contato") or "-",
        "fones": fones or "-",
        "ag_memo": extra.get("ag_memo") or "",
        "equipamentos": equipamentos,
        "tipo_servico": tipo_descricao,
        "transportadora": (travel.get("carrier") or {}).get("nome") or "-",
        "motorista": driver.get("name") or "-",
    }
