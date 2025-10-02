def filtrar_ordens(ordens, filtro_status, filtro_flag, filtro_msg, filtro_uid):
    if filtro_status and filtro_status != "total":
        ordens = [o for o in ordens if o["status_janela"] == filtro_status or o["tag"] == filtro_status]

    if filtro_flag:
        ordens = [o for o in ordens if o.get("flag") == filtro_flag]

    if filtro_msg and filtro_msg.upper() in ["CRITICO", "CRÍTICO"]:
        ordens = [o for o in ordens if (o.get("mensagem") or "").upper() in ["CRITICO", "CRÍTICO"]]

    if filtro_uid == "sem":
        ordens = [o for o in ordens if not o.get("uid")]  # pega sem técnico

    return ordens


def filtrar_tecnicos(tecnicos, filtro_unidade):
    if filtro_unidade:
        tecnicos = [t for t in tecnicos if t["area"] == filtro_unidade]
    return tecnicos
