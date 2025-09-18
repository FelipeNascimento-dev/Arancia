from django.shortcuts import render
from django.contrib import messages
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect

API_MOVER = f"{API_BASE}api/v3/mover"
TOKEN = "123"

# Configuração dinâmica dos campos
MOVER_FIELDS = [
    {"name": "uid", "label": "UID Técnico", "type": "number", "placeholder": "123", "colspan": 2},
     {"name": "os_list", "label": "Ordem de Serviço(s)", "type": "textarea", "placeholder": "Digite uma OS por linha", "colspan": 2},
]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def mover_rota_view(request):
    if request.method == "POST":
        uid = request.POST.get("uid")
        nome_unidade = request.POST.get("nome_unidade")
        os_list = request.POST.get("os_list")

        if not uid:
            messages.error(request, " Por favor, insira um UID válido.")
        elif not os_list:
            messages.error(request, " Informe pelo menos uma OS.")
        else:
            try:
                url = f"{API_MOVER}/{uid.strip()}"
                if nome_unidade:
                    url += f"?nome_unidade={nome_unidade.strip()}"

                headers = {
                    "accept": "application/json",
                    "access_token": TOKEN,
                    "Content-Type": "application/json",
                }

                os_data = [o.strip() for o in os_list.splitlines() if o.strip()]

                client = RequestClient(
                    method="put",
                    url=url,
                    headers=headers,
                    request_data=os_data,
                )

                resp = client.send_api_request()

                if 'detail' not in resp:
                    messages.success(request,f"OSs movidas com sucesso: {resp}")
                    
                else:
                    messages.error(request, f"OSs movidas com sucesso: {resp}")

            except Exception as e:
                messages.error(request, f" Erro inesperado: {resp}")

    return render(request, "transportes/tools/move_route.html", {"fields": MOVER_FIELDS})
