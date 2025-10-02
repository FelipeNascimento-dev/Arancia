from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, localtime, now
from transportes.utils.utils import format_datetime, normalizar_celular

def build_tecnicos(
    dados_status,
    hoje,
    filtro_unidade=None,
    search=None,
    ocultar_sem_nome: bool = False,   # <-- novo parâmetro
):
    resumo_por_uid = dados_status.get("por_uid", {})
    tecnicos, atrasos = [], []

    for uid, info in resumo_por_uid.items():
        t = info.get("tecnico", {})

        # se não tiver "uid" dentro, usa a chave do dict
        uid_str = str(t.get("uid") or uid)

        contagem = t.get("contagem", {}) or {}
        status_counts = contagem.get("status", {})

        # --- login ---
        lastlogin_raw = t.get("lastlogin")
        lastlogin_dt = parse_datetime(lastlogin_raw) if lastlogin_raw else None
        if lastlogin_dt and is_naive(lastlogin_dt):
            lastlogin_dt = make_aware(lastlogin_dt)

        # --- atraso ---
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

        # --- append final ---
        tecnicos.append({
            "nome": t.get("name") or f"Técnico {uid_str}",
            "uid": uid_str,
            "area": t.get("nome_unidade") or "-",
            "phone": normalizar_celular(t.get("phone")),
            "lastlogin": format_datetime(lastlogin_raw),
            "lastopening": format_datetime(t.get("lastopening")),
            "atraso_min": atraso_min,
            "atraso_fmt": atraso_fmt,
            "total": contagem.get("total", 0),
            **status_counts,
            "abriu_hoje": abriu_hoje,
        })

    # remove unidade "teste"
    tecnicos = [t for t in tecnicos if t["area"].lower() != "teste"]
    todos_tecnicos = tecnicos.copy()

    # --- filtro para ocultar sem nome ---
    if ocultar_sem_nome:
        tecnicos = [t for t in tecnicos if not t["nome"].startswith("Técnico ")]

    # filtro por unidade
    if filtro_unidade:
        tecnicos = [
            t for t in tecnicos
            if t["area"] not in (None, "-", "None") and t["area"] == filtro_unidade
        ]
    # filtro por nome ou uid
    if search:
        search = search.lower()
        tecnicos = [
            t for t in tecnicos
            if search in t.get("nome", "").lower() or search in str(t.get("uid", "")).lower()
        ]


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

    return tecnicos, todos_tecnicos, media_fmt, top
