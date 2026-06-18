"""Middleware de timing por request — ativar com PERFORMANCE_INSTRUMENTATION=True."""

from __future__ import annotations

import logging
import time

from django.conf import settings
from django.db import connection

from crm_api.instrumentation import get_request_stats, init_request_stats

logger = logging.getLogger("arancia.performance")


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "PERFORMANCE_INSTRUMENTATION", False):
            return self.get_response(request)

        init_request_stats(request)
        sql_count = {"n": 0}
        start = time.perf_counter()

        def execute_wrapper(execute, sql, params, many, context):
            sql_count["n"] += 1
            return execute(sql, params, many, context)

        with connection.execute_wrapper(execute_wrapper):
            response = self.get_response(request)

        total_ms = (time.perf_counter() - start) * 1000
        crm_stats = get_request_stats(request)

        logger.info(
            "PERF %s %s | total=%.1fms sql=%d crm_http=%d crm_latency=%.1fms",
            request.method,
            request.path,
            total_ms,
            sql_count["n"],
            crm_stats["count"],
            crm_stats["total_ms"],
        )

        response["X-Request-Time-Ms"] = f"{total_ms:.1f}"
        response["X-SQL-Queries"] = str(sql_count["n"])
        response["X-CRM-HTTP-Calls"] = str(crm_stats["count"])
        response["X-CRM-HTTP-Time-Ms"] = f"{crm_stats['total_ms']:.1f}"
        return response
