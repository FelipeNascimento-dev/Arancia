from django.shortcuts import render
from django.contrib import messages
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect

API_ORDENAR_ROTAS = f"{API_BASE}ordenar"
API_TECNICOS = f"{API_BASE}tecnicos/buscar_tec"
TOKEN = "123"

ORDENAR_FIELDS = [
    {"name": "nome_tecnico", "label": "Técnico", "type": "select", "placeholder": "Selecione o técnico", "colspan": 2},
    {"name": "os_list", "label": "Ordem de Serviço(s)", "type": "textarea", "placeholder": "Digite as OSs na sequência desejada, uma por linha", "colspan": 2},
]
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def ordenar_rota_view(request):
    tecnicos = []
    tecnico_nome, uid = None, None

    # sempre carrega técnicos para montar o select
    try:
        headers = {"accept": "application/json", "access_token": TOKEN}
        buscar = RequestClient(method="get", url=API_TECNICOS, headers=headers)
        resp_tecnicos = buscar.send_api_request()
        if isinstance(resp_tecnicos, list):
            tecnicos = resp_tecnicos
    except Exception:
        tecnicos = []

    if request.method == "POST":
        uid = request.POST.get("nome_tecnico")
        os_list = request.POST.get("os_list")

        if not uid:
            messages.error(request, "Por favor, selecione um técnico.")
        elif not os_list:
            messages.error(request, "Informe pelo menos uma OS.")
        else:
            try:
                # busca nome do técnico pelo uid
                tecnico = next((t for t in tecnicos if str(t["uid"]) == str(uid)), None)
                tecnico_nome = tecnico["name"] if tecnico else f"UID {uid}"

                url = f"{API_ORDENAR_ROTAS}/{uid}"
                headers.update({"Content-Type": "application/json"})

                os_data = [o.strip() for o in os_list.splitlines() if o.strip()]

                client = RequestClient(
                    method="put",
                    url=url,
                    headers=headers,
                    request_data=os_data,
                )
                resp = client.send_api_request()

                if isinstance(resp, dict) and "detail" in resp:
                    messages.error(request, f"Erro ao ordenar OSs: {resp}")
                else:
                    messages.success(request, f"OSs ordenadas para {tecnico_nome} com sucesso: {resp}")

            except Exception as e:
                messages.error(request, f"Erro inesperado: {str(e)}")

    return render(
        request,
        "transportes/tools/order_route.html",
        {"fields": ORDENAR_FIELDS, "tecnicos": tecnicos, "tecnico_nome": tecnico_nome},
    )
