from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from setup.local_settings import API_BASE
from utils.request import RequestClient
from transportes.forms.form_create_user import UsuarioForm
from logistica.models import GroupAditionalInformation

API_CRIACAO = f"{API_BASE}/v1/auth/create/"
TOKEN = "123"


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.CC_admin', raise_exception=True)
@permission_required('logistica.acesso_arancia', raise_exception=True)
def criar_user_view(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            unidade = data["nome_unidade"]
            data["user_created_id"] = request.user.id
            data["gai_id"] = unidade.id
            data["nome_unidade"] = f"PA_{unidade.cod_iata}"

            headers = {
                "accept": "application/json",
                "access_token": TOKEN,
                "Content-Type": "application/json",
            }

            try:
                client = RequestClient(
                    method="post",
                    url=API_CRIACAO,
                    headers=headers,
                    request_data=data,
                )
                resp = client.send_api_request()

                if resp and "detail" not in resp:
                    uid = resp.get("uid", "Não retornado")
                    messages.success(request, f"Usuário criado com UID: {uid}")
                else:
                    detail = resp.get("detail", "Erro desconhecido")

                    if isinstance(detail, list):
                        erros = []
                        for err in detail:
                            loc = " → ".join(map(str, err.get("loc", [])))
                            msg = err.get("msg", "Erro de validação")
                            erros.append(f"{loc}: {msg}")
                        detail = "; ".join(erros)

                    messages.error(request, f"Erro ao criar usuário: {detail}")

            except Exception as e:
                messages.error(request, f"Erro na requisição: {e}")
    else:
        form = UsuarioForm()

    return render(request, "transportes/tools/create_user.html", {
        "form": form,
        "current_parent_menu": "transportes",
        "current_menu": "controle_campo",
        "current_submenu": "usuarios",
        "current_subsubmenu": "criar_usuario",
    })
