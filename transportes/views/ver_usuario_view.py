import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from setup.local_settings import API_BASE

API_TOKEN = "123"

@login_required
def ver_usuario_view(request):
    search = request.GET.get("search", "").lower()
    page_number = request.GET.get("page", 1)

    cod_base = request.session.get("COD_BASE")
    projeto = request.session.get("PROJETO")
    profile = request.session.get("PROFILE")

    # se não tiver contexto definido → manda para config
    if not cod_base:
        return redirect(f"{reverse('transportes:config_context')}?next={request.path}")


    API_LIST_TEC = f"{API_BASE}tecnico/{cod_base}/buscar"
    API_PUT_TEC = f"{API_BASE}tecnico/update/"

    # --- Atualização de técnico ---
    if request.method == "POST" and "uid" in request.POST:
        uid = request.POST.get("uid")
        payload = {
            "username": request.POST.get("username"),
            "name": request.POST.get("name"),
            "phone": request.POST.get("phone"),
            "email": request.POST.get("email"),
            "nome_unidade": request.POST.get("nome_unidade"),
            "documento": request.POST.get("documento"),
            "profile": request.POST.get("profile"),
            "status": request.POST.get("status"),
        }
        payload = {k: v for k, v in payload.items() if v}  # remove campos vazios

        try:
            resp = requests.put(
                f"{API_PUT_TEC}{uid}",
                headers={
                    "Authorization": f"Bearer {API_TOKEN}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=5,
            )
            if resp.status_code in (200, 201):
                messages.success(request, "Técnico atualizado com sucesso!")
            else:
                messages.error(request, f"Erro ao atualizar técnico ({resp.status_code}) → {resp.text}")
        except Exception as e:
            messages.error(request, f"Falha ao comunicar API: {e}")
        return redirect("transportes:ver_usuario")

    # --- Listagem de técnicos ---
    params = {}
    if profile:  # só adiciona se houver profile configurado
        params["Profile"] = profile

    try:
        resp = requests.get(
            API_LIST_TEC,
            params=params,
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            timeout=5,
        )
        tecnicos = resp.json() if resp.status_code == 200 else []
    except Exception:
        tecnicos = []

    # Normaliza campos
    for tec in tecnicos:
        for field in ["uid", "username", "name", "phone", "email", "nome_unidade", "documento", "profile", "status"]:
            tec[field] = tec.get(field) or ""

    # Filtro por pesquisa
    if search:
        tecnicos = [
            t for t in tecnicos
            if search in t.get("name", "").lower()
            or search in t.get("nome_unidade", "").lower()
        ]

    paginator = Paginator(tecnicos, 15)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "transportes/tools/see_user.html",
        {
            "page_obj": page_obj,
            "search": search,
            "cod_base": cod_base,
            "projeto": projeto,
            "profile": profile,
        },
    )
