"""Request-scoped counters para chamadas HTTP à API de transportes."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from transportes.utils.baseline import (
    get_request_stats,
    init_request_stats,
    is_instrumentation_enabled,
    record_transp_api_call,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

__all__ = [
    "TranspApiCallTimer",
    "get_request_stats",
    "init_request_stats",
    "is_instrumentation_enabled",
    "record_transp_api_call",
]


class TranspApiCallTimer:
    """Context manager para medir uma chamada à API de transportes."""

    def __init__(
        self,
        request: HttpRequest | None,
        *,
        phase: str,
        url: str,
    ):
        self.request = request
        self.phase = phase
        self.url = url
        self.payload_size = 0
        self._start = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        record_transp_api_call(
            self.request,
            phase=self.phase,
            url=self.url,
            elapsed_ms=elapsed_ms,
            payload_size=self.payload_size,
        )
        return False
