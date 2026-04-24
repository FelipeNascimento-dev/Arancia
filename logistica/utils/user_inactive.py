from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone


def desativar_usuarios_inativos(dias_inatividade=30):
    User = get_user_model()

    cutoff_date = timezone.now() - timedelta(days=dias_inatividade)

    users_to_deactivate = User.objects.filter(
        is_active=True
    ).filter(
        Q(last_login__lt=cutoff_date) |
        Q(last_login__isnull=True, date_joined__lt=cutoff_date)
    ).exclude(
        is_superuser=True
    ).exclude(
        is_staff=True
    )

    count = users_to_deactivate.count()

    users_to_deactivate.update(is_active=False)

    return count
