from django.core.exceptions import PermissionDenied


ARANCIA_DEV_GROUP = 'arancia_DEV'


def user_is_arancia_dev(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=ARANCIA_DEV_GROUP).exists()


def require_arancia_dev(user) -> None:
    if not user_is_arancia_dev(user):
        raise PermissionDenied
