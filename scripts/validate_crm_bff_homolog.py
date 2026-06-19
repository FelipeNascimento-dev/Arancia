"""Homolog deploy validation — smoke, bundles, SLA and cache invalidation (Fase 6).

Usage:
    python scripts/validate_crm_bff_homolog.py [--username ARC0000] [--legacy-basic]
    python scripts/validate_crm_bff_homolog.py --bundles-only
    python scripts/validate_crm_bff_homolog.py --skip-cache-invalidation

Secrets are read from Django settings; nothing is printed to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

import django

django.setup()

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from crm_api.bundle_contracts import (
    validate_billing_lookups_response,
    validate_board_page_response,
    validate_dashboard_summary_response,
    validate_kanban_bundle_response,
)
from crm_api.context import build_bff_headers, build_crm_headers, build_scheduler_headers
from crm_api.probe_helpers import (
    DASHBOARD_SLA_MS,
    KANBAN_SLA_MS,
    cache_invalidation_ok,
    capture_instrumentation_headers,
    sla_met,
)
from crm_api.services.boards import resolve_board_id_from_page

HOMOLOG_CRM_BASE = "http://192.168.0.214/hg-api-crm"

SMOKE_CHECKS = [
    ("lookups_crm", "GET", "lookups/crm", "bff"),
    ("lookups_gais", "GET", "lookups/gais", "bff"),
    ("me_context", "GET", "me/context", "bff"),
    ("boards_list", "GET", "boards/", "bff"),
    ("scheduler", "POST", "internal/scheduler/generate-due-tasks", "scheduler"),
]

BUNDLE_CHECKS = [
    ("board_page", "GET", "lookups/board-page", validate_board_page_response, {"gais_limit": 50}),
    ("billing_lookups", "GET", "lookups/billing", validate_billing_lookups_response, None),
    ("dashboard_summary", "GET", "dashboard/summary", validate_dashboard_summary_response, None),
]


def _headers(mode: str, *, username: str, password: str | None):
    if mode == "bff":
        return build_bff_headers(username=username)
    if mode == "scheduler":
        return build_scheduler_headers()
    if mode == "legacy":
        user = get_user_model().objects.get(username=username)
        return build_crm_headers(user=user, password=password or "")
    raise ValueError(mode)


def _request(client: httpx.Client, api_v1: str, method: str, path: str, headers: dict, *, params=None):
    url = f"{api_v1}/{path.lstrip('/')}"
    return client.request(method.upper(), url, headers=headers, params=params)


def _parse_json(response: httpx.Response) -> dict | list | None:
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        return None


def run_smoke(*, username: str, password: str | None, legacy_basic: bool) -> list[dict]:
    api_v1 = f"{HOMOLOG_CRM_BASE}{settings.CRM_API_V1_STR}"
    rows = []
    with httpx.Client(timeout=float(settings.CRM_API_TIMEOUT), verify=settings.CRM_API_VERIFY_SSL) as client:
        for label, method, path, auth_mode in SMOKE_CHECKS:
            if legacy_basic and auth_mode == "bff":
                headers = _headers("legacy", username=username, password=password)
            elif auth_mode == "bff":
                headers = _headers("bff", username=username, password=None)
            else:
                headers = _headers("scheduler", username=username, password=None)

            started = time.perf_counter()
            try:
                response = _request(client, api_v1, method, path, headers)
                status = response.status_code
                error = response.text[:120] if status >= 400 else ""
            except httpx.RequestError as exc:
                status = 0
                error = str(exc)
            elapsed_ms = (time.perf_counter() - started) * 1000
            rows.append({
                "label": label,
                "status": status,
                "elapsed_ms": elapsed_ms,
                "error": error,
            })
    return rows


def run_bundle_smoke(*, username: str) -> list[dict]:
    """Bearer smoke on aggregated bundles + JSON shape validation."""
    api_v1 = f"{HOMOLOG_CRM_BASE}{settings.CRM_API_V1_STR}"
    headers = build_bff_headers(username=username)
    rows = []
    board_id = None

    with httpx.Client(timeout=float(settings.CRM_API_TIMEOUT), verify=settings.CRM_API_VERIFY_SSL) as client:
        for label, method, path, validator, params in BUNDLE_CHECKS:
            started = time.perf_counter()
            shape_errors: list[str] = []
            cache_header = ""
            try:
                response = _request(client, api_v1, method, path, headers, params=params)
                status = response.status_code
                cache_header = response.headers.get("X-Cache", "")
                error = response.text[:120] if status >= 400 else ""
                if status == 200:
                    payload = _parse_json(response)
                    if not isinstance(payload, dict):
                        shape_errors.append("response must be JSON object")
                    else:
                        shape_errors = validator(payload)
                        if label == "board_page" and not shape_errors:
                            board_id = resolve_board_id_from_page(payload)
                            if not board_id:
                                shape_errors.append("crm.boards missing CRM_COMERCIAL_BOARD_CODE")
            except httpx.RequestError as exc:
                status = 0
                error = str(exc)
            else:
                if status == 200 and not error:
                    error = ""

            elapsed_ms = (time.perf_counter() - started) * 1000
            rows.append({
                "label": label,
                "status": status,
                "elapsed_ms": elapsed_ms,
                "error": error,
                "shape_errors": shape_errors,
                "x_cache": cache_header,
            })

        if board_id:
            label = "kanban_bundle"
            path = f"boards/{board_id}/kanban"
            started = time.perf_counter()
            shape_errors = []
            cache_header = ""
            try:
                response = _request(
                    client,
                    api_v1,
                    "GET",
                    path,
                    headers,
                    params={"task_limit": 100},
                )
                status = response.status_code
                cache_header = response.headers.get("X-Cache", "")
                error = response.text[:120] if status >= 400 else ""
                if status == 200:
                    payload = _parse_json(response)
                    if not isinstance(payload, dict):
                        shape_errors.append("response must be JSON object")
                    else:
                        shape_errors = validate_kanban_bundle_response(payload)
            except httpx.RequestError as exc:
                status = 0
                error = str(exc)
            elapsed_ms = (time.perf_counter() - started) * 1000
            rows.append({
                "label": label,
                "status": status,
                "elapsed_ms": elapsed_ms,
                "error": error,
                "shape_errors": shape_errors,
                "x_cache": cache_header,
                "board_id": str(board_id),
            })
        else:
            rows.append({
                "label": "kanban_bundle",
                "status": 0,
                "elapsed_ms": 0,
                "error": "skipped — board_id not resolved from board_page",
                "shape_errors": ["board_id unresolved"],
                "x_cache": "",
            })

    return rows


def run_bundle_sla_probe(*, username: str, board_id: str, repeat: int = 3) -> list[dict]:
    """Warm latency probe on aggregated kanban + dashboard (acceptance SLAs)."""
    api_v1 = f"{HOMOLOG_CRM_BASE}{settings.CRM_API_V1_STR}"
    headers = build_bff_headers(username=username)
    targets = [
        ("kanban_bundle", "GET", f"boards/{board_id}/kanban", {"task_limit": 100}),
        ("dashboard_summary", "GET", "dashboard/summary", None),
    ]
    rows = []
    with httpx.Client(timeout=float(settings.CRM_API_TIMEOUT), verify=settings.CRM_API_VERIFY_SSL) as client:
        for label, method, path, params in targets:
            samples = []
            status = 0
            x_cache = ""
            for _ in range(repeat):
                started = time.perf_counter()
                response = _request(client, api_v1, method, path, headers, params=params)
                status = response.status_code
                x_cache = response.headers.get("X-Cache", x_cache)
                samples.append((time.perf_counter() - started) * 1000)
            avg_ms = statistics.mean(samples)
            p95_ms = sorted(samples)[int(len(samples) * 0.95)] if len(samples) > 1 else samples[0]
            sla_ok, sla_reason = sla_met(label, avg_ms, x_cache=x_cache)
            rows.append({
                "label": label,
                "status": status,
                "avg_ms": avg_ms,
                "p95_ms": p95_ms,
                "x_cache": x_cache,
                "sla_ok": sla_ok and status == 200,
                "sla_reason": sla_reason,
                "sla_ms": KANBAN_SLA_MS if label == "kanban_bundle" else DASHBOARD_SLA_MS,
            })
    return rows


def run_cache_invalidation_check(
    *,
    username: str,
    board_id: str,
) -> dict:
    """After PATCH move, next kanban GET must return X-Cache: MISS."""
    api_v1 = f"{HOMOLOG_CRM_BASE}{settings.CRM_API_V1_STR}"
    headers = build_bff_headers(username=username)
    kanban_path = f"boards/{board_id}/kanban"
    result = {
        "label": "cache_invalidation",
        "ok": False,
        "detail": "",
        "before_cache": "",
        "after_cache": "",
    }

    with httpx.Client(timeout=float(settings.CRM_API_TIMEOUT), verify=settings.CRM_API_VERIFY_SSL) as client:
        warm = _request(
            client,
            api_v1,
            "GET",
            kanban_path,
            headers,
            params={"task_limit": 100},
        )
        if warm.status_code != 200:
            result["detail"] = f"warm kanban failed HTTP {warm.status_code}"
            return result

        hit = _request(
            client,
            api_v1,
            "GET",
            kanban_path,
            headers,
            params={"task_limit": 100},
        )
        before_cache = hit.headers.get("X-Cache", "")
        result["before_cache"] = before_cache
        if hit.status_code != 200:
            result["detail"] = f"kanban HIT probe failed HTTP {hit.status_code}"
            return result

        payload = _parse_json(hit)
        tasks = (payload or {}).get("tasks") if isinstance(payload, dict) else None
        if not tasks:
            result["detail"] = "skipped — no tasks on board to move"
            result["ok"] = True
            return result

        task = tasks[0]
        task_id = task.get("id")
        status_id = task.get("status_id") or task.get("status_task_id")
        if not task_id or not status_id:
            result["detail"] = "skipped — task missing id/status_id"
            result["ok"] = True
            return result

        move_response = client.patch(
            f"{api_v1}/tasks/{task_id}/move",
            headers=headers,
            json={
                "status_id": status_id,
                "kanban_position": task.get("kanban_position", 0),
                "board_id": board_id,
            },
        )
        if move_response.status_code >= 400:
            result["detail"] = f"PATCH move failed HTTP {move_response.status_code}"
            return result

        miss = _request(
            client,
            api_v1,
            "GET",
            kanban_path,
            headers,
            params={"task_limit": 100},
        )
        after_cache = miss.headers.get("X-Cache", "")
        result["after_cache"] = after_cache
        if miss.status_code != 200:
            result["detail"] = f"post-write kanban failed HTTP {miss.status_code}"
            return result

        ok, reason = cache_invalidation_ok(before_cache, after_cache)
        result["ok"] = ok
        result["detail"] = reason or "HIT → MISS after PATCH move"
        capture_instrumentation_headers(miss)
    return result


def run_latency_probe(*, username: str, repeat: int = 5) -> list[dict]:
    api_v1 = f"{HOMOLOG_CRM_BASE}{settings.CRM_API_V1_STR}"
    headers = build_bff_headers(username=username)
    targets = [("lookups_crm", "GET", "lookups/crm"), ("me_context", "GET", "me/context")]
    rows = []
    with httpx.Client(timeout=float(settings.CRM_API_TIMEOUT), verify=settings.CRM_API_VERIFY_SSL) as client:
        for label, method, path in targets:
            samples = []
            status = 0
            for _ in range(repeat):
                started = time.perf_counter()
                response = _request(client, api_v1, method, path, headers)
                status = response.status_code
                samples.append((time.perf_counter() - started) * 1000)
            rows.append({
                "label": label,
                "status": status,
                "avg_ms": statistics.mean(samples),
                "p95_ms": sorted(samples)[int(len(samples) * 0.95)] if len(samples) > 1 else samples[0],
            })
    return rows


def _bundle_passed(row: dict) -> bool:
    return row["status"] == 200 and not row.get("shape_errors")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CRM BFF Bearer auth on homolog")
    parser.add_argument("--username", default="ARC0000")
    parser.add_argument("--password", default=None, help="Required with --legacy-basic")
    parser.add_argument("--legacy-basic", action="store_true")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--bundles-only", action="store_true")
    parser.add_argument(
        "--skip-cache-invalidation",
        action="store_true",
        help="Não executa PATCH move + verificação X-Cache MISS",
    )
    args = parser.parse_args()

    auth_mode = "legacy_basic" if args.legacy_basic else "bearer"
    if args.legacy_basic and not args.password:
        print("ERROR: --password required with --legacy-basic", file=sys.stderr)
        return 2

    print("=== CRM BFF homolog validation ===")
    print(f"API: {HOMOLOG_CRM_BASE}")
    print(f"Auth mode: {auth_mode}")
    print(f"Acting user: {args.username}")
    print()

    bundle_passed = 0
    bundle_total = 0
    sla_ok = True
    cache_ok = True
    resolved_board_id = None

    if not args.legacy_basic:
        with override_settings(CRM_API_BASE_URL=HOMOLOG_CRM_BASE):
            bundles = run_bundle_smoke(username=args.username)

        print("Aggregated bundle smoke (Bearer):")
        for row in bundles:
            bundle_total += 1
            ok = _bundle_passed(row)
            bundle_passed += int(ok)
            if row.get("board_id"):
                resolved_board_id = row["board_id"]
            mark = "PASS" if ok else "FAIL"
            cache = f" X-Cache={row['x_cache']}" if row.get("x_cache") else ""
            extra = f" board={row['board_id']}" if row.get("board_id") else ""
            print(
                f"  [{mark}] {row['label']}: HTTP {row['status']} "
                f"({row['elapsed_ms']:.1f} ms){cache}{extra}"
            )
            if row.get("error"):
                print(f"         {row['error'][:100]}")
            for shape_err in row.get("shape_errors") or []:
                print(f"         shape: {shape_err}")
        print(f"  Summary: {bundle_passed}/{bundle_total} bundles OK (HTTP 200 + contract shape)")
        print()

        if resolved_board_id:
            with override_settings(CRM_API_BASE_URL=HOMOLOG_CRM_BASE):
                sla_rows = run_bundle_sla_probe(
                    username=args.username,
                    board_id=resolved_board_id,
                    repeat=max(2, args.repeat),
                )
            print(f"Bundle SLA probe (warm, repeat={max(2, args.repeat)}):")
            for row in sla_rows:
                mark = "PASS" if row["sla_ok"] else "FAIL"
                sla_ok = sla_ok and row["sla_ok"]
                cache = f" X-Cache={row['x_cache']}" if row.get("x_cache") else ""
                print(
                    f"  [{mark}] {row['label']}: avg={row['avg_ms']:.1f} ms "
                    f"p95={row['p95_ms']:.1f} ms HTTP {row['status']} "
                    f"(SLA < {row['sla_ms']} ms){cache}"
                )
                if row.get("sla_reason"):
                    print(f"         {row['sla_reason']}")
            print()

            if not args.skip_cache_invalidation:
                with override_settings(CRM_API_BASE_URL=HOMOLOG_CRM_BASE):
                    cache_row = run_cache_invalidation_check(
                        username=args.username,
                        board_id=resolved_board_id,
                    )
                mark = "PASS" if cache_row["ok"] else "FAIL"
                cache_ok = cache_row["ok"]
                print("Cache invalidation (write → kanban MISS):")
                print(
                    f"  [{mark}] before={cache_row['before_cache'] or '-'} "
                    f"after={cache_row['after_cache'] or '-'} — {cache_row['detail']}"
                )
                print()

        if args.bundles_only:
            return 0 if bundle_passed == bundle_total and sla_ok and cache_ok else 1

    with override_settings(CRM_API_BASE_URL=HOMOLOG_CRM_BASE):
        smoke = run_smoke(
            username=args.username,
            password=args.password,
            legacy_basic=args.legacy_basic,
        )

    print("Smoke tests:")
    passed = 0
    for row in smoke:
        ok = row["status"] in (200, 204)
        passed += int(ok)
        mark = "PASS" if ok else "FAIL"
        print(
            f"  [{mark}] {row['label']}: HTTP {row['status']} "
            f"({row['elapsed_ms']:.1f} ms)"
        )
        if row["error"]:
            print(f"         {row['error'][:100]}")
    print(f"  Summary: {passed}/{len(smoke)} HTTP 2xx")
    print()

    if not args.legacy_basic:
        with override_settings(CRM_API_BASE_URL=HOMOLOG_CRM_BASE):
            probe = run_latency_probe(username=args.username, repeat=args.repeat)
        print(f"Latency probe (Bearer, repeat={args.repeat}):")
        for row in probe:
            meta = "OK" if row["avg_ms"] < 500 else "SLOW"
            print(
                f"  {row['label']}: avg={row['avg_ms']:.1f} ms p95={row['p95_ms']:.1f} ms "
                f"HTTP {row['status']} [{meta}]"
            )
        print()
        print("FastAPI logs: confirm crm_auth_completed mode=internal_bff duration_ms < 10")
        print("(grep server logs on hg-api-crm host — not available from this script)")

    smoke_ok = passed == len(smoke)
    bundles_ok = bundle_passed == bundle_total if bundle_total else True
    return 0 if smoke_ok and bundles_ok and sla_ok and cache_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
