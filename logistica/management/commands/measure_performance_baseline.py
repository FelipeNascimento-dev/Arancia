"""Mede baseline de performance em URLs representativas (Fase 0 do plano)."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.test import Client, override_settings

BASELINE_URLS = [
    ("homepage_mural", "/"),
    ("consulta_id", "/consulta-id/"),
    ("crm_dashboard", "/crm/"),
    ("kanban_comercial", "/crm/comercial/"),
    ("lista_faturamento", "/crm/billing/"),
]


class Command(BaseCommand):
    help = (
        "Mede tempo total, contagem SQL e chamadas CRM API em URLs representativas. "
        "Requer PERFORMANCE_INSTRUMENTATION=True (ativado automaticamente neste comando)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            required=True,
            help="Usuário operacional com logistica.acesso_arancia",
        )
        parser.add_argument(
            "--password",
            required=True,
            help="Senha do usuário (também usada para Basic Auth CRM)",
        )
        parser.add_argument(
            "--repeat",
            type=int,
            default=1,
            help="Repetições por URL (default: 1)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        repeat = max(1, options["repeat"])

        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            raise CommandError(f"Usuário '{username}' não encontrado.")

        base_path = getattr(settings, "BASE_PATH", "") or ""
        prefix = f"/{base_path.rstrip('/')}" if base_path else ""

        rows = []
        with override_settings(PERFORMANCE_INSTRUMENTATION=True):
            client = Client()
            login_ok = client.login(username=username, password=password)
            if not login_ok:
                raise CommandError("Falha no login — verifique usuário e senha.")

            for label, path_suffix in BASELINE_URLS:
                url = f"{prefix}{path_suffix}" if prefix else path_suffix
                totals = []
                for _ in range(repeat):
                    response = client.get(url)
                    totals.append(self._extract_metrics(response, url))

                avg = self._average_metrics(totals)
                rows.append((label, url, avg["status"], avg))

        self._print_table(rows)

    def _extract_metrics(self, response, url: str) -> dict:
        headers = response.headers
        return {
            "status": response.status_code,
            "total_ms": self._float_header(headers.get("X-Request-Time-Ms")),
            "sql": self._int_header(headers.get("X-SQL-Queries")),
            "crm_http": self._int_header(headers.get("X-CRM-HTTP-Calls")),
            "crm_ms": self._float_header(headers.get("X-CRM-HTTP-Time-Ms")),
            "url": url,
        }

    @staticmethod
    def _float_header(value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _int_header(value) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _average_metrics(self, totals: list[dict]) -> dict:
        n = len(totals) or 1
        return {
            "status": totals[-1]["status"] if totals else 0,
            "total_ms": sum(t["total_ms"] for t in totals) / n,
            "sql": sum(t["sql"] for t in totals) / n,
            "crm_http": sum(t["crm_http"] for t in totals) / n,
            "crm_ms": sum(t["crm_ms"] for t in totals) / n,
        }

    def _print_table(self, rows):
        self.stdout.write("")
        self.stdout.write(
            f"{'URL':<22} {'HTTP':>4} {'total_ms':>10} {'sql':>6} "
            f"{'crm_http':>9} {'crm_ms':>10}  path"
        )
        self.stdout.write("-" * 90)
        for label, url, status, metrics in rows:
            self.stdout.write(
                f"{label:<22} {int(status):>4} {metrics['total_ms']:>10.1f} "
                f"{metrics['sql']:>6.0f} {metrics['crm_http']:>9.0f} "
                f"{metrics['crm_ms']:>10.1f}  {url}"
            )
        self.stdout.write("")
        self.stdout.write(
            "Dica: defina PERFORMANCE_INSTRUMENTATION=True em local_settings.py "
            "para ver logs PERF em cada request no runserver."
        )
