import requests
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now, make_aware, is_naive, localtime
from django.core.cache import cache
import json
from django.utils.safestring import mark_safe

def format_datetime(value):
    if not value:
        return "—"
    try:
        dt = parse_datetime(value)
        return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"
    except Exception:
        return "—"


def dashboard_view(request):
    headers = {"accept": "application/json", "access_token": "123"}
    hoje_str = now().strftime("%Y-%m-%d")

    # --- API de status (técnicos) com cache ---
    cache_key_status = f"status_{hoje_str}"
    dados_status = cache.get(cache_key_status)
    if not dados_status:
        url_status = "http://192.168.0.214/RetencaoAPI/api/v3/Filtro_status/resumo-status-detalhado/claro"
        resp = requests.get(url_status, params={"date": hoje_str}, headers=headers)
        dados_status = resp.json() if resp.status_code == 200 else {}
        cache.set(cache_key_status, dados_status, 60 * 5)

    resumo_por_uid = dados_status.get("por_uid", {})

    tecnicos = []
    atrasos = []
    hoje = localtime(now()).date()
    seen_uids = set()

    for uid, info in resumo_por_uid.items():
        if not uid or uid in seen_uids:
            continue
        seen_uids.add(uid)

        t = info.get("tecnico", {})
        if not t.get("uid") or not t.get("name"):
            continue

        contagem = t.get("contagem", {})
        if contagem.get("total", 0) <= 0:
            continue

        status_counts = contagem.get("status", {}) or {}

        # --- parse lastlogin ---
        lastlogin_raw = t.get("lastlogin")
        lastlogin_dt = parse_datetime(lastlogin_raw) if lastlogin_raw else None
        if lastlogin_dt and is_naive(lastlogin_dt):
            lastlogin_dt = make_aware(lastlogin_dt)

        # --- cálculo de atraso ---
        atraso_min = 0
        atraso_fmt = "—"
        abriu_hoje = False
        lastopening = parse_datetime(t.get("lastopening")) if t.get("lastopening") else None

        if lastopening:
            if is_naive(lastopening):
                lastopening = make_aware(lastopening)
            lastopening_local = localtime(lastopening)
            if lastopening_local.date() == hoje:
                abriu_hoje = True
                diff = now() - lastopening
                atraso_min = max(0, int(diff.total_seconds() // 60))
                horas, minutos = divmod(atraso_min, 60)
                atraso_fmt = f"{horas}h {minutos}min" if horas else f"{minutos}min"

        if atraso_min > 0:
            atrasos.append(atraso_min)

        tecnicos.append({
            "nome": t.get("name", "-"),
            "uid": t.get("uid"),
            "area": t.get("nome_unidade", "-"),
            "phone": t.get("phone", "-"),
            "lastlogin": format_datetime(lastlogin_raw),
            "lastlogin_dt": lastlogin_dt,
            "lastopening": format_datetime(t.get("lastopening")),
            "atraso_min": atraso_min,
            "atraso_fmt": atraso_fmt,
            "total": contagem.get("total", 0),
            "concluido": status_counts.get("concluido", 0),
            "no_tempo": status_counts.get("no_tempo", 0),
            "no_limite": status_counts.get("no_limite", 0),
            "atrasado": status_counts.get("atrasado", 0),
            "flag_azul": status_counts.get("flag_azul", 0),
            "flag_amarelo": status_counts.get("flag_amarelo", 0),
            "flag_vermelho": status_counts.get("flag_vermelho", 0),
            "critico": status_counts.get("mensagem_critico", 0),
            "abriu_hoje": abriu_hoje,
        })
    
    # --- ordenação ---
    if any(t["atraso_min"] > 29 for t in tecnicos):
        tecnicos.sort(key=lambda x: (
            -x["atraso_min"],
            not x["abriu_hoje"],
            -(x["lastlogin_dt"].timestamp() if x["lastlogin_dt"] else 0)
        ))
    else:
        tecnicos.sort(key=lambda x: (
            not x["abriu_hoje"],
            -(x["lastlogin_dt"].timestamp() if x["lastlogin_dt"] else 0),
            -x["atraso_min"]
        ))

    # --- métricas ---
    atrasos_validos = [a for a in atrasos if a > 29]
    media_atraso = int(sum(atrasos_validos) / len(atrasos_validos)) if atrasos_validos else 0
    horas, minutos = divmod(media_atraso, 60)
    media_fmt = f"{horas}h {minutos}min" if horas else f"{minutos}min"
    top = max((t for t in tecnicos if t["atraso_min"] > 29),
              key=lambda t: t["atraso_min"], default=None)

    # --- API de ordens atendidas ---
    cache_key_ordens = f"ordens_{hoje_str}"
    dados_ordens = cache.get(cache_key_ordens)
    if not dados_ordens:
        url_ordens = "http://192.168.0.214/RetencaoAPI/api/v3/consultasM/ordens-atendidas-data/claro"
        resp2 = requests.get(url_ordens, params={"date": hoje_str}, headers=headers)
        dados_ordens = resp2.json() if resp2.status_code == 200 else []
        cache.set(cache_key_ordens, dados_ordens, 60 * 5)
    mapa_tecnicos = {t["uid"]: t["nome"] for t in tecnicos}
    ordens = []
    for o in dados_ordens:
        uid = o.get("uid")
        ordens.append({
            "os": o.get("os"),
            "uid": uid,
            "nome_tecnico": mapa_tecnicos.get(uid, "-"),   # <-- aqui entra o nome
            "hf": o.get("alteracao_hf"),   
            "cep": o.get("cep"),
            "endereco": o.get("logradouro"),
            "bairro": o.get("bairro"),
            "cidade": o.get("cidade"),
            "uf": o.get("uf"),
            "status_janela": o.get("status_janela"),
            "tempo_restante": o.get("tempo_restante"),
            "tag": o.get("tag"),
            "flag": o.get("flag"),
            "critico": o.get("mensagem_critico", 0)
        })


    # --- API de ordens OS detalhadas ---
    cache_key_os = f"ordens_os_{hoje_str}"
    dados_os = cache.get(cache_key_os)
    if not dados_os:
        url_os = "http://192.168.0.214/RetencaoAPI/api/v3/consultasM/ordens-os-data/claro"
        resp3 = requests.get(url_os, params={"date": hoje_str}, headers=headers)
        dados_os = resp3.json() if resp3.status_code == 200 else []
        cache.set(cache_key_os, dados_os, 60 * 5)

    ordens_os = []
    for o in dados_os:
        ordens_os.append({
            "id": o.get("id"),
            "uid": o.get("uid"),
            "os": o.get("os"),
            "cep": o.get("cep"),
            "alteracao_hf": o.get("alteracao_hf"),
            "endereco": o.get("logradouro"),
            "numero": o.get("numero"),
            "complemento": o.get("complemento"),
            "bairro": o.get("bairro"),
            "cidade": o.get("cidade"),
            "uf": o.get("uf"),
            "flag": o.get("flag"),
            "conclusao_operador": o.get("conclusao_operador"),
            "tag": o.get("tag"),
            "mensagem": o.get("mensagem"),
            "status_janela": o.get("status_janela"),
            "tempo_restante": o.get("tempo_restante"),
        })

    context = {
        "geral": dados_status.get("geral", {}),
        "status": dados_status.get("geral", {}).get("status", {}),
        "tecnicos": mark_safe(json.dumps(tecnicos, ensure_ascii=False, default=str)),
        "ordens": mark_safe(json.dumps(ordens, ensure_ascii=False, default=str)),
        "media_atraso": media_fmt,
        "top": top,
    }
    return render(request, "transportes/controle_campo/technical_panel.html", context)
