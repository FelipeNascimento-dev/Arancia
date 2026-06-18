from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from crm.context_processors import sync_crm_module_session
from crm_api.exceptions import CrmApiError, crm_error_message_pt
from crm_api.session_credentials import store_password_in_session
from setup.middleware.password_expiration_session import sync_password_expiration_session


class UserLoginView(LoginView):
    template_name = 'logistica/templates_user/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_title"] = "Login"
        return context

    def form_valid(self, form):
        password = (form.cleaned_data.get("password") or "").strip()
        response = super().form_valid(form)

        sync_crm_module_session(self.request)

        if password and not getattr(self.request, "_crm_login_via_access_code", False):
            store_password_in_session(self.request, password)
            if self.request.user.has_module_perms("crm"):
                self._validate_crm_api_credentials()

        sync_password_expiration_session(self.request)

        return response

    def _validate_crm_api_credentials(self):
        """Avisa no login se a API CRM rejeitar username/senha (Basic + API key)."""
        try:
            from crm_api.client import CrmApiClient
            from crm_api.services.auth import get_me_context

            get_me_context(CrmApiClient(self.request))
        except CrmApiError as exc:
            messages.warning(
                self.request,
                crm_error_message_pt(exc),
            )

    def get_success_url(self):
        user = self.request.user
        first = user.first_name or user.username
        last = user.last_name or ""
        messages.info(
            self.request,
            f"👋 Olá, {first} {last}! Seja bem-vindo ao Arancia, nossa nova plataforma de gestão."
        )
        return reverse_lazy("logistica:index")
