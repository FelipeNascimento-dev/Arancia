from setup.local_settings import API_BASE
from transportes.utils.utils import get_api_data

def build_ordens(request, projeto, cod_base, headers, hoje_str, tecnicos):
    url_ordens = f"{API_BASE}/v3/consultasM/ordens-atendidas-data/{projeto}"
    url_tec = f"{API_BASE}/v3/tecnicos/buscar_tec/{cod_base}?Profile={projeto}"

    skip = int(request.GET.get("skip", 0))
    limit = int(request.GET.get("limit", 20000))
    params_ordens = {"date": hoje_str, "skip": skip, "limit": limit}

    # --- técnicos ---
    dados_tecnicos = get_api_data(f"tecnicos_{cod_base}", url_tec, {}, headers)
    if not isinstance(dados_tecnicos, list):
        dados_tecnicos = []

    mapa_tecnicos = {
        str(t.get("uid", "")).strip(): (
            t.get("nome") or t.get("name") or t.get("nome_tecnico") or ""
        )
        for t in dados_tecnicos
    }

    for t in tecnicos:
        t["nome_tecnico"] = t.get("nome_tecnico") or t.get("nome") or t.get("name") or ""

    # --- ordens ---
    dados_ordens = get_api_data(f"ordens_{hoje_str}_{skip}_{limit}", url_ordens, params_ordens, headers)
    ordens = []
    if isinstance(dados_ordens, list):
        for o in dados_ordens:
            uid = str(o.get("uid") or "").strip()
            status_fmt = (o.get("status_janela") or "").replace("_", " ").upper()

            ordens.append({
                "os": o.get("os"),
                "uid": uid,
                "nome_tecnico": mapa_tecnicos.get(uid, ""),
                "alteracao_hf": o.get("alteracao_hf"),
                "tempo_restante": o.get("tempo_restante") or "",
                "cep": o.get("cep"),
                "endereco": o.get("logradouro") or "",
                "status_janela": status_fmt,
                "tag": o.get("tag"),
                "flag": o.get("flag"),
                "ocorrencia": o.get("ocorrencia"),
                "mensagem": o.get("mensagem") or "",
                "mensagem_critico": o.get("mensagem_critico", 0),
                "longitude": o.get("longitude") or "",
                "latitude": o.get("latitude") or "",
                "imageurl": o.get("imageurl") or "",
            })

    # --- filtros ---
    filtro_status = request.GET.get("status_janela")
    filtro_flag = request.GET.get("flag")
    filtro_msg = request.GET.get("mensagem")
    filtro_uid = request.GET.get("uid")

    if filtro_status and filtro_status != "total":
        filtro_status_fmt = filtro_status.replace("_", " ").upper()
        ordens = [o for o in ordens if o["status_janela"] == filtro_status_fmt or o["tag"] == filtro_status_fmt]

    if filtro_flag:
        ordens = [o for o in ordens if o.get("flag") == filtro_flag]

    if filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]:
        ordens = [o for o in ordens if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]]

    # --- filtro sem técnico ---
    if filtro_uid == "sem":
        ordens = [
            o for o in ordens
            if not o.get("uid") or str(o.get("uid")).strip().lower() in ["", "none", "null", "0"]
        ]

   
    # --- ordens detalhadas por técnico ---
    ordens_os = []
    ver_rota_uid = request.GET.get("ver_rota")
    if ver_rota_uid:
        for t in tecnicos:
            uid = str(t["uid"])
            if uid != ver_rota_uid:
                continue

            url_os_tecnico = f"{API_BASE}/v3/consultas/{cod_base}/ordens-atendidas-data/{uid}"
            dados_os_tecnico = get_api_data(f"ordens_tecnico_{uid}_{hoje_str}", url_os_tecnico, {"date": hoje_str}, headers)

            if isinstance(dados_os_tecnico, dict):
                dados_os_tecnico = [dados_os_tecnico]
            elif not isinstance(dados_os_tecnico, list):
                dados_os_tecnico = []

            for o in dados_os_tecnico:
                ordens_os.append({
                    "uid": uid,
                    "nome_tecnico": t.get("nome_tecnico") or t.get("nome"),
                    "os": o.get("os"),
                    "cep": o.get("cep"),
                    "endereco": o.get("logradouro"),
                    "numero": o.get("numero") or "",
                    "bairro": o.get("bairro"),
                    "cidade": o.get("cidade"),
                    "uf": o.get("uf"),
                    "status_janela": (o.get("status_janela") or "").replace("_", " ").upper(),
                    "tag": o.get("tag"),
                    "ocorrencia": o.get("ocorrencia"),
                    "mensagem": o.get("mensagem") or "",
                    "alteracao_hf": o.get("alteracao_hf"),
                    "tempo_restante": o.get("tempo_restante"),
                    "flag": o.get("flag"),
                    "longitude": o.get("longitude") or "",
                    "latitude": o.get("latitude") or "",
                    "imageurl": o.get("imageurl") or "",
                })

        # 🔽 aplica os mesmos filtros também ao ordens_os
        if filtro_status and filtro_status != "total":
            filtro_status_fmt = filtro_status.replace("_", " ").upper()
            ordens_os = [o for o in ordens_os if o["status_janela"] == filtro_status_fmt or o["tag"] == filtro_status_fmt]

        if filtro_flag:
            ordens_os = [o for o in ordens_os if o.get("flag") == filtro_flag]

        if filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]:
            ordens_os = [o for o in ordens_os if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]]

        if filtro_uid == "sem":
            ordens_os = [
                o for o in ordens_os
                if not o.get("uid") or str(o.get("uid")).strip().lower() in ["", "none", "null", "0"]
            ]


    return ordens, ordens_os, skip, limit
