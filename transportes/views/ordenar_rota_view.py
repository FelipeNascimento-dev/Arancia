# views/ordenar_rota_view.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from setup.local_settings import API_BASE
from transportes.views.ver_usuario_view import API_TOKEN
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect

API_ORDENAR_ROTAS = f"{API_BASE}ordenar"

ORDENAR_FIELDS = [
    {"name": "nome_tecnico", "label": "Técnico", "type": "select", "placeholder": "Selecione o técnico", "colspan": 2},
    {"name": "os_list", "label": "Ordem de Serviço(s)", "type": "textarea", "placeholder": "Digite as OSs na sequência desejada, uma por linha", "colspan": 2},
]


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def ordenar_rota_view(request):
    cod_base = request.session.get("COD_BASE")
    profile = request.session.get("PROFILE")

    # Se não tiver contexto -> redireciona para config
    if not cod_base:
        return redirect(f"{reverse('transportes:config_context')}?next={request.path}")

    API_TECNICOS = f"{API_BASE}tecnicos/buscar_tec/{cod_base}"

    tecnicos = []
    tecnico_nome = None

    # 🔹 Buscar lista de técnicos
    try:
        headers = {
            "Accept": "application/json",
            "access_token": API_TOKEN
        }

        url_tecnicos = API_TECNICOS
        if profile:
            url_tecnicos += f"?Profile={profile}"

        buscar = RequestClient(
            method="get",
            url=url_tecnicos,
            headers=headers
        )
        resp_tecnicos = buscar.send_api_request()

        if isinstance(resp_tecnicos, list):
            tecnicos = resp_tecnicos
    except Exception as e:
        messages.warning(request, f"Não foi possível carregar técnicos: {str(e)}")

    # --- POST: ordenar rota ---
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
                headers_put = {
                    "Accept": "application/json",
                    "access_token": API_TOKEN,
                    "Content-Type": "application/json",
                }

                os_data = [o.strip() for o in os_list.splitlines() if o.strip()]

                client = RequestClient(
                    method="put",
                    url=url,
                    headers=headers_put,
                    request_data=os_data,
                )
                resp = client.send_api_request()

                #  Tratamento da resposta
                if isinstance(resp, dict) and "detail" in resp:
                    messages.error(request, f"Erro ao ordenar OSs: {resp.get('detail')}")
                elif isinstance(resp, dict):
                    messages.success(request, f"OSs ordenadas para {tecnico_nome}: {resp}")
                elif isinstance(resp, str):
                    messages.success(request, f"{resp} (Técnico: {tecnico_nome})")
                else:
                    messages.warning(request, f"Resposta inesperada da API: {resp}")

            except Exception as e:
                messages.error(request, f"Erro inesperado: {str(e)}")

    return render(
        request,
        "transportes/tools/order_route.html",
        {"fields": ORDENAR_FIELDS, "tecnicos": tecnicos, "tecnico_nome": tecnico_nome},
    )
