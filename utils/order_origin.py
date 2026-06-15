"""
Catálogo de order origins (Stock API GET {STOCK_API_URL}/v1/origins).

Metadados estáveis entre homolog e prod — o id numérico varia por ambiente
e é aplicado em setup/local_settings via apply_environment (environments.py).

Uso nas views:
    from utils.order_origin import ORDER_ORIGIN_LAST_MILE_SUPRIMENTO
    payload["order_origin_id"] = ORDER_ORIGIN_LAST_MILE_SUPRIMENTO
"""
from setup import local_settings

ORIGINS_API_PATH = "/v1/origins"

# Metadados retornados pela API (match homolog ↔ prod por estes campos)
ORDER_ORIGIN_CATALOG = {
    "SAP_CACA_POS_AGUARDANDO_REVERSA": {
        "origin_name": "sap",
        "project_name": "Caça_POS",
        "stock_type": "Aguardando Reversa",
    },
    "LAST_MILE_SUPRIMENTO": {
        "origin_name": "intelipost",
        "project_name": "last_mile_b2c",
        "stock_type": "Suprimento P/ Entrega",
    },
    "LAST_MILE_AGUARDANDO_REVERSA": {
        "origin_name": "intelipost",
        "project_name": "last_mile_b2c",
        "stock_type": "Aguardando Reversa",
    },
    "REVERSA_AGUARDANDO": {
        "origin_name": "arancia",
        "project_name": "REVERSA",
        "stock_type": "Aguardando Reversa",
    },
    "SAP_CACA_POS_AGUARDANDO_REVERSA_PROVISORIO": {
        "origin_name": "sap",
        "project_name": "Caça_POS",
        "stock_type": "Aguardando Reversa (Seriais Provisórios)",
    },
    "REVERSA_AGUARDANDO_PROVISORIO": {
        "origin_name": "arancia",
        "project_name": "REVERSA",
        "stock_type": "Aguardando Reversa (Seriais Provisórios)",
    },
    "LAST_MILE_AGUARDANDO_REVERSA_PROVISORIO": {
        "origin_name": "intelipost",
        "project_name": "last_mile_b2c",
        "stock_type": "Aguardando Reversa (Seriais Provisórios)",
    },
    "SAP_BAU_SUPRIMENTO": {
        "origin_name": "SAP",
        "project_name": "BAU",
        "stock_type": "Suprimento P/ Entrega",
    },
    "LAST_MILE_SUPRIMENTO_ERRO_INTEGRACAO": {
        "origin_name": "intelipost",
        "project_name": "last_mile_b2c",
        "stock_type": "Suprimento P/ Entrega (Erro integração)",
    },
}

# IDs do ambiente ativo (homolog ou prod) — definidos em setup/environments.py
ORDER_ORIGIN_SAP_CACA_POS_AGUARDANDO_REVERSA = getattr(
    local_settings, "ORDER_ORIGIN_SAP_CACA_POS_AGUARDANDO_REVERSA", None
)
ORDER_ORIGIN_LAST_MILE_SUPRIMENTO = getattr(
    local_settings, "ORDER_ORIGIN_LAST_MILE_SUPRIMENTO", None
)
ORDER_ORIGIN_LAST_MILE_AGUARDANDO_REVERSA = getattr(
    local_settings, "ORDER_ORIGIN_LAST_MILE_AGUARDANDO_REVERSA", None
)
ORDER_ORIGIN_REVERSA_AGUARDANDO = getattr(
    local_settings, "ORDER_ORIGIN_REVERSA_AGUARDANDO", None
)
ORDER_ORIGIN_SAP_CACA_POS_AGUARDANDO_REVERSA_PROVISORIO = getattr(
    local_settings, "ORDER_ORIGIN_SAP_CACA_POS_AGUARDANDO_REVERSA_PROVISORIO", None
)
ORDER_ORIGIN_REVERSA_AGUARDANDO_PROVISORIO = getattr(
    local_settings, "ORDER_ORIGIN_REVERSA_AGUARDANDO_PROVISORIO", None
)
ORDER_ORIGIN_LAST_MILE_AGUARDANDO_REVERSA_PROVISORIO = getattr(
    local_settings, "ORDER_ORIGIN_LAST_MILE_AGUARDANDO_REVERSA_PROVISORIO", None
)
ORDER_ORIGIN_SAP_BAU_SUPRIMENTO = getattr(
    local_settings, "ORDER_ORIGIN_SAP_BAU_SUPRIMENTO", None
)
ORDER_ORIGIN_LAST_MILE_SUPRIMENTO_ERRO_INTEGRACAO = getattr(
    local_settings, "ORDER_ORIGIN_LAST_MILE_SUPRIMENTO_ERRO_INTEGRACAO", None
)

__all__ = [
    "ORIGINS_API_PATH",
    "ORDER_ORIGIN_CATALOG",
    "ORDER_ORIGIN_SAP_CACA_POS_AGUARDANDO_REVERSA",
    "ORDER_ORIGIN_LAST_MILE_SUPRIMENTO",
    "ORDER_ORIGIN_LAST_MILE_AGUARDANDO_REVERSA",
    "ORDER_ORIGIN_REVERSA_AGUARDANDO",
    "ORDER_ORIGIN_SAP_CACA_POS_AGUARDANDO_REVERSA_PROVISORIO",
    "ORDER_ORIGIN_REVERSA_AGUARDANDO_PROVISORIO",
    "ORDER_ORIGIN_LAST_MILE_AGUARDANDO_REVERSA_PROVISORIO",
    "ORDER_ORIGIN_SAP_BAU_SUPRIMENTO",
    "ORDER_ORIGIN_LAST_MILE_SUPRIMENTO_ERRO_INTEGRACAO",
]
