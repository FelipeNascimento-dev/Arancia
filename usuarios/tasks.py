from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


@shared_task
def deactivate_inactive_users():
    User = get_user_model()
    cutoff_date = timezone.now() - timedelta(days=30)

    users_to_deactivate = User.objects.filter(
        is_active=True,
        last_login__lt=cutoff_date
    )
    count = users_to_deactivate.update(is_active=False)
    return f"{count} usuários desativados por inatividade."
