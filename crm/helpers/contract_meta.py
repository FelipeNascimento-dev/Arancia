"""Metadados de contrato embutidos em ``description`` até a API expor ``number``/``value``."""

import re
from decimal import Decimal, InvalidOperation
from urllib.parse import quote, unquote

CRM_CONTRACT_META_RE = re.compile(
    r"^<!--crm-contract:([^>]*)-->\s*",
    re.MULTILINE,
)


def parse_contract_meta(description):
    """Extrai número/valor do comentário HTML e devolve a descrição limpa."""
    if description in (None, ""):
        return {}, ""
    text = str(description)
    match = CRM_CONTRACT_META_RE.match(text)
    if not match:
        return {}, text
    meta = {}
    for part in match.group(1).split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        value = unquote(value.strip())
        if key in ("numero", "valor") and value:
            meta[key] = value
    clean_desc = CRM_CONTRACT_META_RE.sub("", text, count=1).strip()
    return meta, clean_desc


def build_contract_meta_comment(*, numero=None, valor=None):
    parts = []
    if numero not in (None, ""):
        parts.append(f"numero={quote(str(numero).strip(), safe='')}")
    if valor not in (None, ""):
        if isinstance(valor, Decimal):
            value = str(valor)
        else:
            value = str(valor).strip()
        parts.append(f"valor={quote(value, safe='')}")
    if not parts:
        return ""
    return f"<!--crm-contract:{';'.join(parts)}-->\n"


def merge_contract_description(descricao, *, numero=None, valor=None):
    """Inclui metadados BFF no início da descrição enviada à API."""
    _, clean = parse_contract_meta(descricao or "")
    meta_line = build_contract_meta_comment(numero=numero, valor=valor)
    if not meta_line:
        return clean
    if clean:
        return f"{meta_line}{clean}"
    return meta_line.strip()


def contract_money_display(value):
    if value in (None, ""):
        return ""
    try:
        amount = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return str(value)
    from crm.helpers.dashboard import format_card_value

    return format_card_value("total_value", amount)
