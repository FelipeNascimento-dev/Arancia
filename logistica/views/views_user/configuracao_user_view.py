from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from utils.request import RequestClient
from ...forms import ConfiguracaoUserForm
from ...models import UserProfile
import httpx


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def settings_view(request):
    perfil, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ConfiguracaoUserForm(
            request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            user = form.save()

            foto = request.FILES.get("foto_perfil")
            if foto:
                try:
                    api_url = "http://192.168.0.214/RetencaoAPI/api/v3/upload/upload/Firebase/"
                    headers = {
                        "accept": "application/json",
                        "access_token": "123",
                    }
                    files = {"file": (foto.name, foto, foto.content_type)}

                    with httpx.Client(timeout=30) as client:
                        response = client.post(
                            api_url, headers=headers, files=files)

                    if response.status_code == 200:
                        data = response.json()
                        firebase_url = data.get("url")

                        perfil.avatar = firebase_url
                        perfil.save(update_fields=["avatar"])

                        messages.success(
                            request, "Foto enviada e atualizada com sucesso.")
                    else:
                        messages.error(
                            request, f"Falha ao enviar a foto ({e})."
                        )

                except Exception as e:
                    messages.error(
                        request, f"Erro ao conectar com o servidor de upload: {e}"
                    )

            if form.password_changed():
                update_session_auth_hash(request, user)
                messages.success(request, "Senha alterada com sucesso.")
            else:
                messages.success(request, "Dados atualizados.")

            return redirect("logistica:settings")

        else:
            for campo, errs in form.errors.items():
                messages.error(request, f"{campo}: {errs.as_text()}")
            messages.error(request, "Corrija os erros e tente novamente.")
    else:
        form = ConfiguracaoUserForm(instance=request.user)

    return render(
        request,
        "logistica/templates_user/configuracao_user.html",
        {
            "form": form,
            "site_title": "Configurações",
            "avatar_url": perfil.avatar,
        },
    )


class UserPasswordChangeView(PasswordChangeView):
    template_name = "logistica/templates_user/password_change.html"
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
