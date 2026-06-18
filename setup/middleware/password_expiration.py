from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from django.utils import timezone

from setup.middleware.password_expiration_session import (
    SESSION_WARNING_DATE_KEY,
    get_password_expiration_state,
    sync_password_expiration_session,
)


class PasswordExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            try:
                view_name = resolve(request.path_info).view_name
            except Resolver404:
                view_name = ""

            rotas_liberadas = {
                "logistica:settings",
                "logistica:logout",
                "logout",
                "admin:logout",
            }

            state = get_password_expiration_state(request)
            if state is None:
                state = sync_password_expiration_session(request)

            if state["is_expired"] and view_name not in rotas_liberadas:
                return redirect("logistica:settings")

            if state["should_warn"]:
                hoje = timezone.localdate().isoformat()

                if request.session.get(SESSION_WARNING_DATE_KEY) != hoje:
                    dias = state["days_to_expire"]

                    if dias == 1:
                        texto = "Sua senha vence em 1 dia. Recomendamos alterar sua senha."
                    else:
                        texto = f"Sua senha vence em {dias} dias. Recomendamos alterar sua senha."

                    messages.warning(request, texto)
                    request.session[SESSION_WARNING_DATE_KEY] = hoje
                    request.session.modified = True

        return self.get_response(request)
