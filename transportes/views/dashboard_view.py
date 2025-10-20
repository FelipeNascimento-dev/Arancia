from datetime import timedelta
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import now, localtime
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect
from setup.local_settings import API_BASE
from transportes.utils.utils import get_multiple_api_data

from .view_panel_technical import build_tecnicos
from .view_panel_ordens import build_ordens
from .view_cards import build_cards
@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def dashboard_view(request):

    headers = {"accept": "application/json", "access_token": "123"}
  
    hoje = localtime(now()).date() - timedelta(days=0)
    hoje_str = hoje.strftime("%Y-%m-%d")
    
    cod_base = request.session.get("COD_BASE")
    projeto = request.session.get("PROJETO")
    if not cod_base:
        return redirect(f"{reverse('transportes:config_context')}?next={request.path}")

    # --- filtros da URL ---
    filtro_unidade = request.GET.get("unidade")
    filtro_uid = request.GET.get("uid")
    filtro_flag = request.GET.get("flag")
    filtro_msg = request.GET.get("mensagem")
    ver_rota_uid = request.GET.get("ver_rota")
    search = request.GET.get("search") or ""
    ocultar_sem_nome = request.GET.get("ocultar_sem_nome") == "1"  # ?ocultar_sem_nome=1
   
    # --- buscar APIs em paralelo ---
    urls = [
        (f"status_{hoje_str}", f"{API_BASE}/v3/Filtro_status/resumo-status-detalhado/{projeto}", {"date": hoje_str}),
        (f"ordens_{hoje_str}", f"{API_BASE}/v3/consultasM/ordens-atendidas-data/{projeto}", {"date": hoje_str}),
    ]
    dados = get_multiple_api_data(urls, headers, ttl=0)
    dados_status = dados.get(f"status_{hoje_str}", {})
    resumo_geral = dados_status.get("geral", {})

    # --- técnicos ---
    tratar_uid = request.GET.get("tratar_uid")
    pessoa = request.user.username

    tecnicos, todos_tecnicos, media_fmt, top = build_tecnicos(
        dados_status,
        hoje,
        filtro_unidade=filtro_unidade,
        search=search,
        ocultar_sem_nome=ocultar_sem_nome,
        tratar_uid=tratar_uid,
        pessoa=pessoa,
    )
    # --- ordens ---
    ordens, ordens_os, skip, limit = build_ordens(request, projeto, cod_base, headers, hoje_str, tecnicos)

    # --- cards ---
    resumo_cards = build_cards(resumo_geral, ordens, ordens_os, ver_rota_uid, filtro_uid, filtro_flag, filtro_msg)
    sem_tecnico_count = len([
    o for o in ordens
    if not o.get("uid") or str(o.get("uid")).strip().lower() in ["", "none", "null", "0"]
])

    # --- unidades ---
    unidades = sorted({
        t.get("area") for t in todos_tecnicos
        if t.get("area") not in (None, "-", "None")
    })
    # --- flags ---
    filtro_ativo = bool(filtro_uid or filtro_flag or filtro_msg or request.GET.get("status_janela"))
    sem_tecnico_count = len([
        o for o in ordens
        if not o.get("uid") or str(o.get("uid")).strip().lower() in ["", "none", "null", "0"]
    ])
 
        # --- contexto ---
    context = {
        
        "geral": resumo_cards,
        "status": resumo_cards.get("status", {}),
        "tecnicos": tecnicos,
        "ordens": ordens,
        "ordens_os": ordens_os,
        "media_atraso": media_fmt,
        "top": top,
        "filtro_ativo": filtro_ativo,
        "unidades": unidades,
        "filtro_unidade": filtro_unidade,
        "filtro_uid": filtro_uid,
        "ver_rota_uid": ver_rota_uid,
        "exibir_detalhadas": bool(ver_rota_uid),
        "skip": skip,
        "limit": limit,
        "next_skip": skip + limit,
        "prev_skip": max(0, skip - limit),
        "search": search,
        "ocultar_sem_nome": ocultar_sem_nome,
        "sem_tecnico_count": sem_tecnico_count,
        "API_BASE": API_BASE, 
        "usuario_logado": request.user.username,
        "hoje": hoje,
    "show_config_link": True,
    }

    return render(request, "transportes/controle_campo/technical_panel.html", context)
