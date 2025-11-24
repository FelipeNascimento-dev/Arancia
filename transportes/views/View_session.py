# views/config_view.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

PROJECTS_BY_BASE = {
    
    "CTBSEQ": ["CTBPO", "CIELO","CLARO","CTB Transportes"],
    "CTBFED": ["FIRST", "CTB", "C6-BANK", "PICPAY"],
}

PROFILE_OPTIONS = ["CLARO", "CIELO", "FEDEX", "CTB","CTB Transportes"]


@login_required
def config_context_view(request):
    # 1) pega de GET ou POST
    next_url = request.GET.get("next") or request.POST.get("next")

    # 2) se não veio, tenta recuperar da sessão
    if not next_url:
        next_url = request.session.get("NEXT_URL")

    if request.method == "POST":
        cod_base = request.POST.get("cod_base")
        projeto = request.POST.get("projeto")
        profile = request.POST.get("profile")

        # salva na sessão
        request.session["COD_BASE"] = cod_base
        request.session["PROJETO"] = projeto
        request.session["PROFILE"] = profile

        # também salva o next_url para usos futuros
        request.session["NEXT_URL"] = next_url

        # redireciona para quem chamou
        if not next_url:
            return redirect("/arancia/")  # fallback fixo
        return redirect(next_url)

    # --- GET ---
    cod_base = request.session.get("COD_BASE", "")
    projeto = request.session.get("PROJETO", "")
    profile = request.session.get("PROFILE", "")
    projetos_disponiveis = PROJECTS_BY_BASE.get(cod_base, [])

    return render(
        request,
        "transportes/tools/filtro_api.html",
        {
            "cod_base": cod_base,
            "projeto": projeto,
            "projetos_disponiveis": projetos_disponiveis,
            "profile": profile,
            "profile_options": PROFILE_OPTIONS,
            "next_url": next_url,  # vai para o form hidden
        },
    )
