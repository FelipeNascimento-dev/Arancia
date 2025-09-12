import requests
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now, make_aware, is_naive, localtime
from django.core.cache import cache

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

def dashboard_view(request):
    headers = {"accept": "application/json", "access_token": "123"}
    hoje_str = now().strftime("%Y-%m-%d")
    hoje = localtime(now()).date()

    # Resumo geral + técnicos
    url_status = "http://192.168.0.214/RetencaoAPI/api/v3/Filtro_status/resumo-status-detalhado/claro"
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
            "phone": t.get("phone"),
            "lastlogin": format_datetime(lastlogin_raw),
            "lastopening": format_datetime(t.get("lastopening")),
            "atraso_min": atraso_min,
            "atraso_fmt": atraso_fmt,
            "total": contagem.get("total", 0),
            **status_counts,
            "abriu_hoje": abriu_hoje,
        })

    # ordenação
    if any(t["atraso_min"] > 29 for t in tecnicos):
        tecnicos.sort(key=lambda x: (-x["atraso_min"], not x["abriu_hoje"]))
    else:
        tecnicos.sort(key=lambda x: (not x["abriu_hoje"], -x["atraso_min"]))

    # métricas
    atrasos_validos = [a for a in atrasos if a > 29]
    media_atraso = int(sum(atrasos_validos) / len(atrasos_validos)) if atrasos_validos else 0
    h, m = divmod(media_atraso, 60)
    media_fmt = f"{h}h {m}min" if h else f"{m}min"
    top = max((t for t in tecnicos if t["atraso_min"] > 29), key=lambda t: t["atraso_min"], default=None)

    # Ordens gerais
    url_ordens = "http://192.168.0.214/RetencaoAPI/api/v3/consultasM/ordens-atendidas-data/claro"
    dados_ordens = get_api_data(f"ordens_{hoje_str}", url_ordens, {"date": hoje_str}, headers)

    mapa_tecnicos = {t["uid"]: t["nome"] for t in tecnicos}
    ordens = [{
        "os": o.get("os"),
        "uid": o.get("uid"),
        "nome_tecnico": mapa_tecnicos.get(o.get("uid"), "-"),
        "cep": o.get("cep"),
        "endereco": o.get("logradouro"),
        "status_janela": o.get("status_janela"),
        "tag": o.get("tag"),
        "flag": o.get("flag"),
    } for o in dados_ordens if isinstance(dados_ordens, list)]

    # Ordens detalhadas por técnico
    ordens_os = []
    for t in tecnicos:
        uid = t["uid"]
        url_os_tecnico = f"http://127.0.0.1:8000/RetencaoAPI/api/v3/consultas/CTBSEQ/ordens-atendidas-data/{uid}"
        dados_os_tecnico = get_api_data(
            f"ordens_tecnico_{uid}_{hoje_str}",
            url_os_tecnico,
            {"date": hoje_str},
            headers
        )

        if not isinstance(dados_os_tecnico, list):
            continue

        for o in dados_os_tecnico:
            ordens_os.append({
                "uid": uid,
                "nome_tecnico": t["nome"],
                "os": o.get("os"),
                "cep": o.get("cep"),
                "endereco": o.get("logradouro"),
                "numero": o.get("numero"),
                "bairro": o.get("bairro"),
                "cidade": o.get("cidade"),
                "uf": o.get("uf"),
                "status_janela": o.get("status_janela"),
                "tag": o.get("tag"),
                "mensagem": o.get("mensagem"),
            })

    
    context = {
        "geral": resumo_geral,
        "status": resumo_geral.get("status", {}),
        "tecnicos": tecnicos,
        "ordens":None,
        "ordens_os": None,
        "media_atraso": media_fmt,
        "top": top,
    }
    return render(request, "transportes/controle_campo/technical_panel.html", context)
