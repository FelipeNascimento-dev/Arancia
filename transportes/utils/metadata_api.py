"""Metadados compartilhados da API de transportes (clientes/status, carriers) com cache Django."""

from __future__ import annotations

from setup.local_settings import TRANSP_API_URL
from transportes.utils.utils import get_api_data, get_multiple_api_data

METADATA_CACHE_TTL = 600  # 10 minutos
CACHE_KEY_CLIENTES_STATUS = "transp_metadata:v1:clientes_status"
CACHE_KEY_CARRIERS_LIST = "transp_metadata:v1:carriers_list"


def default_transp_api_headers() -> dict[str, str]:
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def normalize_clientes_status_response(data) -> list:
    if isinstance(data, dict) and data.get("detail"):
        return []
    if isinstance(data, list):
        return data
    return []


def normalize_carriers_list_response(data) -> list:
    if isinstance(data, dict) and data.get("detail"):
        return []
    if isinstance(data, dict):
        return (
            data.get("items")
            or data.get("results")
            or []
        )
    if isinstance(data, list):
        return data
    return []


def get_clientes_status(*, ttl: int = METADATA_CACHE_TTL) -> list:
    """Lista de clientes com OrderType/status — cache global (não depende de usuário)."""
    url = f"{TRANSP_API_URL}/gai/clientes/status"
    params = {"cliente": "arancia_client"}
    headers = default_transp_api_headers()
    raw = get_api_data(CACHE_KEY_CLIENTES_STATUS, url, params, headers, ttl)
    return normalize_clientes_status_response(raw)


def get_carriers_list(*, ttl: int = METADATA_CACHE_TTL) -> list:
    """Lista de transportadoras — cache global."""
    url = f"{TRANSP_API_URL}/Carriers/list"
    headers = default_transp_api_headers()
    raw = get_api_data(CACHE_KEY_CARRIERS_LIST, url, {}, headers, ttl)
    return normalize_carriers_list_response(raw)


def get_transportes_metadata(*, ttl: int = METADATA_CACHE_TTL) -> dict[str, list]:
    """Busca clientes/status e Carriers/list em paralelo (com cache)."""
    headers = default_transp_api_headers()
    requests_list = [
        (
            CACHE_KEY_CLIENTES_STATUS,
            f"{TRANSP_API_URL}/gai/clientes/status",
            {"cliente": "arancia_client"},
        ),
        (
            CACHE_KEY_CARRIERS_LIST,
            f"{TRANSP_API_URL}/Carriers/list",
            {},
        ),
    ]
    results = get_multiple_api_data(requests_list, headers, ttl)
    return {
        "clientes_status": normalize_clientes_status_response(
            results.get(CACHE_KEY_CLIENTES_STATUS, {})
        ),
        "carriers_list": normalize_carriers_list_response(
            results.get(CACHE_KEY_CARRIERS_LIST, {})
        ),
    }
