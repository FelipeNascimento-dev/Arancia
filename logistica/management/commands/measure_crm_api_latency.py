"""Diagnóstico de latência da API CRM FastAPI (Fase 6).

Mede tempo de resposta direto nos endpoints críticos, sem passar pelo Django BFF.
Útil para confirmar se o gargalo está na API externa (hg-api-crm).
"""

from __future__ import annotations

import time
from uuid import UUID

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from crm_api.context import build_bff_headers, build_crm_headers
from crm_api.probe_helpers import (
    SLOW_THRESHOLD_MS,
    build_probe_endpoints,
    capture_instrumentation_headers,
    format_probe_row,
    sla_met,
    summarize_probe_rows,
)


class Command(BaseCommand):
    help = (
        "Mede latência direta da API CRM FastAPI (Fase 6). "
        "Requer credenciais de usuário operacional com acesso CRM."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            required=True,
            help="Usuário ARC com acesso CRM (X-Acting-User em modo Bearer)",
        )
        parser.add_argument(
            "--password",
            default=None,
            help="Senha (obrigatório apenas com --legacy-basic)",
        )
        parser.add_argument(
            "--legacy-basic",
            action="store_true",
            help="Usar Basic Auth + X-API-Key (modo legado) em vez de Bearer",
        )
        parser.add_argument(
            "--repeat",
            type=int,
            default=3,
            help="Repetições por endpoint (default: 3)",
        )
        parser.add_argument(
            "--board-id",
            default=None,
            help="UUID do board para probes extras (legado ou kanban bundle)",
        )
        parser.add_argument(
            "--include-aggregates",
            action="store_true",
            help=(
                "Inclui endpoints agregados: board-page, kanban, dashboard/summary, "
                "lookups/billing"
            ),
        )
        parser.add_argument(
            "--compare-lookups-cache",
            action="store_true",
            help="Executa /lookups/crm duas vezes para comparar X-Cache cold vs warm",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        legacy_basic = options["legacy_basic"]
        repeat = max(1, options["repeat"])
        board_id = options["board_id"]
        include_aggregates = options["include_aggregates"]
        compare_lookups_cache = options["compare_lookups_cache"]

        if board_id:
            try:
                board_id = str(UUID(board_id))
            except ValueError as exc:
                raise CommandError(f"--board-id inválido (esperado UUID): {board_id}") from exc

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"Usuário '{username}' não encontrado.") from exc

        base = getattr(settings, "CRM_API_BASE_URL", "").rstrip("/")
        v1 = getattr(settings, "CRM_API_V1_STR", "/api/v1")
        api_base = f"{base}{v1}"
        if not base:
            raise CommandError("CRM_API_BASE_URL não configurado.")

        timeout = float(getattr(settings, "CRM_API_TIMEOUT", 30))
        verify_ssl = getattr(settings, "CRM_API_VERIFY_SSL", False)

        if legacy_basic:
            if not password:
                raise CommandError("--password é obrigatório com --legacy-basic.")
            headers = build_crm_headers(user=user, password=password)
            auth_mode = "legacy_basic"
        else:
            headers = build_bff_headers(username=username)
            auth_mode = "bearer"

        endpoints = build_probe_endpoints(
            board_id,
            include_aggregates=include_aggregates,
        )
        all_rows: list[dict] = []

        with httpx.Client(timeout=timeout, verify=verify_ssl) as client:
            if compare_lookups_cache:
                self.stdout.write("\n[cache] Comparação 1ª vs 2ª execução de lookups/crm")
                for run_idx in (1, 2):
                    row = self._probe_once(
                        client,
                        api_base,
                        "lookups_crm_warm" if run_idx > 1 else "lookups_crm",
                        "lookups/crm",
                        "GET",
                        None,
                        headers,
                    )
                    all_rows.append(row)
                    self.stdout.write(
                        f"  run {run_idx}: {format_probe_row(row['label'], status=row['status'], elapsed_ms=row['elapsed_ms'], instr_headers=row['instr_headers'], error=row['error'], path=row['path'])}"
                    )

            for repeat_idx in range(1, repeat + 1):
                self.stdout.write(f"\n[repeat {repeat_idx}/{repeat}]")
                for label, path, method, params in endpoints:
                    if label == "lookups_crm" and compare_lookups_cache:
                        continue
                    row = self._probe_once(
                        client,
                        api_base,
                        label,
                        path,
                        method,
                        params,
                        headers,
                    )
                    all_rows.append(row)
                    self.stdout.write(f"  {format_probe_row(row['label'], status=row['status'], elapsed_ms=row['elapsed_ms'], instr_headers=row['instr_headers'], error=row['error'], path=row['path'])}")

        self._print_summary(api_base, auth_mode, all_rows)
        self._print_recommendations(all_rows, legacy_basic=legacy_basic)

    def _probe_once(
        self,
        client: httpx.Client,
        api_base: str,
        label: str,
        path: str,
        method: str,
        params: dict | None,
        headers: dict,
    ) -> dict:
        url = f"{api_base}/{path}" if path else api_base
        started = time.perf_counter()
        status = 0
        error = ""
        instr_headers: dict[str, str] = {}
        try:
            response = client.request(
                method.upper(),
                url,
                headers=headers,
                params=params,
            )
            status = response.status_code
            instr_headers = capture_instrumentation_headers(response)
            if response.status_code >= 400:
                error = response.text[:120]
        except httpx.RequestError as exc:
            error = str(exc)
        elapsed_ms = (time.perf_counter() - started) * 1000
        x_cache = instr_headers.get("X-Cache", "")
        sla_ok, _ = sla_met(label, elapsed_ms, x_cache=x_cache) if status == 200 else (True, "")
        return {
            "label": label,
            "status": status,
            "elapsed_ms": elapsed_ms,
            "instr_headers": instr_headers,
            "x_cache": x_cache,
            "error": error,
            "path": path,
            "sla_ok": sla_ok,
        }

    def _print_summary(self, api_base: str, auth_mode: str, rows: list[dict]) -> None:
        self.stdout.write("")
        self.stdout.write(f"API CRM: {api_base}")
        self.stdout.write(f"Auth mode: {auth_mode}")
        self.stdout.write("")
        self.stdout.write(
            f"{'endpoint':<20} {'HTTP':>4} {'avg_ms':>10} {'p95_ms':>10} {'SLA':>6}  X-Cache"
        )
        self.stdout.write("-" * 90)
        summary = summarize_probe_rows(rows)
        for label, stats in summary.items():
            avg = stats["avg_ms"]
            p95 = stats["p95_ms"]
            sla_fail = stats["sla_failures"]
            cache_vals = stats.get("x_cache") or []
            cache_note = ",".join(cache_vals) if cache_vals else "-"
            avg_s = f"{avg:.1f}" if avg is not None else "-"
            p95_s = f"{p95:.1f}" if p95 is not None else "-"
            sla_mark = "FAIL" if sla_fail else "OK"
            self.stdout.write(
                f"{label:<20} {'':>4} {avg_s:>10} {p95_s:>10} {sla_mark:>6}  {cache_note}"
            )

    def _print_recommendations(self, rows: list[dict], *, legacy_basic: bool) -> None:
        slow = [
            r for r in rows
            if r["status"] == 200 and r["elapsed_ms"] >= SLOW_THRESHOLD_MS
        ]
        sla_failed = [r for r in rows if r.get("status") == 200 and not r.get("sla_ok", True)]

        self.stdout.write("")
        if sla_failed:
            self.stdout.write(self.style.ERROR("SLA failures:"))
            for row in sla_failed:
                self.stdout.write(
                    f"  • {row['label']}: {row['elapsed_ms']:.0f} ms "
                    f"(X-Cache={row.get('x_cache') or '-'})"
                )
            self.stdout.write("")

        if not slow and not sla_failed:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Todos os endpoints respondem em < {SLOW_THRESHOLD_MS} ms "
                    "e dentro das metas de SLA configuradas."
                )
            )
            return

        if slow:
            self.stdout.write(self.style.WARNING("Diagnóstico Fase 6 — API CRM lenta:"))
            for row in slow:
                self.stdout.write(
                    f"  • {row['label']}: {row['elapsed_ms']:.0f} ms médio "
                    f"(threshold geral < {SLOW_THRESHOLD_MS} ms)"
                )
        self.stdout.write("")
        self.stdout.write("Checklist no backend FastAPI (hg-api-crm):")
        self.stdout.write("  1. Logar queries SQL dos endpoints de lookup (N+1 / full scan)")
        self.stdout.write("  2. Verificar índices em status_tasks, boards, tasks, designations")
        if legacy_basic:
            self.stdout.write("  3. Medir custo do middleware de auth (Basic + API key)")
        else:
            self.stdout.write(
                "  3. Medir custo do middleware de auth "
                "(Bearer + X-Acting-User — meta < 10 ms)"
            )
        self.stdout.write("  4. Conferir pool SQLAlchemy e proxy nginx → uvicorn")
        self.stdout.write("  5. Cache Redis nos bundles (/lookups/*, /boards/{id}/kanban)")
        self.stdout.write(
            "  6. Após PATCH /tasks/{id}/move, próximo GET kanban deve retornar X-Cache: MISS"
        )
        self.stdout.write("")
        self.stdout.write(
            "Mitigação Django: CRM_USE_AGGREGATED_ENDPOINTS=true + cache Redis BFF "
            "(ver CRM_LOOKUPS_REDIS_CACHE_TTL em settings)."
        )
