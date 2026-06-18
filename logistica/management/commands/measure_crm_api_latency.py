"""Diagnóstico de latência da API CRM FastAPI (Fase 6A).

Mede tempo de resposta direto nos endpoints críticos, sem passar pelo Django BFF.
Útil para confirmar se o gargalo está na API externa (hg-api-crm).
"""

from __future__ import annotations

import statistics
import time

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from crm_api.context import build_crm_headers

# Endpoints críticos identificados no plano de performance
PROBE_ENDPOINTS = [
    ("health", "", "GET"),
    ("lookups_crm", "lookups/crm", "GET"),
    ("lookups_gais", "lookups/gais", "GET"),
    ("me_context", "me/context", "GET"),
    ("boards_list", "boards/", "GET"),
]

SLOW_THRESHOLD_MS = 500


class Command(BaseCommand):
    help = (
        "Mede latência direta da API CRM FastAPI (Fase 6A). "
        "Requer credenciais de usuário operacional com acesso CRM."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            required=True,
            help="Usuário ARC com acesso CRM",
        )
        parser.add_argument(
            "--password",
            required=True,
            help="Senha (Basic Auth CRM)",
        )
        parser.add_argument(
            "--repeat",
            type=int,
            default=3,
            help="Repetições por endpoint (default: 3)",
        )
        parser.add_argument(
            "--board-id",
            type=int,
            default=None,
            help="ID de board para probes extras (columns, tasks, access)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        repeat = max(1, options["repeat"])
        board_id = options["board_id"]

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

        headers = build_crm_headers(user=user, password=password)

        endpoints = list(PROBE_ENDPOINTS)
        if board_id is not None:
            endpoints.extend([
                ("board_detail", f"boards/{board_id}", "GET"),
                ("board_columns", f"boards/{board_id}/columns", "GET"),
                ("board_tasks", "tasks/", "GET"),
                ("board_access", f"boards/{board_id}/access/me", "GET"),
            ])

        rows = []
        with httpx.Client(timeout=timeout, verify=verify_ssl) as client:
            for label, path, method in endpoints:
                url = f"{api_base}/{path}" if path else api_base
                params = None
                if label == "board_tasks":
                    params = {"board_id": board_id, "limit": 100}

                samples_ms = []
                status = 0
                error = ""
                for _ in range(repeat):
                    started = time.perf_counter()
                    try:
                        response = client.request(
                            method.upper(),
                            url,
                            headers=headers,
                            params=params,
                        )
                        status = response.status_code
                        if response.status_code >= 400:
                            error = response.text[:120]
                    except httpx.RequestError as exc:
                        error = str(exc)
                        status = 0
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    samples_ms.append(elapsed_ms)

                avg_ms = statistics.mean(samples_ms) if samples_ms else 0.0
                p95_ms = (
                    sorted(samples_ms)[int(len(samples_ms) * 0.95)]
                    if len(samples_ms) > 1
                    else avg_ms
                )
                rows.append({
                    "label": label,
                    "url": url,
                    "status": status,
                    "avg_ms": avg_ms,
                    "p95_ms": p95_ms,
                    "error": error,
                })

        self._print_results(api_base, rows)
        self._print_recommendations(rows)

    def _print_results(self, api_base: str, rows: list[dict]) -> None:
        self.stdout.write("")
        self.stdout.write(f"API CRM: {api_base}")
        self.stdout.write("")
        self.stdout.write(
            f"{'endpoint':<18} {'HTTP':>4} {'avg_ms':>10} {'p95_ms':>10}  path"
        )
        self.stdout.write("-" * 80)
        for row in rows:
            path = row["url"].replace(api_base.rstrip("/"), "").lstrip("/") or "/"
            self.stdout.write(
                f"{row['label']:<18} {row['status']:>4} {row['avg_ms']:>10.1f} "
                f"{row['p95_ms']:>10.1f}  /{path}"
            )
            if row["error"]:
                self.stdout.write(self.style.WARNING(f"  erro: {row['error'][:100]}"))

    def _print_recommendations(self, rows: list[dict]) -> None:
        slow = [r for r in rows if r["avg_ms"] >= SLOW_THRESHOLD_MS and r["status"] < 500]
        self.stdout.write("")
        if not slow:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Todos os endpoints respondem em < {SLOW_THRESHOLD_MS} ms — "
                    "gargalo provavelmente não está na API CRM."
                )
            )
            return

        self.stdout.write(self.style.WARNING("Diagnóstico Fase 6A — API CRM lenta:"))
        for row in slow:
            self.stdout.write(
                f"  • {row['label']}: {row['avg_ms']:.0f} ms médio "
                f"(meta < {SLOW_THRESHOLD_MS} ms)"
            )
        self.stdout.write("")
        self.stdout.write("Checklist no backend FastAPI (hg-api-crm):")
        self.stdout.write("  1. Logar queries SQL dos endpoints de lookup (N+1 / full scan)")
        self.stdout.write("  2. Verificar índices em status_tasks, boards, tasks, designations")
        self.stdout.write("  3. Medir custo do middleware de auth (Basic + API key)")
        self.stdout.write("  4. Conferir pool SQLAlchemy e proxy nginx → uvicorn")
        self.stdout.write("  5. Cache Redis in-memory nos /lookups/* (TTL 5 min)")
        self.stdout.write("  6. Endpoints agregados: /lookups/board-page, /boards/{id}/kanban")
        self.stdout.write("")
        self.stdout.write(
            "Mitigação Django (já aplicável): cache Redis BFF + HTTP paralelo "
            "(ver CRM_LOOKUPS_REDIS_CACHE_TTL em settings)."
        )
