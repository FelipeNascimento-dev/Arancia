from celery import shared_task

from logistica.utils.user_inactive import desativar_usuarios_inativos


@shared_task
def deactivate_inactive_users():
    count = desativar_usuarios_inativos(dias_inatividade=30)

    return f"{count} usuários desativados por inatividade."
