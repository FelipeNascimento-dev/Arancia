from django.shortcuts import render
from django.contrib import messages
from setup.local_settings import API_BASE
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect

API_MOVER = f"{API_BASE}mover"
API_TECNICOS = f"{API_BASE}tecnicos/buscar_tec"
TOKEN = "123"

MOVER_FIELDS = [
    {"name": "nome_tecnico", "label": "Nome do Técnico", "type": "text", "placeholder": "Digite o nome do técnico", "colspan": 1},
    {"name": "os_list", "label": "Ordem de Serviço(s)", "type": "textarea", "placeholder": "Digite uma OS por linha", "colspan": 2},
]

@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def mover_rota_view(request):
    tecnicos = []
    tecnico_nome = None
    uid = None

    # 🔎 Buscar lista de técnicos (GET /buscar_tec)
    try:
        headers = {"accept": "application/json", "access_token": TOKEN}
        buscar = RequestClient(method="get", url=API_TECNICOS, headers=headers)
        resp_tec = buscar.send_api_request()

        if isinstance(resp_tec, list):  # lista de técnicos
            tecnicos = resp_tec
    except Exception as e:
        messages.warning(request, f"Não foi possível carregar a lista de técnicos: {str(e)}")

    if request.method == "POST":
        uid = request.POST.get("nome_tecnico")   # agora vem direto do select
        os_list = request.POST.get("os_list")

        if not uid:
            messages.error(request, "Por favor, selecione um técnico.")
        elif not os_list:
            messages.error(request, "Informe pelo menos uma OS.")
        else:
            try:
                # achar nome pelo uid
                tec_match = next((t for t in tecnicos if str(t["uid"]) == str(uid)), None)
                tecnico_nome = tec_match["name"] if tec_match else f"UID {uid}"

                # 🔄 Chamada da API de mover rota
                url = f"{API_MOVER}/{uid}"
                headers.update({"Content-Type": "application/json"})

                os_data = [o.strip() for o in os_list.splitlines() if o.strip()]

                client = RequestClient(
                    method="put",
                    url=url,
                    headers=headers,
                    request_data=os_data,
                )
                resp = client.send_api_request()

                # ✅ Tratamento da resposta
                if isinstance(resp, dict):
                    moved_success = resp.get("moved_success", 0)
                    moved_error = resp.get("moved_error", 0)

                    if moved_success > 0 and moved_error == 0:
                        messages.success(request, f"{moved_success} OS(s) movida(s) para {tecnico_nome} (UID {uid}) com sucesso!")
                    elif moved_success > 0 and moved_error > 0:
                        messages.warning(request, f"{moved_success} OS(s) movida(s), mas {moved_error} falharam: {resp}")
                    else:
                        messages.error(request, f"Nenhuma OS movida: {resp}")

                elif isinstance(resp, str):
                    if "sucesso" in resp.lower():
                        messages.success(request, f"{resp} (Técnico: {tecnico_nome} - UID {uid})")
                    else:
                        messages.error(request, resp)
                else:
                    messages.error(request, f"Resposta inesperada da API: {resp}")

            except Exception as e:
                messages.error(request, f"Erro inesperado: {str(e)}")

    return render(request, "transportes/tools/move_route.html", {
        "fields": MOVER_FIELDS,
        "tecnicos": tecnicos,
        "tecnico_nome": tecnico_nome,
    })
