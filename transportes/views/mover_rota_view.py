from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from setup.local_settings import API_BASE
from transportes.views.ver_usuario_view import API_TOKEN
from utils.request import RequestClient
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
import requests

API_MOVER = f"{API_BASE}/v3/mover"

MOVER_FIELDS = [
    {"name": "nome_tecnico", "label": "Técnico", "type": "select",
        "placeholder": "Selecione o técnico", "colspan": 1},
    {"name": "os_list", "label": "Ordem de Serviço(s)", "type": "textarea",
     "placeholder": "Digite uma OS por linha", "colspan": 2},
]


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def mover_rota_view(request):
    cod_base = request.session.get("COD_BASE")
    profile = request.session.get("PROFILE")

    if not cod_base:
        return redirect(f"{reverse('transportes:config_context')}?next={request.path}")

    API_TECNICOS = f"{API_BASE}/v3/tecnicos/buscar_tec/{cod_base}"

    tecnicos = []
    tecnico_nome = None

    # Buscar lista de técnicos
    try:
        headers = {"Accept": "application/json", "access_token": API_TOKEN}
        url_tecnicos = API_TECNICOS + \
            (f"?Profile={profile}" if profile else "")
        buscar = RequestClient(method="get", url=url_tecnicos, headers=headers)
        resp_tec = buscar.send_api_request()
        if isinstance(resp_tec, list):
            tecnicos = resp_tec
    except Exception as e:
        messages.warning(
            request, f"Não foi possível carregar técnicos: {str(e)}")

    # --- POST: mover rota ---
    if request.method == "POST":
        uid = request.POST.get("nome_tecnico")
        os_list = request.POST.get("os_list")
        uploaded_file = request.FILES.get("file_upload")

        # Se foi enviado um arquivo, ignora a seleção do técnico
        if uploaded_file:
            try:
                url = f"{API_MOVER}/excel?created_by={request.user.username}"
                headers = {"access_token": API_TOKEN}
                files = {
                    "file": (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}

                resp = requests.put(url, headers=headers, files=files)

                texto = resp.text.lower().strip()
                # aceita sucesso por código 200/201 ou texto
                if resp.status_code in [200, 201] or any(p in texto for p in ["sucesso", "movida", "processado"]):
                    messages.success(
                        request,
                        f"Arquivo '{uploaded_file.name}' enviado e processado com sucesso."
                    )
                else:
                    messages.error(
                        request,
                        f"Falha ao processar o arquivo ({resp.status_code}): {resp.text}"
                    )
            except Exception as e:
                messages.error(request, f"Erro ao enviar o arquivo: {str(e)}")

        #  Caso não tenha arquivo, exige seleção de técnico e OS
        else:
            if not uid:
                messages.error(request, "Por favor, selecione um técnico.")
            elif not os_list:
                messages.error(request, "Informe pelo menos uma OS.")
            else:
                try:
                    tec_match = next(
                        (t for t in tecnicos if str(t["uid"]) == str(uid)), None)
                    tecnico_nome = tec_match["name"] if tec_match else f"UID {uid}"

                    os_data = [o.strip()
                               for o in os_list.splitlines() if o.strip()]
                    url = f"{API_MOVER}/manual?uid={uid}&novo_tec={tecnico_nome}&created_by={request.user.username}"
                    headers_put = {
                        "Accept": "application/json",
                        "access_token": API_TOKEN,
                        "Content-Type": "application/json",
                    }

                    client = RequestClient(
                        method="put",
                        url=url,
                        headers=headers_put,
                        request_data=os_data,
                    )
                    resp = client.send_api_request()

                    # --- Tratamento aprimorado ---
                    if isinstance(resp, dict):
                        moved_success = resp.get("moved_success", 0)
                        moved_error = resp.get("moved_error", 0)

                        if moved_success > 0 and moved_error == 0:
                            messages.success(
                                request,
                                f"{moved_success} OS(s) movida(s) para {tecnico_nome} (UID {uid}) com sucesso!"
                            )
                        elif moved_success > 0 and moved_error > 0:
                            messages.warning(
                                request,
                                f"{moved_success} OS(s) movida(s), mas {moved_error} falharam: {resp}"
                            )
                        else:
                            messages.error(
                                request, f"Nenhuma OS movida: {resp}")

                    elif isinstance(resp, str):
                        texto = resp.lower().strip()
                        if any(p in texto for p in ["sucesso", "movida", "movidas", "processado"]):
                            messages.success(request, resp)
                        else:
                            messages.error(request, resp)
                    else:
                        messages.error(
                            request, f"Resposta inesperada da API: {resp}")

                except Exception as e:
                    messages.error(request, f"Erro inesperado: {str(e)}")

    return render(
        request,
        "transportes/tools/move_route.html",
        {
            "fields": MOVER_FIELDS,
            "tecnicos": tecnicos,
            "tecnico_nome": tecnico_nome,
            "created_by": request.user.username,
            "show_config_link": True,
            "current_parent_menu": "transportes",
            "current_menu": "controle_campo",
            "current_submenu": "rotas",
            "current_subsubmenu": "mover_rota"
        },
    )
