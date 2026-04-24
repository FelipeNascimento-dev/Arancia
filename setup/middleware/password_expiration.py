from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from django.utils import timezone

from logistica.models import UserPasswordControl


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

            control, _ = UserPasswordControl.objects.get_or_create(
                user=request.user
            )

            if control.is_password_expired() and view_name not in rotas_liberadas:
                messages.error(
                    request,
                    "Sua senha venceu. Para continuar usando o sistema, altere sua senha."
                )
                return redirect("logistica:settings")

            if control.should_warn():
                hoje = timezone.localdate().isoformat()
                session_key = "password_expiration_warning_date"

                if request.session.get(session_key) != hoje:
                    dias = control.days_to_expire()

                    if dias == 1:
                        texto = "Sua senha vence em 1 dia. Recomendamos alterar sua senha."
                    else:
                        texto = f"Sua senha vence em {dias} dias. Recomendamos alterar sua senha."

                    messages.warning(request, texto)
                    request.session[session_key] = hoje

        return self.get_response(request)
