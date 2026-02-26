from django.http import JsonResponse
import requests
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, localtime, now
from transportes.utils.utils import format_datetime, normalizar_celular
from setup.local_settings import API_BASE
from django.contrib.auth.decorators import login_required, permission_required

TRATAMENTOS = "{APIBASE}/v3/tratamento/{uid}?person_treated={pessoa}"


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def build_tecnicos(
    dados_status,
    hoje,
    filtro_unidade=None,
    search=None,
    ocultar_sem_nome: bool = False,
    tratar_uid: str | None = None,
    pessoa: str | None = None,
):
    """
    Monta a lista de técnicos com dados de login, atraso e tratamento.
    Se 'tratar_uid' for informado, faz PUT na API apenas para aquele técnico.
    """
    resumo_por_uid = dados_status.get("por_uid", {})
    tecnicos, atrasos = [], []

    for uid, info in resumo_por_uid.items():
        t = info.get("tecnico", {}) or {}
        uid_str = str(t.get("uid") or uid)
        contagem = t.get("contagem", {}) or {}
        status_counts = contagem.get("status", {}) or {}

        # --- login ---
        lastlogin_raw = t.get("lastlogin")
        lastlogin_dt = parse_datetime(lastlogin_raw) if lastlogin_raw else None
        if lastlogin_dt and is_naive(lastlogin_dt):
            lastlogin_dt = make_aware(lastlogin_dt)

        # --- atraso ---
      # --- atraso ---
        atraso_min, atraso_fmt, abriu_hoje = 0, "—", False
        lastopening = parse_datetime(
            t.get("lastopening")) if t.get("lastopening") else None

        # Total de OS e OS concluídas
        total_os = contagem.get("total", 0)
        concluidas = status_counts.get("concluido", 0)

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

        # 🚫 Se total == concluído, não marcar como atrasado
        if total_os and total_os == concluidas:
            atraso_min = 0
            atraso_fmt = "-"
        # --- TRATAR APENAS O TÉCNICO SELECIONADO ---
        if tratar_uid and pessoa and str(tratar_uid) == uid_str:
            url = TRATAMENTOS.format(
                APIBASE=API_BASE, uid=uid_str, pessoa=pessoa)
            try:
                response = requests.put(
                    url,
                    headers={"accept": "application/json",
                             "access_token": "123"},
                    timeout=5,
                )

                if response.status_code == 200:
                    print(
                        f" Técnico {uid_str} tratado com sucesso ({response.status_code})")
                else:
                    print(
                        f" Tratamento falhou p/ UID {uid_str} - status {response.status_code}")

            except requests.exceptions.Timeout:
                print(f" Timeout ao tratar técnico {uid_str}")
            except requests.exceptions.RequestException as e:
                print(f" Erro de requisição ao tratar técnico {uid_str}: {e}")

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
            "last_treatment": format_datetime(t.get("last_treatment")) or "-",
            "quantity_treatments_day": t.get("quantity_treatments_day") or "-",
            "person_treated": t.get("person_treated") or "-",
            "quantity_treatments": t.get("quantity_treatments") or "-",
        })

    # --- filtros visuais ---
    tecnicos = [t for t in tecnicos if t["area"].lower() != "teste"]
    todos_tecnicos = tecnicos.copy()

    if ocultar_sem_nome:
        tecnicos = [
            t for t in tecnicos if not t["nome"].startswith("Técnico ")]
    if filtro_unidade:
        tecnicos = [t for t in tecnicos if t["area"] not in (
            None, "-", "None") and t["area"] == filtro_unidade]
    if search:
        search = search.lower()
        tecnicos = [t for t in tecnicos if search in t.get(
            "nome", "").lower() or search in str(t.get("uid", "")).lower()]

    # --- ordenação e métricas ---
    if any(t["atraso_min"] > 29 for t in tecnicos):
        tecnicos.sort(key=lambda x: (-x["atraso_min"], not x["abriu_hoje"]))
    else:
        tecnicos.sort(key=lambda x: (not x["abriu_hoje"], -x["atraso_min"]))

    atrasos_validos = [a for a in atrasos if a > 29]
    media_atraso = int(sum(atrasos_validos) /
                       len(atrasos_validos)) if atrasos_validos else 0
    h, m = divmod(media_atraso, 60)
    media_fmt = f"{h}h {m}min" if h else f"{m}min"
    top = max((t for t in tecnicos if t["atraso_min"] > 29),
              key=lambda t: t["atraso_min"], default=None)

    return tecnicos, todos_tecnicos, media_fmt, top

# transportes/views/view_tratamento.py


@login_required(login_url='logistica:login')
@permission_required('logistica.acesso_arancia', raise_exception=True)
def registrar_tratamento_view(request, uid):
    pessoa = request.user.username
    url = f"{API_BASE}/v3/tratamento/{uid}?person_treated={pessoa}"

    try:
        r = requests.put(
            url, headers={"accept": "application/json", "access_token": "123"}, timeout=5)
        return JsonResponse({"status": r.status_code, "ok": r.ok})
    except Exception as e:
        return JsonResponse({"status": 500, "detail": str(e)}, status=500)
