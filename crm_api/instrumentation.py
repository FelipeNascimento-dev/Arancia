"""Request-scoped counters for CRM API HTTP calls (performance diagnostics)."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django.http import HttpRequest

_ATTR = "_crm_api_instrumentation"


def _empty_stats() -> dict[str, Any]:
    return {"calls": [], "count": 0, "total_ms": 0.0}


def init_request_stats(request: HttpRequest) -> dict[str, Any]:
    stats = _empty_stats()
    setattr(request, _ATTR, stats)
    return stats


def get_request_stats(request: HttpRequest) -> dict[str, Any]:
    return getattr(request, _ATTR, None) or _empty_stats()


def is_instrumentation_enabled() -> bool:
    from django.conf import settings

    return bool(getattr(settings, "PERFORMANCE_INSTRUMENTATION", False))


def record_crm_api_call(
    request: HttpRequest | None,
    *,
    method: str,
    url: str,
    elapsed_ms: float,
    status_code: int | None = None,
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
            "method": method.upper(),
            "url": url,
            "elapsed_ms": round(elapsed_ms, 2),
            "status_code": status_code,
        }
    )


class CrmApiCallTimer:
    """Context manager to time a single CRM API call."""

    def __init__(self, request, *, method: str, url: str):
        self.request = request
        self.method = method
        self.url = url
        self._start = 0.0
        self.status_code: int | None = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        record_crm_api_call(
            self.request,
            method=self.method,
            url=self.url,
            elapsed_ms=elapsed_ms,
            status_code=self.status_code,
        )
        return False
