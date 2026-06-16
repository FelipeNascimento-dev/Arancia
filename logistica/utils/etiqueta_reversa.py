import base64
import io
from typing import Any, Dict, List, Optional

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def _primeiro_valor(*valores: Any) -> str:
    for valor in valores:
        if valor is None:
            continue
        texto = str(valor).strip()
        if texto and texto.lower() not in {"none", "null", "-"}:
            return texto
    return ""


def _buscar_gai(gai_id: Any):
    if gai_id in (None, "", "None"):
        return None
    try:
        from logistica.models import GroupAditionalInformation

        return GroupAditionalInformation.objects.filter(id=int(gai_id)).first()
    except (ValueError, TypeError):
        return None


def _partes_de_gai(gai) -> Dict[str, str]:
    telefones = ", ".join(
        filter(
            None,
            [
                _primeiro_valor(gai.telefone1),
                _primeiro_valor(gai.telefone2),
            ],
        )
    )

    return {
        "nome": _primeiro_valor(gai.nome),
        "razao_social": _primeiro_valor(gai.razao_social),
        "cnpj": _primeiro_valor(gai.cnpj),
        "inscricao_estadual": _primeiro_valor(gai.inscricao_estadual),
        "logradouro": _primeiro_valor(gai.logradouro),
        "numero": _primeiro_valor(gai.numero),
        "complemento": _primeiro_valor(gai.complemento),
        "bairro": _primeiro_valor(gai.bairro),
        "cidade": _primeiro_valor(gai.cidade),
        "uf": _primeiro_valor(gai.UF),
        "cep": _primeiro_valor(gai.CEP),
        "cod_iata": _primeiro_valor(gai.cod_iata),
        "cod_center": _primeiro_valor(gai.cod_center),
        "deposito": _primeiro_valor(gai.deposito),
        "telefones": telefones,
        "email": _primeiro_valor(gai.email),
        "responsavel": _primeiro_valor(gai.responsavel),
    }


def _partes_de_dict(data: Dict[str, Any]) -> Dict[str, str]:
    telefones = _primeiro_valor(
        data.get("telefones"),
        data.get("telefone"),
        data.get("phone"),
        data.get("telefone1"),
    )
    if not telefones:
        telefones = ", ".join(
            filter(
                None,
                [
                    _primeiro_valor(data.get("telefone1")),
                    _primeiro_valor(data.get("telefone2")),
                ],
            )
        )

    return {
        "nome": _primeiro_valor(data.get("nome"), data.get("name")),
        "razao_social": _primeiro_valor(data.get("razao_social"), data.get("company_name")),
        "cnpj": _primeiro_valor(data.get("cnpj"), data.get("document")),
        "inscricao_estadual": _primeiro_valor(
            data.get("inscricao_estadual"),
            data.get("ie"),
        ),
        "logradouro": _primeiro_valor(
            data.get("logradouro"),
            data.get("endereco"),
            data.get("address"),
            data.get("street"),
        ),
        "numero": _primeiro_valor(data.get("numero"), data.get("number")),
        "complemento": _primeiro_valor(data.get("complemento"), data.get("complement")),
        "bairro": _primeiro_valor(data.get("bairro"), data.get("district"), data.get("neighborhood")),
        "cidade": _primeiro_valor(data.get("cidade"), data.get("city")),
        "uf": _primeiro_valor(data.get("uf"), data.get("UF"), data.get("state")),
        "cep": _primeiro_valor(data.get("cep"), data.get("CEP"), data.get("zip_code")),
        "cod_iata": _primeiro_valor(data.get("cod_iata"), data.get("iata")),
        "cod_center": _primeiro_valor(data.get("cod_center"), data.get("center")),
        "deposito": _primeiro_valor(data.get("deposito"), data.get("warehouse")),
        "telefones": telefones,
        "email": _primeiro_valor(data.get("email"), data.get("mail")),
        "responsavel": _primeiro_valor(data.get("responsavel"), data.get("contact")),
    }


def _mesclar_partes(base: Dict[str, str], overlay: Dict[str, str]) -> Dict[str, str]:
    resultado = dict(base)
    for chave, valor in overlay.items():
        if valor:
            resultado[chave] = valor
    return resultado


def _montar_linha_logradouro(partes: Dict[str, str]) -> str:
    logradouro = partes.get("logradouro", "")
    numero = partes.get("numero", "")
    complemento = partes.get("complemento", "")

    if logradouro and numero:
        linha = f"{logradouro}, {numero}"
    else:
        linha = logradouro or numero

    if complemento:
        linha = f"{linha} - {complemento}" if linha else complemento

    return linha


def _montar_linha_cidade(partes: Dict[str, str]) -> str:
    cidade = partes.get("cidade", "")
    uf = partes.get("uf", "")
    if cidade and uf:
        return f"{cidade} - {uf}"
    return cidade or uf


def _montar_linhas_endereco(partes: Dict[str, str]) -> List[str]:
    linhas: List[str] = []

    nome = partes.get("nome", "")
    razao = partes.get("razao_social", "")

    if razao and (not nome or razao.lower() != nome.lower()):
        linhas.append(razao)

    documentos = " · ".join(
        filter(
            None,
            [
                f"CNPJ {partes['cnpj']}" if partes.get("cnpj") else "",
                f"IE {partes['inscricao_estadual']}" if partes.get("inscricao_estadual") else "",
            ],
        )
    )
    if documentos:
        linhas.append(documentos)

    endereco = _montar_linha_logradouro(partes)
    if endereco:
        linhas.append(endereco)

    localidade = " · ".join(
        filter(
            None,
            [
                partes.get("bairro", ""),
                _montar_linha_cidade(partes),
                f"CEP {partes['cep']}" if partes.get("cep") else "",
            ],
        )
    )
    if localidade:
        linhas.append(localidade)

    contato = " · ".join(
        filter(
            None,
            [
                f"Tel {partes['telefones']}" if partes.get("telefones") else "",
                partes.get("email", ""),
                f"Resp. {partes['responsavel']}" if partes.get("responsavel") else "",
            ],
        )
    )
    if contato:
        linhas.append(contato)

    referencia = " · ".join(
        filter(
            None,
            [
                f"IATA {partes['cod_iata']}" if partes.get("cod_iata") else "",
                f"Centro {partes['cod_center']}" if partes.get("cod_center") else "",
                f"Dep. {partes['deposito']}" if partes.get("deposito") else "",
            ],
        )
    )
    if referencia:
        linhas.append(referencia)

    return linhas


def montar_endereco_etiqueta(
    valor: Any,
    gai_id: Any = None,
) -> Dict[str, Any]:
    partes: Dict[str, str] = {}

    gai = _buscar_gai(gai_id)
    if gai:
        partes = _partes_de_gai(gai)

    if isinstance(valor, dict):
        partes = _mesclar_partes(partes, _partes_de_dict(valor))
    elif isinstance(valor, str):
        texto = valor.strip()
        if texto:
            if partes.get("nome"):
                partes = _mesclar_partes(partes, {"nome": texto})
            else:
                partes["nome"] = texto

    linhas = _montar_linhas_endereco(partes)
    if not linhas and valor not in (None, ""):
        linhas = [str(valor).strip()]

    titulo = _primeiro_valor(partes.get("nome"), partes.get("razao_social"), "—")

    return {
        "titulo": titulo,
        "linhas": linhas,
    }


def extrair_seriais_volume(volume: Dict[str, Any]) -> List[str]:
    seriais = []
    for kit in volume.get("kits") or []:
        serial = str(kit.get("serial") or "").strip().upper()
        if serial:
            seriais.append(serial)
    return seriais


def montar_conteudo_qr(
    numero_romaneio: str,
    volume_atual: int,
    volume_total: int,
    seriais: List[str],
) -> str:
    linhas = [
        "ROMANEIO REVERSA",
        "================",
        "",
        f"Romaneio: {numero_romaneio}",
        f"Volume:   {volume_atual} de {volume_total}",
        f"Kits:     {len(seriais)}",
        "",
        "SERIAIS",
        "-------",
    ]

    largura_num = len(str(len(seriais))) if seriais else 1
    for indice, serial in enumerate(seriais, start=1):
        linhas.append(f"{indice:0{largura_num}d}. {serial}")

    return "\n".join(linhas)


def gerar_qr_base64(conteudo: str) -> str:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(conteudo)
    qr.make(fit=True)

    buffer = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _numero_romaneio(romaneio_data: Dict[str, Any], fallback: str = "") -> str:
    for chave in ("order_number", "numero", "external_order_number", "romaneio_number"):
        valor = romaneio_data.get(chave)
        if valor:
            return str(valor).strip()
    return str(fallback).strip()


def _resolver_gai_id(romaneio_data: Dict[str, Any], *chaves: str) -> Any:
    for chave in chaves:
        valor = romaneio_data.get(chave)
        if valor not in (None, "", "None"):
            return valor
    return None


def montar_etiqueta_reversa(
    romaneio_data: Dict[str, Any],
    volume_number: int,
    romaneio_fallback: str = "",
) -> Optional[Dict[str, Any]]:
    volums = romaneio_data.get("volums") or []
    total_volumes = len(volums)

    volume = None
    for item in volums:
        if int(item.get("volum_number") or 0) == int(volume_number):
            volume = item
            break

    if not volume:
        return None

    seriais = extrair_seriais_volume(volume)
    numero = _numero_romaneio(romaneio_data, romaneio_fallback)

    qr_texto = montar_conteudo_qr(
        numero,
        int(volume_number),
        total_volumes,
        seriais,
    )

    return {
        "romaneio_numero": numero,
        "volume_atual": int(volume_number),
        "volume_total": total_volumes,
        "volume_label": f"{volume_number}/{total_volumes}",
        "barcode_value": numero,
        "qr_payload": qr_texto,
        "qr_image_base64": gerar_qr_base64(qr_texto),
        "seriais_count": len(seriais),
        "remetente": montar_endereco_etiqueta(
            romaneio_data.get("origin"),
            gai_id=_resolver_gai_id(
                romaneio_data,
                "origin_id",
                "from_location_id",
            ),
        ),
        "destinatario": montar_endereco_etiqueta(
            romaneio_data.get("destination"),
            gai_id=_resolver_gai_id(
                romaneio_data,
                "destination_id",
                "to_location_id",
            ),
        ),
    }


def montar_etiquetas_todos_volumes(
    romaneio_data: Dict[str, Any],
    romaneio_fallback: str = "",
) -> List[Dict[str, Any]]:
    etiquetas = []
    for volume in romaneio_data.get("volums") or []:
        volume_number = int(volume.get("volum_number") or 0)
        if not volume_number:
            continue
        etiqueta = montar_etiqueta_reversa(
            romaneio_data,
            volume_number,
            romaneio_fallback=romaneio_fallback,
        )
        if etiqueta:
            etiquetas.append(etiqueta)
    return etiquetas
