from django.shortcuts import render
from django.contrib import messages
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
API_BASE = "http://192.168.0.214/RetencaoAPI"
API_CRIACAO = f"{API_BASE}/api/v1/auth/create/"
TOKEN = "123"

# Campos configuráveis
USER_FIELDS = [
    {"name": "username", "label": "Usuário", "type": "text", "required": True},
    {"name": "name", "label": "Nome", "type": "text", "required": True},
    {"name": "pwd", "label": "Senha", "type": "password", "required": True},
    {"name": "pwd_confirm", "label": "Confirmar Senha", "type": "password", "required": False},
    {"name": "phone", "label": "Telefone", "type": "text", "required": False},
    {"name": "email", "label": "E-mail", "type": "email", "required": True},
    {"name": "cod_base", "label": "Código Base", "type": "text", "required": True},
    {"name": "nome_unidade", "label": "Unidade", "type": "text", "required": False},
    {"name": "documento", "label": "Documento", "type": "text", "required": True},
    {"name": "profile", "label": "Projeto", "type": "text", "required": False},
]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.CC_admin', raise_exception=True)
def criar_user_view(request):
    if request.method == "POST":
        data = {f["name"]: request.POST.get(f["name"], "").strip() for f in USER_FIELDS}

        # 1. valida se tem campos obrigatórios vazios
        missing = [f["label"] for f in USER_FIELDS if f.get("required") and not data.get(f["name"])]
        if missing:
            messages.error(request, f" Campos obrigatórios não preenchidos: {', '.join(missing)}.")
            return render(request, "transportes/tools/create_user.html", {"fields": USER_FIELDS})

        # 2. valida senha
        if data.get("pwd") != data.get("pwd_confirm"):
            messages.error(request, " As senhas não coincidem.")
            return render(request, "transportes/tools/create_user.html", {"fields": USER_FIELDS})

        # 3. envia para API
        headers = {
            "accept": "application/json",
            "access_token": TOKEN,
            "Content-Type": "application/json",
        }

        client = RequestClient(
            method="post",
            url=API_CRIACAO,
            headers=headers,
            request_data=data,
        )

        try:
            resp = client.send_api_request()
            if 'detail' not in resp:
                uid = resp.get("uid", "Não retornado")
                messages.success(request, f" Usuário criado com UID: {uid}")
            else:
                messages.error(request, " Erro inesperado ao criar usuário.")
        except Exception as e:
            messages.error(request, f" Erro na requisição: {e}")

    return render(request, "transportes/tools/create_user.html", {"fields": USER_FIELDS})
