from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash

from ..forms import ConfiguracaoUserForm


@login_required(login_url='logistica:login')
def settings_view(request):
    if request.method == "POST":
        form = ConfiguracaoUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados atualizados com sucesso.")
            return redirect("logistica:settings")
        else:
            messages.error(request, "Corrija os erros e tente novamente.")
    else:
        form = ConfiguracaoUserForm(instance=request.user)

    return render(request, "logistica/configuracao_user.html", {
        "form": form,
        "site_title": "Configurações",
    })


class UserPasswordChangeView(PasswordChangeView):
    template_name = "logistica/password_change.html"
    success_url = reverse_lazy("logistica:settings")

    def form_valid(self, form):
        response = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Senha alterada com sucesso.")
        return response

    def form_invalid(self, form):
        messages.error(
            self.request, "Não foi possível alterar a senha. Verifique os dados.")
        return super().form_invalid(form)
