import sys
import logging

from django.apps import AppConfig
from django.core.cache import cache
from django.utils import timezone


logger = logging.getLogger(__name__)


class LogisticaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "logistica"

    def ready(self):
        comandos_ignorados = [
            "makemigrations",
            "migrate",
            "collectstatic",
            "shell",
            "test",
        ]

        if len(sys.argv) > 1 and sys.argv[1] in comandos_ignorados:
            return

        hoje = timezone.localdate().isoformat()
        cache_key = f"desativar_usuarios_inativos_startup_{hoje}"

        ja_rodou = cache.get(cache_key)

        if ja_rodou:
            return

        try:
            from logistica.utils.user_inactive import desativar_usuarios_inativos

            count = desativar_usuarios_inativos(dias_inatividade=30)

            cache.set(cache_key, True, timeout=60 * 60 * 24)

            logger.info(
                "Verificação de usuários inativos executada no startup. "
                f"{count} usuários desativados."
            )

        except Exception as e:
            logger.exception(
                f"Erro ao executar verificação de usuários inativos no startup: {e}"
            )
