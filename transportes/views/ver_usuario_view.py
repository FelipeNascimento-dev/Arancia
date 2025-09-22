import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from setup.local_settings import API_BASE

# Endpoints
API_LIST_TEC = f"{API_BASE}/tecnicos/buscar_tec"  # lista todos
API_GET_TEC = f"{API_BASE}/update"                # busca individual
API_PUT_TEC = f"{API_BASE}/update/tec"            # atualiza
API_TOKEN = "123"  # ideal mover para settings.py

@login_required
def ver_usuario_view(request):
    # carrega lista de técnicos
    resp = requests.get(
        API_LIST_TEC,
        headers={"access_token": API_TOKEN},
    )
    tecnicos = resp.json() if resp.status_code == 200 else []

    # garante que todos os campos existam
    for tec in tecnicos:
        tec.setdefault("username", "")
        tec.setdefault("phone", "")
        tec.setdefault("email", "")
        tec.setdefault("nome_unidade", "")
        tec.setdefault("documento", "")
        tec.setdefault("profile", "")
        tec.setdefault("status", "")

    context = {
        "tecnicos": tecnicos,
        "api_list_tec": API_LIST_TEC,  # lista
        "api_get_tec": API_GET_TEC,    # GET individual
        "api_put_tec": API_PUT_TEC,    # PUT update
        "api_token": API_TOKEN,
    }
    return render(request, "transportes/tools/see_user.html", context)
