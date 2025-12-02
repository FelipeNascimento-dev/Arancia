from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class UserLoginView(LoginView):
    template_name = 'logistica/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_title"] = "Login"
        return context

    def get_success_url(self):
        user = self.request.user
        first = user.first_name or user.username
        last = user.last_name or ""
        messages.info(
            self.request,
            f"👋 Olá, {first} {last}! Seja bem-vindo ao Arancia, nossa nova plataforma de gestão."
        )
        return reverse_lazy("logistica:index")
