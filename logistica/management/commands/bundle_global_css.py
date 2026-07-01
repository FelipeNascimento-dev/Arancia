"""Concatena CSS globais em um único arquivo (evita 20+ @import sequenciais)."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

CSS_DIR = Path(settings.BASE_DIR) / "base_static" / "global" / "css"

PARTIALS = [
    "layout-tokens.css",
    "content-shell.css",
    "navbar.css",
    "login.css",
    "logout.css",
    "register.css",
    "form_3col.css",
    "form_2col.css",
    "form_1col.css",
    "form_card_2col.css",
    "button_1b.css",
    "button_2b.css",
    "consulta_id.css",
    "pagination.css",
    "barra_progresso.css",
    "nav_usuario.css",
    "trackingIP.css",
    "configuracao_user.css",
    "user_ger.css",
    "skill_ger.css",
    "dinamic_table.css",
    "responsividade.css",
    "campo.css",
    "crm_task_detail.css",
    "ferramentas.css",
    "mural.css",
    "mural_gerenciamento.css",
    "detalhe_os.css",
    "detalhe_os_chamados.css",
    "detalhe_viagem.css",
    "arancia_message_iframe.css",
    "acompanhamento_iframe.css",
]


class Command(BaseCommand):
    help = "Gera base_static/global/css/style.bundle.css a partir dos parciais."

    def handle(self, *args, **options):
        style_path = CSS_DIR / "style.css"
        bundle_path = CSS_DIR / "style.bundle.css"

        style_text = style_path.read_text(encoding="utf-8")
        body_start = style_text.find(":root {")
        if body_start == -1:
            self.stderr.write("Não encontrou bloco :root em style.css")
            return

        chunks = [
            "/* Gerado por bundle_global_css — não editar manualmente */\n",
            style_text[body_start:],
        ]

        for name in PARTIALS:
            path = CSS_DIR / name
            chunks.append(f"\n/* --- {name} --- */\n")
            chunks.append(path.read_text(encoding="utf-8"))

        bundle_path.write_text("".join(chunks), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Bundle escrito em {bundle_path}"))
