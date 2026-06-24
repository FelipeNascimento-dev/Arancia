"""Instrumentação e probes de baseline para APIs de transportes (Fase 0)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlencode

from setup.local_settings import TRANSP_API_URL
from transportes.utils.metadata_api import default_transp_api_headers
from utils.request import RequestClient

logger = logging.getLogger("arancia.performance.transportes")

_ATTR = "_transp_api_instrumentation"


@dataclass
class ApiTimingResult:
    name: str
    url: str
    elapsed_ms: float
    payload_size: int = 0
    response_type: str = ""
    error: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaginationProbeResult:
    supports_offset_limit: bool
    response_shape: str
    has_total_field: bool
    total_field_name: str | None
    page0_count: int
    page1_count: int
    total_reported: int | None
    distinct_ids_page0_vs_page1: bool
    notes: list[str] = field(default_factory=list)


def is_instrumentation_enabled() -> bool:
    from django.conf import settings

    return bool(getattr(settings, "PERFORMANCE_INSTRUMENTATION", False))


def init_request_stats(request) -> dict[str, Any]:
    stats: dict[str, Any] = {"calls": [], "count": 0, "total_ms": 0.0}
    setattr(request, _ATTR, stats)
    return stats


def get_request_stats(request) -> dict[str, Any]:
    return getattr(request, _ATTR, None) or {
        "calls": [],
        "count": 0,
        "total_ms": 0.0,
    }


def record_transp_api_call(
    request,
    *,
    phase: str,
    url: str,
    elapsed_ms: float,
    payload_size: int = 0,
) -> None:
    if request is None or not is_instrumentation_enabled():
        return

    stats = get_request_stats(request)
    if not hasattr(request, _ATTR):
        init_request_stats(request)
        stats = get_request_stats(request)

    stats["count"] += 1
    stats["total_ms"] += elapsed_ms
    stats["calls"].append(
        {
            "phase": phase,
            "url": url,
            "elapsed_ms": round(elapsed_ms, 2),
            "payload_size": payload_size,
        }
    )
    logger.info(
        "TRANS_PERF %s | phase=%s | %.1fms | items=%d | %s",
        getattr(request, "path", "?"),
        phase,
        elapsed_ms,
        payload_size,
        url,
    )


def measure_transp_api(
    name: str,
    url: str,
    *,
    params: dict | None = None,
    timeout: int = 100,
) -> ApiTimingResult:
    """Mede uma chamada GET à API de transportes e retorna timing + tamanho do payload."""
    headers = default_transp_api_headers()
    client = RequestClient(
        method="get",
        url=url,
        headers=headers,
        request_data=params,
        timeout=timeout,
    )
    start = time.perf_counter()
    try:
        data = client.send_api_request()
        elapsed_ms = (time.perf_counter() - start) * 1000
        payload_size, response_type = _payload_metrics(data)
        return ApiTimingResult(
            name=name,
            url=url,
            elapsed_ms=elapsed_ms,
            payload_size=payload_size,
            response_type=response_type,
        )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ApiTimingResult(
            name=name,
            url=url,
            elapsed_ms=elapsed_ms,
            error=str(exc),
        )


def _payload_metrics(data) -> tuple[int, str]:
    if isinstance(data, list):
        return len(data), "list"
    if isinstance(data, dict):
        if data.get("detail"):
            return 0, "error"
        for key in ("items", "results", "data"):
            items = data.get(key)
            if isinstance(items, list):
                return len(items), f"dict[{key}]"
        total = data.get("total") or data.get("count") or data.get("total_count")
        if total is not None:
            return int(total), "dict[total_only]"
        return 0, "dict"
    return 0, type(data).__name__


def _extract_travel_items(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and not data.get("detail"):
        for key in ("items", "results", "data"):
            items = data.get(key)
            if isinstance(items, list):
                return items
    return []


def _travel_row_id(item: dict) -> str | None:
    travel = item.get("travel") or {}
    travel_id = travel.get("id")
    if travel_id is not None:
        return str(travel_id)
    return None


def _find_total_field(data: dict) -> tuple[bool, str | None, int | None]:
    for field_name in ("total", "count", "total_count"):
        value = data.get(field_name)
        if value is not None:
            try:
                return True, field_name, int(value)
            except (TypeError, ValueError):
                continue
    return False, None, None


def probe_order_travel_pagination(
    *,
    page_size: int = 50,
    base_params: dict | None = None,
    timeout: int = 100,
) -> PaginationProbeResult:
    """
    Valida se v2/order_travel/list/general honra offset/limit e expõe total/count.

    Compara página 0 e página 1; verifica formato da resposta e campos de total.
    """
    params_base = {"Response": "resume"}
    if base_params:
        params_base.update(base_params)

    notes: list[str] = []

    def fetch_page(offset: int) -> tuple[Any, float]:
        params = {**params_base, "offset": offset, "limit": page_size}
        url = (
            f"{TRANSP_API_URL}/v2/order_travel/list/general?"
            f"{urlencode(params, safe=',')}"
        )
        result = measure_transp_api(
            f"order_travel_offset_{offset}",
            url,
            timeout=timeout,
        )
        if result.error:
            notes.append(f"offset={offset}: {result.error}")
            return None, result.elapsed_ms
        headers = default_transp_api_headers()
        client = RequestClient(method="get", url=url, headers=headers, timeout=timeout)
        return client.send_api_request(), result.elapsed_ms

    page0_raw, _ = fetch_page(0)
    page1_raw, _ = fetch_page(page_size)

    if page0_raw is None:
        return PaginationProbeResult(
            supports_offset_limit=False,
            response_shape="error",
            has_total_field=False,
            total_field_name=None,
            page0_count=0,
            page1_count=0,
            total_reported=None,
            distinct_ids_page0_vs_page1=False,
            notes=notes or ["Falha ao consultar página 0"],
        )

    if isinstance(page0_raw, list):
        response_shape = "list"
        page0_items = page0_raw
        has_total, total_field, total_reported = False, None, None
    elif isinstance(page0_raw, dict):
        if page0_raw.get("detail"):
            return PaginationProbeResult(
                supports_offset_limit=False,
                response_shape="error",
                has_total_field=False,
                total_field_name=None,
                page0_count=0,
                page1_count=0,
                total_reported=None,
                distinct_ids_page0_vs_page1=False,
                notes=[str(page0_raw.get("detail"))],
            )
        has_total, total_field, total_reported = _find_total_field(page0_raw)
        page0_items = _extract_travel_items(page0_raw)
        response_shape = "dict"
        if page0_items:
            response_shape = f"dict[{total_field or 'items'}]"
    else:
        return PaginationProbeResult(
            supports_offset_limit=False,
            response_shape=type(page0_raw).__name__,
            has_total_field=False,
            total_field_name=None,
            page0_count=0,
            page1_count=0,
            total_reported=None,
            distinct_ids_page0_vs_page1=False,
            notes=["Formato de resposta inesperado"],
        )

    page1_items = _extract_travel_items(page1_raw) if page1_raw is not None else []

    ids0 = {_travel_row_id(item) for item in page0_items}
    ids0.discard(None)
    ids1 = {_travel_row_id(item) for item in page1_items}
    ids1.discard(None)
    distinct = bool(ids0 and ids1 and not ids0.intersection(ids1))

    # Heurística: offset/limit funcionam se página 1 tem itens distintos ou página 0 tem exatamente page_size
    supports = distinct or (
        len(page0_items) == page_size and len(page1_items) > 0
    )

    if len(page0_items) > page_size:
        notes.append(
            f"API retornou {len(page0_items)} itens com limit={page_size} — "
            "possível ignorar paginação"
        )
        supports = False

    if not has_total:
        notes.append(
            "Resposta sem total/count — usar heurística has_next=len(items)==limit (padrão OS)"
        )

    return PaginationProbeResult(
        supports_offset_limit=supports,
        response_shape=response_shape,
        has_total_field=has_total,
        total_field_name=total_field,
        page0_count=len(page0_items),
        page1_count=len(page1_items),
        total_reported=total_reported,
        distinct_ids_page0_vs_page1=distinct,
        notes=notes,
    )


def measure_lista_viagens_apis(*, timeout: int = 100) -> list[ApiTimingResult]:
    """Mede as três APIs usadas na abertura da Lista de Viagens."""
    results: list[ApiTimingResult] = []

    url_clientes = f"{TRANSP_API_URL}/gai/clientes/status?cliente=arancia_client"
    results.append(
        measure_transp_api("clientes_status", url_clientes, timeout=timeout)
    )

    url_carriers = f"{TRANSP_API_URL}/Carriers/list"
    results.append(
        measure_transp_api("carriers_list", url_carriers, timeout=timeout)
    )

    params = {"Response": "resume"}
    url_travel = (
        f"{TRANSP_API_URL}/v2/order_travel/list/general?"
        f"{urlencode(params, safe=',')}"
    )
    results.append(
        measure_transp_api("order_travel_full", url_travel, timeout=timeout)
    )

    params_paged = {"Response": "resume", "offset": 0, "limit": 50}
    url_travel_paged = (
        f"{TRANSP_API_URL}/v2/order_travel/list/general?"
        f"{urlencode(params_paged, safe=',')}"
    )
    results.append(
        measure_transp_api("order_travel_p50", url_travel_paged, timeout=timeout)
    )

    return results
