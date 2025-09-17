import re
import requests
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now, make_aware, is_naive, localtime
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_protect


def format_datetime(value):
    if not value:
        return "—"
    try:
        dt = parse_datetime(value)
        return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"
    except Exception:
        return "—"


def get_api_data(cache_key, url, params, headers, ttl=300):
    """Busca dados de API com cache"""
    data = cache.get(cache_key)
    if not data:
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json() if resp.status_code == 200 else {}
        cache.set(cache_key, data, ttl)
    return data


def normalizar_celular(numero: str) -> str:
    """Remove () + - e espaços, mantém apenas DDD + número"""
    if not numero:
        return ""
    numero = re.sub(r"\D", "", numero)  # mantém só dígitos
    if numero.startswith("55") and len(numero) > 11:
        numero = numero[2:]  # remove código do país
    return numero


@csrf_protect
@login_required(login_url='logistica:login')
@permission_required('transportes.controle_campo', raise_exception=True)
def dashboard_view(request):
    headers = {"accept": "application/json", "access_token": "123"}
    hoje_str = now().strftime("%Y-%m-%d")
    hoje = localtime(now()).date()

    # --- filtros recebidos da URL ---
    filtro_status = request.GET.get("status_janela")
    filtro_flag = request.GET.get("flag")
    filtro_msg = request.GET.get("mensagem")
    filtro_unidade = request.GET.get("unidade")
    filtro_uid = request.GET.get("uid")
    # --- Resumo geral + técnicos ---
    url_status = "http://192.168.0.216/RetencaoAPI/api/v3/Filtro_status/resumo-status-detalhado/claro"
    dados_status = get_api_data(f"status_{hoje_str}", url_status, {"date": hoje_str}, headers)

    resumo_geral = dados_status.get("geral", {})
    resumo_por_uid = dados_status.get("por_uid", {})
    
    tecnicos, atrasos = [], []
    for uid, info in resumo_por_uid.items():
        t = info.get("tecnico", {})
        if not t.get("uid"):
            continue

        contagem = t.get("contagem", {}) or {}
        status_counts = contagem.get("status", {})

        # login
        lastlogin_raw = t.get("lastlogin")
        lastlogin_dt = parse_datetime(lastlogin_raw) if lastlogin_raw else None
        if lastlogin_dt and is_naive(lastlogin_dt):
            lastlogin_dt = make_aware(lastlogin_dt)

        # atraso
        atraso_min, atraso_fmt, abriu_hoje = 0, "—", False
        lastopening = parse_datetime(t.get("lastopening")) if t.get("lastopening") else None
        if lastopening:
            if is_naive(lastopening):
                lastopening = make_aware(lastopening)
            if localtime(lastopening).date() == hoje:
                abriu_hoje = True
                diff = now() - lastopening
                atraso_min = max(0, int(diff.total_seconds() // 60))
                horas, minutos = divmod(atraso_min, 60)
                atraso_fmt = f"{horas}h {minutos}min" if horas else f"{minutos}min"
                atrasos.append(atraso_min)

        tecnicos.append({
            "nome": t.get("name"),
            "uid": t.get("uid"),
            "area": t.get("nome_unidade"),
            "phone": normalizar_celular(t.get("phone")),
            "lastlogin": format_datetime(lastlogin_raw),
            "lastopening": format_datetime(t.get("lastopening")),
            "atraso_min": atraso_min,
            "atraso_fmt": atraso_fmt,
            "total": contagem.get("total", 0),
            **status_counts,
            "abriu_hoje": abriu_hoje,
        })

    # --- cópia antes do filtro de unidade ---
    todos_tecnicos = tecnicos.copy()

        # --- aplicar filtro de unidade (só técnicos) ---
    if filtro_unidade:
        tecnicos = [t for t in tecnicos if t["area"] == filtro_unidade]
   

    # --- ordenação técnicos ---
    if any(t["atraso_min"] > 29 for t in tecnicos):
        tecnicos.sort(key=lambda x: (-x["atraso_min"], not x["abriu_hoje"]))
    else:
        tecnicos.sort(key=lambda x: (not x["abriu_hoje"], -x["atraso_min"]))

    # --- métricas ---
    atrasos_validos = [a for a in atrasos if a > 29]
    media_atraso = int(sum(atrasos_validos) / len(atrasos_validos)) if atrasos_validos else 0
    h, m = divmod(media_atraso, 60)
    media_fmt = f"{h}h {m}min" if h else f"{m}min"
    top = max((t for t in tecnicos if t["atraso_min"] > 29), key=lambda t: t["atraso_min"], default=None)

    # --- Ordens gerais ---
    url_ordens = "http://192.168.0.216/RetencaoAPI/api/v3/consultasM/ordens-atendidas-data/claro"
    dados_ordens = get_api_data(f"ordens_{hoje_str}", url_ordens, {"date": hoje_str}, headers)

    mapa_tecnicos = {t["uid"]: t["nome"] for t in tecnicos}
    ordens = []
  
    if isinstance(dados_ordens, list):
        for o in dados_ordens:
            item = {
                "os": o.get("os"),
                "uid": o.get("uid"),
                "nome_tecnico": mapa_tecnicos.get(o.get("uid"), "-"),
                "alteracao_hf": o.get("alteracao_hf"),
                "tempo_restante": o.get ("tempo_restante") or "-",
                "cep": o.get("cep"),
                "endereco": o.get("logradouro") or "",
                "status_janela": o.get("status_janela"),
                "tag": o.get("tag"),
                "flag": o.get("flag"),
                "mensagem": o.get("mensagem") or "",
                "mensagem_critico": o.get("mensagem_critico", 0),
            }
            ordens.append(item)

    # --- aplicar filtros nas ordens ---
    if filtro_status and filtro_status != "total":
        ordens = [o for o in ordens if o["status_janela"] == filtro_status or o["tag"] == filtro_status]

    if filtro_flag:
        ordens = [o for o in ordens if o["flag"] == filtro_flag]

    if filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]:
        ordens = [o for o in ordens if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]]
 
    sem_tecnico_count = len([o for o in ordens if o.get("uid") in (0, None)])

    if filtro_uid == "sem":
        # pega ordens sem técnico: uid == 0 ou uid é None
        ordens = [o for o in ordens if not o.get("uid")]  # 0, None ou vazio
   
       # --- Ordens detalhadas por técnico ---
    ordens_os = []
    ver_rota_uid = request.GET.get("ver_rota")
    exibir_detalhadas = ver_rota_uid is not None

    if ver_rota_uid:
        for t in tecnicos:
            uid = str(t["uid"])
            if uid != ver_rota_uid:
                continue

            url_os_tecnico = f"http://192.168.0.216/RetencaoAPI/api/v3/consultas/CTBSEQ/ordens-atendidas-data/{uid}"
            dados_os_tecnico = get_api_data(
                f"ordens_tecnico_{uid}_{hoje_str}",
                url_os_tecnico,
                {"date": hoje_str},
                headers
            )

            print("Consultando ordens detalhadas:", uid, hoje_str, url_os_tecnico)
            print("Qtd ordens retornadas:", len(dados_os_tecnico) if isinstance(dados_os_tecnico, list) else "não é lista")

            # força lista mesmo se vier dict único
            if isinstance(dados_os_tecnico, dict):
                dados_os_tecnico = [dados_os_tecnico]
            elif not isinstance(dados_os_tecnico, list):
                dados_os_tecnico = []

            for o in dados_os_tecnico:
                ordens_os.append({
                    "uid": uid,
                    "nome_tecnico": t["nome"],
                    "os": o.get("os"),
                    "cep": o.get("cep"),
                    "endereco": o.get("logradouro"),
                    "numero": o.get("numero") or "",
                    "bairro": o.get("bairro"),
                    "cidade": o.get("cidade"),
                    "uf": o.get("uf"),
                    "status_janela": o.get("status_janela"),
                    "tag": o.get("tag"),
                    "mensagem": o.get("mensagem") or "",
                    "alteracao_hf": o.get("alteracao_hf"),
                    "tempo_restante": o.get("tempo_restante"),
                    "flag": o.get("flag"),
                })
    
    # --- decide se há filtro ativo ---
    filtro_ativo = bool(filtro_status or filtro_flag or filtro_msg or filtro_uid)
    filtro_unidade = request.GET.get("unidade") or None
    if filtro_status and filtro_status != "total":
        ordens_os = [
            o for o in ordens_os
            if o["status_janela"] == filtro_status or o["tag"] == filtro_status
        ]

    if filtro_flag:
        ordens_os = [o for o in ordens_os if o.get("flag") == filtro_flag]

    if filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]:
        ordens_os = [
            o for o in ordens_os
            if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]
        ]
    # --- cards de status ---
        # decide se pega geral ou técnico
   
    # --- decide de onde vem os números para os cards ---
    # --- decide de onde vem os números para os cards ---
    if ordens_os:  # ordens detalhadas de técnico
        resumo_cards = {
            "total": len(ordens_os),
            "status": {
                "concluido": sum(1 for o in ordens_os if o["status_janela"] == "concluido"),
                "no_tempo": sum(1 for o in ordens_os if o["status_janela"] == "no_tempo"),
                "no_limite": sum(1 for o in ordens_os if o["status_janela"] == "no_limite"),
                "atrasado": sum(1 for o in ordens_os if o["status_janela"] == "atrasado"),
                "flag_azul": sum(1 for o in ordens_os if o.get("flag") == "AZUL"),
                "flag_vermelho": sum(1 for o in ordens_os if o.get("flag") == "VERMELHO"),
                "mensagem_critico": sum(1 for o in ordens_os if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]),
            },
        }
    elif filtro_uid == "sem":  # quando for "Sem Técnico"
        resumo_cards = {
            "total": len(ordens),
            "status": {
                "concluido": sum(1 for o in ordens if o["status_janela"] == "concluido"),
                "no_tempo": sum(1 for o in ordens if o["status_janela"] == "no_tempo"),
                "no_limite": sum(1 for o in ordens if o["status_janela"] == "no_limite"),
                "atrasado": sum(1 for o in ordens if o["status_janela"] == "atrasado"),
                "flag_azul": sum(1 for o in ordens if o.get("flag") == "AZUL"),
                "flag_vermelho": sum(1 for o in ordens if o.get("flag") == "VERMELHO"),
                "mensagem_critico": sum(1 for o in ordens if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]),
            },
        }
    else:
        resumo_cards = resumo_geral

    base_ordens = ordens_os if ordens_os else ordens

    if base_ordens:  # sempre recalcula com base no que sobrou após filtros
        resumo_cards = {
            "total": len(base_ordens),
            "status": {
                "concluido": sum(1 for o in base_ordens if o["status_janela"] == "concluido"),
                "no_tempo": sum(1 for o in base_ordens if o["status_janela"] == "no_tempo"),
                "no_limite": sum(1 for o in base_ordens if o["status_janela"] == "no_limite"),
                "atrasado": sum(1 for o in base_ordens if o["status_janela"] == "atrasado"),
                "flag_azul": sum(1 for o in base_ordens if o.get("flag") == "AZUL"),
                "flag_vermelho": sum(1 for o in base_ordens if o.get("flag") == "VERMELHO"),
                "mensagem_critico": sum(
                    1 for o in base_ordens if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]
                ),
            },
        }
    else:
        resumo_cards = resumo_geral
        # --- cards de status ---
    status_cards = [
        {"key": "total", "label": "Total", "icon": "fa-clipboard", "border": "border-black", "color": "black", "value": resumo_cards.get("total", 0)},
        {"key": "concluido", "label": "Concluído", "icon": "fa-circle-check", "border": "border-blue1", "color": "blue1", "value": resumo_cards.get("status", {}).get("concluido", 0)},
        {"key": "no_tempo", "label": "No Tempo", "icon": "fa-thumbs-up", "border": "border-green1", "color": "green1", "value": resumo_cards.get("status", {}).get("no_tempo", 0)},
        {"key": "no_limite", "label": "No Limite", "icon": "fa-hourglass-half", "border": "border-orange", "color": "orange", "value": resumo_cards.get("status", {}).get("no_limite", 0)},
        {"key": "atrasado", "label": "Atrasado", "icon": "fa-hourglass-end", "border": "border-redore", "color": "redore", "value": resumo_cards.get("status", {}).get("atrasado", 0)},
    ]

    flag_cards = [
        {"param": "AZUL", "query": "flag", "label": "Casos Azuis", "color": "blue", "value": resumo_cards.get("status", {}).get("flag_azul", 0)},
        {"param": "VERMELHO", "query": "flag", "label": "Casos Vermelhos", "color": "red", "value": resumo_cards.get("status", {}).get("flag_vermelho", 0)},
        {"param": "CRÍTICO", "query": "mensagem", "label": "Casos Críticos", "color": "green", "value": resumo_cards.get("status", {}).get("mensagem_critico", 0)},
    ]


    # --- unidades para os filtros ---
    unidades = sorted({t.get("area") for t in todos_tecnicos if t.get("area")})

    context = {
    "geral": resumo_cards,  # agora usa o mesmo base
    "status": resumo_cards.get("status", {}),
    "tecnicos": tecnicos,
    "ordens": ordens,
    "ordens_os": ordens_os,
    "media_atraso": media_fmt,
    "top": top,
    "filtro_ativo": filtro_ativo,
    "status_cards": status_cards,
    "flag_cards": flag_cards,
    "ver_rota_uid": ver_rota_uid,
    "exibir_detalhadas": exibir_detalhadas,
    "unidades": unidades,
    "filtro_unidade": filtro_unidade,
    "filtro_uid": filtro_uid,
    "sem_tecnico_count": sem_tecnico_count,
}

    return render(request, "transportes/controle_campo/technical_panel.html", context)
