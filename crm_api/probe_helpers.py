"""Shared constants and helpers for CRM API latency probes and acceptance checks."""

from __future__ import annotations

import statistics
from typing import Any
from uuid import UUID

INSTRUMENTATION_HEADERS = (
    "X-Request-Time-Ms",
    "X-Handler-Time-Ms",
    "X-SQL-Queries",
    "X-Cache",
    "X-DB-Pool-Wait-Ms",
)

SLOW_THRESHOLD_MS = 500
KANBAN_SLA_MS = 3000
DASHBOARD_SLA_MS = 2000
LOOKUPS_WARM_SLA_MS = 100
LOOKUPS_COLD_SLA_MS = 500

# Labels used by probe commands and homolog validation
SLA_MS_BY_LABEL = {
    "kanban_bundle": KANBAN_SLA_MS,
    "dashboard_summary": DASHBOARD_SLA_MS,
    "board_page": LOOKUPS_COLD_SLA_MS,
    "billing_lookups": LOOKUPS_COLD_SLA_MS,
    "lookups_crm": LOOKUPS_WARM_SLA_MS,
    "lookups_crm_warm": LOOKUPS_WARM_SLA_MS,
}

LEGACY_PROBE_ENDPOINTS = [
    ("health", "", "GET", None),
    ("lookups_crm", "lookups/crm", "GET", None),
    ("lookups_gais", "lookups/gais", "GET", None),
    ("me_context", "me/context", "GET", None),
    ("boards_list", "boards/", "GET", None),
]

AGGREGATE_PROBE_ENDPOINTS = [
    ("board_page", "lookups/board-page", "GET", {"gais_limit": 50}),
    ("dashboard_summary", "dashboard/summary", "GET", None),
    ("billing_lookups", "lookups/billing", "GET", None),
]


def validate_board_id(board_id: str) -> str:
    """Return normalized board UUID string or raise ValueError."""
    return str(UUID(board_id))


def capture_instrumentation_headers(response) -> dict[str, str]:
    headers = getattr(response, "headers", {}) or {}
    return {
        name: headers[name]
        for name in INSTRUMENTATION_HEADERS
        if name in headers
    }


def auth_est_ms(instr_headers: dict[str, str]) -> int | None:
    total = instr_headers.get("X-Request-Time-Ms")
    handler = instr_headers.get("X-Handler-Time-Ms")
    if total is None or handler is None:
        return None
    return max(0, int(total) - int(handler))


def sla_threshold_ms(label: str, *, x_cache: str = "") -> int | None:
    if label == "lookups_crm" and x_cache.upper() == "HIT":
        return LOOKUPS_WARM_SLA_MS
    if label == "lookups_crm":
        return LOOKUPS_COLD_SLA_MS
    return SLA_MS_BY_LABEL.get(label)


def sla_met(label: str, elapsed_ms: float, *, x_cache: str = "") -> tuple[bool, str]:
    threshold = sla_threshold_ms(label, x_cache=x_cache)
    if threshold is None:
        return True, ""
    if elapsed_ms <= threshold:
        return True, ""
    return False, f"{elapsed_ms:.0f} ms > SLA {threshold} ms"


def format_probe_row(
    label: str,
    *,
    status: int,
    elapsed_ms: float,
    instr_headers: dict[str, str] | None = None,
    error: str = "",
    path: str = "",
) -> str:
    parts = [
        f"{label:<20}",
        f"HTTP {status:>3}",
        f"wall={elapsed_ms:>7.1f}ms",
    ]
    for header in INSTRUMENTATION_HEADERS:
        value = (instr_headers or {}).get(header)
        if value is not None:
            parts.append(f"{header}={value}")
    est = auth_est_ms(instr_headers or {})
    if est is not None:
        parts.append(f"auth_est={est}ms")
    threshold = sla_threshold_ms(label, x_cache=(instr_headers or {}).get("X-Cache", ""))
    if threshold is not None and status == 200:
        ok, _ = sla_met(label, elapsed_ms, x_cache=(instr_headers or {}).get("X-Cache", ""))
        parts.append("SLA_OK" if ok else "SLA_FAIL")
    if error:
        parts.append(f"ERR={error[:80]}")
    if path:
        parts.append(f"/{path.lstrip('/')}")
    return " | ".join(parts)


def build_probe_endpoints(
    board_id: str | None,
    *,
    include_aggregates: bool,
) -> list[tuple[str, str, str, dict | None]]:
    endpoints = list(LEGACY_PROBE_ENDPOINTS)
    if include_aggregates:
        endpoints.extend(AGGREGATE_PROBE_ENDPOINTS)
        if board_id:
            endpoints.append((
                "kanban_bundle",
                f"boards/{board_id}/kanban",
                "GET",
                {"task_limit": 100},
            ))
    elif board_id:
        endpoints.extend([
            ("board_detail", f"boards/{board_id}", "GET", None),
            ("board_columns", f"boards/{board_id}/columns", "GET", None),
            ("board_tasks", "tasks/", "GET", {"board_id": board_id, "limit": 100}),
            ("board_access", f"boards/{board_id}/access/me", "GET", None),
        ])
    return endpoints


def summarize_probe_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_label: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_label.setdefault(row["label"], []).append(row)

    summary: dict[str, dict[str, Any]] = {}
    for label, group in by_label.items():
        ok_times = [r["elapsed_ms"] for r in group if r.get("status") == 200]
        summary[label] = {
            "count": len(group),
            "avg_ms": statistics.mean(ok_times) if ok_times else None,
            "p95_ms": (
                sorted(ok_times)[int(len(ok_times) * 0.95)]
                if len(ok_times) > 1
                else (ok_times[0] if ok_times else None)
            ),
            "x_cache": [r.get("x_cache") for r in group if r.get("x_cache")],
            "sla_failures": sum(1 for r in group if not r.get("sla_ok", True)),
        }
    return summary


def cache_invalidation_ok(before_cache: str, after_cache: str) -> tuple[bool, str]:
    """After a write, the next kanban read should miss cache."""
    if before_cache.upper() != "HIT":
        return False, f"expected warm HIT before write, got {before_cache or 'missing'}"
    if after_cache.upper() != "MISS":
        return False, f"expected MISS after write, got {after_cache or 'missing'}"
    return True, ""
