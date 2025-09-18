from django.shortcuts import render
from django.contrib import messages
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
API_ORDENAR_ROTAS = f"{API_BASE}api/v3/ordenar"
TOKEN = "123"

ORDENAR_FIELDS = [
    {"name": "uid", "label": "UID Técnico", "type": "number", "placeholder": "123", "colspan": 2},
    {"name": "os_list", "label": "Ordem de Serviço(s)", "type": "textarea", "placeholder": "Digite as OSs na sequência desejada, uma por linha", "colspan": 2},
]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def ordenar_rota_view(request):
    if request.method == "POST":
        uid = request.POST.get("uid")
        os_list = request.POST.get("os_list")

        if not uid:
            messages.error(request, " Por favor, insira um UID válido.")
        elif not os_list:
            messages.error(request, " Informe pelo menos uma OS.")
        else:
            try:
                url = f"{API_ORDENAR_ROTAS}/{uid.strip()}"

                headers = {
                    "accept": "application/json",
                    "access_token": TOKEN,
                    "Content-Type": "application/json",
                }

                # transforma textarea em lista de OS
                os_data = [o.strip() for o in os_list.splitlines() if o.strip()]

                client = RequestClient(
                    method="put",
                    url=url,
                    headers=headers,
                    request_data=os_data,
                )

                resp = client.send_api_request()

                if 'detail' not in resp:
                   
                    messages.success(request, f" OSs ordenadas com sucesso: {resp}")
                    
                else:
                    messages.error(request, f" OSs ordenadas com sucesso: {resp}")

            except Exception as e:
                messages.error(request, f"Erro inesperado: {resp} ")

    return render(request, "transportes/tools/order_route.html", {"fields": ORDENAR_FIELDS})
