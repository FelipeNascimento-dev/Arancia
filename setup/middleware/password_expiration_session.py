"""Cache de expiração de senha na sessão — evita get_or_create em todo request."""

from django.utils import timezone

from logistica.models import UserPasswordControl

SESSION_STATE_KEY = "password_expiration_state"
SESSION_WARNING_DATE_KEY = "password_expiration_warning_date"


def _state_from_control(control):
    return {
        "is_expired": control.is_password_expired(),
        "days_to_expire": control.days_to_expire(),
        "should_warn": control.should_warn(),
    }


def sync_password_expiration_session(request, control=None):
    """Carrega UserPasswordControl no DB e grava estado na sessão."""
    if control is None:
        control, _ = UserPasswordControl.objects.get_or_create(user=request.user)

    state = {
        "user_id": request.user.pk,
        "cached_at": timezone.localdate().isoformat(),
        **_state_from_control(control),
    }
    request.session[SESSION_STATE_KEY] = state
    request.session.modified = True
    return state


def clear_password_expiration_session(request):
    request.session.pop(SESSION_STATE_KEY, None)
    request.session.pop(SESSION_WARNING_DATE_KEY, None)
    request.session.modified = True


def get_password_expiration_state(request):
    """
    Retorna estado em cache ou None se ausente/desatualizado.
    Desatualiza 1x/dia (cached_at) ou se o user_id não bater.
    """
    state = request.session.get(SESSION_STATE_KEY)
    if not state:
        return None

    if state.get("user_id") != request.user.pk:
        return None

    if state.get("cached_at") != timezone.localdate().isoformat():
        return None

    return state
