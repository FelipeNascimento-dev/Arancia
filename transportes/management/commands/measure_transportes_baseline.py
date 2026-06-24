"""Mede baseline de performance das listas de transportes e valida paginação da API de viagens."""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.test import Client, override_settings

from transportes.utils.baseline import (
    measure_lista_viagens_apis,
    probe_order_travel_pagination,
)


class Command(BaseCommand):
    help = (
        "Mede tempos das APIs de transportes (clientes/status, Carriers/list, order_travel/list) "
        "e valida suporte a offset/limit+total. Opcionalmente mede views Django com login."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            help="Usuário com transportes.ver_transportes (para medir views Django)",
        )
        parser.add_argument(
            "--password",
            help="Senha do usuário (obrigatória com --username)",
        )
        parser.add_argument(
            "--repeat",
            type=int,
            default=1,
            help="Repetições por medição de API (default: 1)",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=100,
            help="Timeout HTTP em segundos (default: 100)",
        )
        parser.add_argument(
            "--skip-views",
            action="store_true",
            help="Não medir views Django (somente APIs diretas)",
        )

    def handle(self, *args, **options):
        username = options.get("username")
        password = options.get("password")
        repeat = max(1, options["repeat"])
        timeout = options["timeout"]
        skip_views = options["skip_views"]

        if bool(username) ^ bool(password):
            raise CommandError("Informe --username e --password juntos para medir views.")

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("=== APIs diretas (Lista de Viagens) ==="))
        self._print_api_table(repeat, timeout)

        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("=== Validação paginação order_travel/list ==="))
        self._print_pagination_probe(timeout)

        if not skip_views and username and password:
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING("=== Views Django (com login) ==="))
            self._print_view_table(username, password, repeat)

        self.stdout.write("")
        self.stdout.write(
            "Dica: defina PERFORMANCE_INSTRUMENTATION=True em local_settings.py "
            "para logs TRANS_PERF por fase em lista_viagens no runserver."
        )

    def _print_api_table(self, repeat: int, timeout: int) -> None:
        aggregated: dict[str, list] = {}
        for _ in range(repeat):
            for row in measure_lista_viagens_apis(timeout=timeout):
                aggregated.setdefault(row.name, []).append(row)

        self.stdout.write(
            f"{'endpoint':<22} {'ms':>10} {'items':>8} {'tipo':<14} status"
        )
        self.stdout.write("-" * 62)
        for name, rows in aggregated.items():
            avg_ms = sum(r.elapsed_ms for r in rows) / len(rows)
            last = rows[-1]
            status = "ERR" if last.error else "OK"
            self.stdout.write(
                f"{name:<22} {avg_ms:>10.1f} {last.payload_size:>8} "
                f"{last.response_type:<14} {status}"
            )
            if last.error:
                self.stdout.write(f"  erro: {last.error}")

    def _print_pagination_probe(self, timeout: int) -> None:
        probe = probe_order_travel_pagination(timeout=timeout)
        self.stdout.write(f"Formato resposta     : {probe.response_shape}")
        self.stdout.write(
            f"offset/limit OK      : {'sim' if probe.supports_offset_limit else 'não'}"
        )
        self.stdout.write(
            f"Campo total          : "
            f"{'sim (' + probe.total_field_name + ')' if probe.has_total_field else 'não'}"
        )
        if probe.total_reported is not None:
            self.stdout.write(f"Total reportado      : {probe.total_reported}")
        self.stdout.write(f"Itens página 0       : {probe.page0_count}")
        self.stdout.write(f"Itens página 1       : {probe.page1_count}")
        self.stdout.write(
            f"IDs distintos p0/p1  : {'sim' if probe.distinct_ids_page0_vs_page1 else 'não'}"
        )
        for note in probe.notes:
            self.stdout.write(f"  nota: {note}")

    def _print_view_table(self, username: str, password: str, repeat: int) -> None:
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            raise CommandError(f"Usuário '{username}' não encontrado.")

        base_path = getattr(settings, "BASE_PATH", "") or ""
        prefix = f"/{base_path.rstrip('/')}" if base_path else ""

        view_paths = [
            ("lista_viagens", f"{prefix}/transportes/lista-viagens/"),
            ("consulta_os_transp", f"{prefix}/transportes/consulta-os-transp/"),
        ]

        with override_settings(PERFORMANCE_INSTRUMENTATION=True):
            client = Client()
            if not client.login(username=username, password=password):
                raise CommandError("Falha no login — verifique usuário e senha.")

            self.stdout.write(
                f"{'view':<22} {'HTTP':>4} {'total_ms':>10} "
                f"{'transp_http':>12} {'transp_ms':>10}  path"
            )
            self.stdout.write("-" * 90)

            for label, url in view_paths:
                totals = []
                for _ in range(repeat):
                    response = client.get(url)
                    headers = response.headers
                    totals.append({
                        "status": response.status_code,
                        "total_ms": self._float_header(headers.get("X-Request-Time-Ms")),
                        "transp_http": self._int_header(
                            headers.get("X-Transp-HTTP-Calls")
                        ),
                        "transp_ms": self._float_header(
                            headers.get("X-Transp-HTTP-Time-Ms")
                        ),
                    })

                n = len(totals) or 1
                avg = {
                    "status": totals[-1]["status"],
                    "total_ms": sum(t["total_ms"] for t in totals) / n,
                    "transp_http": sum(t["transp_http"] for t in totals) / n,
                    "transp_ms": sum(t["transp_ms"] for t in totals) / n,
                }
                self.stdout.write(
                    f"{label:<22} {int(avg['status']):>4} {avg['total_ms']:>10.1f} "
                    f"{avg['transp_http']:>12.0f} {avg['transp_ms']:>10.1f}  {url}"
                )

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
