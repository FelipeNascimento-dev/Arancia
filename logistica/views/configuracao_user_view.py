from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from ..forms import ConfiguracaoUserForm
from ..models import UserProfile


@login_required(login_url='logistica:login')
def settings_view(request):
    perfil, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ConfiguracaoUserForm(
            request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            user = form.save()

            if form.password_changed():
                update_session_auth_hash(request, user)
                messages.success(request, "Senha alterada com sucesso.")

            foto = request.FILES.get("foto_perfil")
            if foto:
                if perfil.avatar:
                    try:
                        perfil.avatar.delete(save=False)
                    except Exception:
                        pass
                perfil.avatar.save(foto.name, foto, save=True)
                messages.success(request, "Foto atualizada com sucesso.")
            else:
                messages.info(request, "Dados atualizados.")

            return redirect("logistica:settings")
        else:
            for campo, errs in form.errors.items():
                messages.error(request, f"{campo}: {errs.as_text()}")
            messages.error(request, "Corrija os erros e tente novamente.")
    else:
        form = ConfiguracaoUserForm(instance=request.user)

    return render(request, "logistica/configuracao_user.html", {
        "form": form,
        "site_title": "Configurações",
        "avatar_url": perfil.avatar_url(),
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
