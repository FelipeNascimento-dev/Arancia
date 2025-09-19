import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

API_BASE = "http://192.168.0.214/RetencaoAPI/api/v3"
API_TOKEN = "123"  # ideal mover para settings.py

@login_required
def ver_usuario_view(request):
    # Buscar lista inicial de técnicos
    resp = requests.get(f"{API_BASE}/tecnicos/buscar_tec", headers={"access_token": API_TOKEN})
    tecnicos = resp.json() if resp.status_code == 200 else []

    context = {
        "tecnicos": tecnicos,
        "api_base": API_BASE,
        "api_token": API_TOKEN,
    }
    return render(request, "transportes/tools/see_user.html", context)
